"""VentureLens: match each selected startup to 3 publicly listed comparables via an LLM.

Run:
    python llm_matching.py --input venturelens_portfolio_output.csv --limit 2

The LLM only proposes comparable tickers and explains why; it never changes
scores or weights. Raw responses are cached in cache/llm_matching/ so re-runs
(and the live demo) are reproducible and work offline. Use --refresh to ignore it.

Output (fixed contract, long format, 3 rows per startup): venturelens_matches.csv
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import pandas as pd
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    AzureOpenAI,
    BadRequestError,
    InternalServerError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

DEFAULT_INPUT = "venturelens_portfolio_output.csv"
DEFAULT_OUTPUT = "venturelens_matches.csv"
CACHE_DIR = os.path.join(HERE, "cache", "llm_matching")
DEFAULT_MODEL = "gpt-4o"
DEFAULT_AZURE_API_VERSION = "2024-10-21"

# Startup fields sent to the LLM, as (input column, JSON key). Scores, weights, allocation,
# founders, investor names, logos, addresses and profile URLs are deliberately excluded.
STARTUP_FIELDS = [
    ("Company_ID", "startup_name"),
    ("Description", "Description"),
    ("Categories", "Categories"),
    ("Domain", "Domain"),
    ("Funding_Stage", "Funding_Stage"),
    ("Status", "Status"),
    ("Year Founded", "Year Founded"),
    ("Y Combinator Year", "Y Combinator Year"),
    ("Headquarters (City)", "Headquarters (City)"),
    ("Headquarters (US State)", "Headquarters (US State)"),
    ("Headquarters (Country)", "Headquarters (Country)"),
    ("Website", "Website"),
    ("Total_Raised_USD_Millions", "Total_Raised_USD_Millions"),
    ("Investor_Count", "Investor_Count"),
    ("Tier1_Investor_Count", "Tier1_Investor_Count"),
]
INT_FIELDS = {"Year Founded", "Y Combinator Year", "Investor_Count", "Tier1_Investor_Count"}

OUTPUT_COLUMNS = [
    "Company_ID", "Domain", "Country", "Funding_Stage", "rank", "ticker", "company_name",
    "exchange", "similarity_rationale", "key_similarities", "key_differences",
    "confidence", "model", "generated_at", "startup_description",
]

SYSTEM_PROMPT = """You are a financial analyst matching private startups to publicly listed comparable companies.
Given one startup's characteristics as JSON, return the 3 most similar publicly listed companies, most similar first.
Rules:
- Match primarily on WHAT THE COMPANY DOES, from Description and Categories; then business model and customer type (consumer vs business); then stage, scale (total raised) and geography.
- The Description is the most reliable field. If the name and the Description disagree (e.g. a name that doesn't match the product described), go by the Description.
- If you recognise the startup, you may use general knowledge of its product to judge similarity, but do not invent financial figures. The rationale must mainly cite the Description and Categories.
- Never return the startup itself, or a company that acquired it, as a comparable.
- Confidence must reflect how much of the comparable's CORE business matches the startup. If the match is only one product line or segment of a larger company (e.g. a budgeting app inside a mortgage lender), confidence must be 0.6 or lower, and you should prefer companies whose main business matches (pure-plays).
- Among similarly good matches, prefer companies listed on US exchanges (NYSE/NASDAQ) for at least 3 years that file annual reports with the SEC (10-K or 20-F). Similarity comes first: do not drop a clearly better match for this.
- Use only real, currently listed companies with their correct primary ticker. If you are not confident a ticker is correct, lower the confidence; do not invent tickers.
- similarity_rationale must say in plain words what both companies do, e.g. "Both run search engines for electronic component pricing...".
Return JSON only, in this exact shape:
{"matches": [{"rank": 1, "ticker": "XXXX", "company_name": "...", "exchange": "NASDAQ", "similarity_rationale": "1-2 sentences", "key_similarities": ["..."], "key_differences": ["..."], "confidence": 0.0}]}
confidence is between 0 and 1."""

INVALID_RETRIES = 2      # extra attempts when the response fails validation
TRANSIENT_RETRIES = 5    # attempts on rate-limit / network errors, with exponential backoff


def startup_payload(row: pd.Series, columns: list[str]) -> dict:
    """Only this startup's characteristics, with NaNs dropped and counts as ints."""
    payload = {}
    for col, key in STARTUP_FIELDS:
        if col not in columns:
            continue
        value = row[col]
        if value is None or (isinstance(value, float) and math.isnan(value)):
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        if hasattr(value, "item"):  # numpy scalar -> python
            value = value.item()
        if col in INT_FIELDS and isinstance(value, float) and value.is_integer():
            value = int(value)
        payload[key] = value
    return payload


def validate(content: str) -> list[dict]:
    """Parse and validate the LLM response; raise ValueError if it breaks the contract."""
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"not valid JSON: {exc}") from exc
    matches = data.get("matches") if isinstance(data, dict) else None
    if not isinstance(matches, list) or len(matches) != 3:
        raise ValueError("expected exactly 3 matches")

    cleaned = []
    for m in matches:
        if not isinstance(m, dict):
            raise ValueError("match is not an object")
        ticker = str(m.get("ticker") or "").strip().upper()
        if not ticker:
            raise ValueError("empty ticker")
        try:
            rank = int(m.get("rank"))
            confidence = float(m.get("confidence"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"bad rank/confidence: {exc}") from exc
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence out of range: {confidence}")
        cleaned.append({
            "rank": rank,
            "ticker": ticker,
            "company_name": str(m.get("company_name") or "").strip(),
            "exchange": str(m.get("exchange") or "").strip(),
            "similarity_rationale": str(m.get("similarity_rationale") or "").strip(),
            "key_similarities": [str(s).strip() for s in m.get("key_similarities") or []],
            "key_differences": [str(s).strip() for s in m.get("key_differences") or []],
            "confidence": confidence,
        })
    if sorted(m["rank"] for m in cleaned) != [1, 2, 3]:
        raise ValueError("ranks must be 1, 2, 3")
    return sorted(cleaned, key=lambda m: m["rank"])


class Matcher:
    def __init__(self, model: str):
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("No API key: set LLM_API_KEY (or OPENAI_API_KEY) in .env")
        base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None
        # Retries are handled here so backoff and logging are explicit.
        if base_url and "azure" in urlparse(base_url).netloc.lower():
            # Azure routes by deployment (= model) and needs an api-version.
            self.client = AzureOpenAI(api_key=api_key, azure_endpoint=base_url,
                                      api_version=os.getenv("LLM_API_VERSION", DEFAULT_AZURE_API_VERSION),
                                      max_retries=0, timeout=120)
        else:
            self.client = OpenAI(api_key=api_key, base_url=base_url, max_retries=0, timeout=120)
        self.model = model
        self.json_mode = True
        self.fixed_temperature = True

    def _complete(self, startup: dict) -> str:
        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(startup)},
            ],
        }
        for attempt in range(TRANSIENT_RETRIES):
            try:
                if self.json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                else:
                    kwargs.pop("response_format", None)
                if self.fixed_temperature:
                    kwargs["temperature"] = 0
                else:
                    kwargs.pop("temperature", None)
                resp = self.client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content or ""
            except BadRequestError as exc:
                if self.fixed_temperature and "temperature" in str(exc):
                    # Some reasoning models only allow the default; the cache keeps re-runs reproducible.
                    print("    [!] temperature=0 not supported by this model; using its default")
                    self.fixed_temperature = False
                    continue
                if self.json_mode and "response_format" in str(exc):
                    print("    [!] response_format not supported; retrying without JSON mode")
                    self.json_mode = False
                    continue
                raise
            except (RateLimitError, APIConnectionError, APITimeoutError, InternalServerError) as exc:
                if attempt == TRANSIENT_RETRIES - 1:
                    raise
                wait = 2 ** attempt
                print(f"    [!] {type(exc).__name__}; retrying in {wait}s")
                time.sleep(wait)
        raise RuntimeError("unreachable")

    def match(self, startup: dict) -> tuple[str, list[dict]]:
        """Return (raw content, validated matches), retrying invalid responses."""
        last_error = None
        for attempt in range(1 + INVALID_RETRIES):
            content = self._complete(startup)
            try:
                return content, validate(content)
            except ValueError as exc:
                last_error = exc
                print(f"    [!] invalid response (attempt {attempt + 1}): {exc}")
        raise ValueError(f"invalid after {1 + INVALID_RETRIES} attempts: {last_error}")


def cache_path(company_id: str) -> str:
    # Company_ID is a real startup name, so keep the filename filesystem-safe.
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", company_id).strip("._") or "unnamed"
    return os.path.join(CACHE_DIR, f"{safe}.json")


def load_cached(company_id: str) -> dict | None:
    path = cache_path(company_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            entry = json.load(f)
        entry["matches"] = validate(entry["raw_response"])
        return entry
    except (OSError, KeyError, ValueError) as exc:
        print(f"    [!] ignoring unusable cache {path}: {exc}")
        return None


def save_cache(company_id: str, entry: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path(company_id), "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Match selected startups to 3 public comparables via an LLM.")
    parser.add_argument("-i", "--input", default=DEFAULT_INPUT, help=f"Input CSV (default: {DEFAULT_INPUT})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help=f"Output CSV (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--model", default=None, help=f"Model id (default: $LLM_MODEL or {DEFAULT_MODEL})")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N companies")
    parser.add_argument("--refresh", action="store_true", help="Ignore cached responses and call the LLM again")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise SystemExit(f"Input CSV not found: {args.input} (pass --input)")
    model = args.model or os.getenv("LLM_MODEL") or DEFAULT_MODEL

    df = pd.read_csv(args.input)
    print(f"Loaded {args.input}: {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    if "Company_ID" not in df.columns:
        raise SystemExit("Input has no Company_ID column")
    missing = [c for c, _ in STARTUP_FIELDS if c not in df.columns]
    if missing:
        print(f"Note: fields not in input (not sent to LLM): {missing}")

    ids = df["Company_ID"].astype("string").str.strip()
    df = df[ids.notna() & (ids != "") & (ids.str.upper() != "CASH")].copy()
    df["Company_ID"] = df["Company_ID"].astype(str).str.strip()
    if args.limit is not None:
        df = df.head(args.limit)
    print(f"Matching {len(df)} startups with model {model}\n")

    matcher = None  # created lazily so fully cached runs work offline without a key
    rows, failures = [], []
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        company_id = row["Company_ID"]
        startup = startup_payload(row, list(df.columns))
        print(f"[{i}/{len(df)}] {company_id} ({startup.get('Domain', '?')}, "
              f"{startup.get('Headquarters (Country)', '?')})")

        entry = None if args.refresh else load_cached(company_id)
        if entry is not None:
            print("    cached")
        else:
            try:
                matcher = matcher or Matcher(model)
                raw, matches = matcher.match(startup)
            except (AuthenticationError, PermissionDeniedError) as exc:
                # Provider error text can echo part of the key, so don't print it.
                raise SystemExit(f"LLM auth failed ({type(exc).__name__}, HTTP {exc.status_code}); "
                                 "check LLM_API_KEY / LLM_BASE_URL in .env")
            except Exception as exc:  # log and move on to the next startup
                print(f"    [x] failed: {type(exc).__name__}: {exc}")
                failures.append(company_id)
                continue
            entry = {
                "company_id": company_id,
                "model": model,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "request": startup,
                "raw_response": raw,
            }
            save_cache(company_id, entry)
            entry["matches"] = matches

        for m in entry["matches"]:
            rows.append({
                "Company_ID": company_id,
                "Domain": startup.get("Domain", ""),
                "Country": startup.get("Headquarters (Country)", ""),
                "Funding_Stage": startup.get("Funding_Stage", ""),
                **m,
                "key_similarities": " | ".join(m["key_similarities"]),
                "key_differences": " | ".join(m["key_differences"]),
                "model": entry["model"],
                "generated_at": entry["generated_at"],
                "startup_description": startup.get("Description", ""),
            })
            print(f"    {m['rank']}. {m['ticker']:<6} {m['company_name']} ({m['exchange']}) conf={m['confidence']:.2f}")

    out = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    out.to_csv(args.output, index=False, encoding="utf-8")
    print(f"\nSaved {len(out)} rows for {len(out) // 3} startups to {args.output}")
    if failures:
        print(f"Failed ({len(failures)}): {failures}")
        sys.exit(1)


if __name__ == "__main__":
    main()
