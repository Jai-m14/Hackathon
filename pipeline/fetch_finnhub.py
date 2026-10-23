"""Fetch Finnhub data for each startup's best valid public comparable.

Reads the LLM-generated matches (3 ranked tickers per Company_ID, where
Company_ID is the startup's name), picks the best-ranked ticker with a Finnhub
profile and enough annual financials, and fetches free-tier Finnhub data for it.
Startup details from the portfolio output are joined in by Company_ID.
Every response is cached to cache/finnhub/{TICKER}/{endpoint}.json so the demo
can run fully offline from the cache.

Usage:
    py finnhub_fetch.py --input venturelens_matches.csv
    py finnhub_fetch.py --input sample_matches.csv --limit 2
    py finnhub_fetch.py --input venturelens_matches.csv --offline   # cache only
    py finnhub_fetch.py --input venturelens_matches.csv --refresh   # ignore cache
"""

import argparse
import json
import math
import os
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

CACHE_DIR = Path("cache/finnhub")
OUTPUT_JSON = "venturelens_comparable_data.json"
OUTPUT_CSV = "venturelens_comparables_summary.csv"
PORTFOLIO_CSV = "venturelens_portfolio_output.csv"

# Portfolio output columns joined into the JSON "startup" object
PORTFOLIO_TEXT_FIELDS = ["Description", "Categories", "Headquarters (City)",
                         "Headquarters (Country)", "Website"]
PORTFOLIO_NUMBER_FIELDS = ["Year Founded", "Total_Raised_USD_Millions",
                           "Risk_Adjusted_Score", "Weight", "Allocation_USD"]

MIN_CALL_INTERVAL = 1.1  # seconds; free tier is ~60 calls/min
MAX_RETRIES = 3
NEWS_DAYS = 90
FINANCIAL_YEARS = 5
MIN_REVENUE_PERIODS = 2  # annual periods with revenue a ticker needs to be "valid"

PROFILE_FIELDS = ["name", "finnhubIndustry", "country", "exchange", "ipo",
                  "marketCapitalization", "weburl"]
NEWS_FIELDS = ["headline", "source", "datetime", "url", "summary"]

# Summary CSV column -> Basic Financials metric key (verified against cached CRM response)
METRIC_COLUMNS = {
    "revenue_growth_ttm_yoy": "revenueGrowthTTMYoy",
    "revenue_growth_5y": "revenueGrowth5Y",
    "gross_margin_ttm": "grossMarginTTM",
    "net_margin_ttm": "netProfitMarginTTM",
    "ps_ttm": "psTTM",
    "beta": "beta",
    "return_52w": "52WeekPriceReturnDaily",
}

# XBRL concepts (without the "us-gaap_" prefix), in order of preference
REVENUE_CONCEPTS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueServicesNet",
]
NET_INCOME_CONCEPTS = [
    "NetIncomeLoss",
    "ProfitLoss",
    "NetIncomeLossAvailableToCommonStockholdersBasic",
]

SUMMARY_COLUMNS = [
    "Company_ID", "startup_description", "status", "status_reason", "chosen_rank",
    "ticker", "company_name", "display_name", "industry",
    "country", "ipo", "market_cap_usd_m", *METRIC_COLUMNS.keys(),
    "llm_confidence", "news_count_90d", "fetched_at",
]


class FinnhubFetcher:
    """Throttled, cached, retrying wrapper around the Finnhub client."""

    def __init__(self, refresh=False, offline=False):
        self.refresh = refresh
        self.offline = offline
        self._client = None
        self._api_key = None
        self._last_call = 0.0
        self.network_calls = 0

    def _get_client(self):
        if self._client is None:
            import finnhub  # imported lazily so a fully cached run needs no key

            load_dotenv()
            self._api_key = os.getenv("FINNHUB_KEY")
            if not self._api_key:
                raise RuntimeError("FINNHUB_KEY is not set in .env")
            self._client = finnhub.Client(api_key=self._api_key)
        return self._client

    def _redact(self, text):
        # Request errors can include the full URL, which carries the token
        text = str(text)
        if self._api_key:
            text = text.replace(self._api_key, "***")
        return re.sub(r"token=[^&\s'\"]+", "token=***", text)

    def _throttle(self):
        wait = MIN_CALL_INTERVAL - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def _call_api(self, path, params):
        import finnhub

        client = self._get_client()
        for attempt in range(MAX_RETRIES + 1):
            self._throttle()
            self.network_calls += 1
            try:
                return client._get(path, params=params)
            except finnhub.FinnhubAPIException as e:
                if e.status_code == 429 and attempt < MAX_RETRIES:
                    backoff = 5 * 2 ** attempt
                    print(f"    429 rate limited on {path}; retrying in {backoff}s")
                    time.sleep(backoff)
                    continue
                raise

    def get(self, ticker, endpoint, path, params):
        """Return (data, error). Uses cache unless --refresh; never raises."""
        # Keep odd tickers (e.g. "RDS/A") from escaping or breaking the cache path
        cache_file = CACHE_DIR / re.sub(r"[^A-Za-z0-9.\-]", "_", ticker) / f"{endpoint}.json"
        if cache_file.exists() and not self.refresh:
            with open(cache_file, encoding="utf-8") as f:
                return json.load(f)["data"], None
        if self.offline:
            return None, "not cached (offline mode)"

        try:
            data = self._call_api(path, params)
        except Exception as e:
            return None, self._redact(e)

        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"fetched_at": utc_now(), "params": params, "data": data}, f)
        return data, None


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def display_name(name):
    """Strip trailing bracketed suffixes, e.g. 'Datadog Inc (Pre-Reincorporation)'."""
    if not name:
        return None
    return re.sub(r"(\s*[\(\[][^\(\)\[\]]*[\)\]])+\s*$", "", name).strip() or name


def clean_text(value):
    """Return a stripped string, or None for empty/missing values."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    value = str(value).strip()
    return value or None


def clean_number(value):
    """Return a float, or None for missing/non-numeric values (never 0)."""
    if value is None or isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(value) or math.isinf(value) else value


def statement_items(statement):
    """Normalise a report section to {concept_without_prefix: value}.

    The live API returns a list of {concept, label, unit, value}; the docs show
    a plain dict. Handle both.
    """
    items = {}
    if isinstance(statement, dict):
        pairs = statement.items()
    elif isinstance(statement, list):
        pairs = ((row.get("concept", ""), row.get("value")) for row in statement
                 if isinstance(row, dict))
    else:
        return items
    for concept, value in pairs:
        name = concept.split("_", 1)[1] if "_" in concept else concept
        items.setdefault(name, value)
    return items


def pick_concept(items, concepts):
    for concept in concepts:
        value = clean_number(items.get(concept))
        if value is not None:
            return value, concept
    return None, None


def reported_cutoff():
    return f"{date.today().year - FINANCIAL_YEARS - 1}-01-01"


def fetch_reported(fetcher, ticker):
    return fetcher.get(ticker, "financials_reported", "/stock/financials-reported",
                       {"symbol": ticker, "freq": "annual", "from": reported_cutoff()})


def recent_filings(reported):
    """Annual filings newest first, dropping periods before the cutoff.

    Finnhub's `from` filter is not reliable: FIG returns Fortress Investment
    Group's 2012-13 filings (a previous holder of the symbol), so filter here.
    """
    cutoff = reported_cutoff()
    filings = [f for f in (reported or {}).get("data") or []
               if (f.get("endDate") or "")[:10] >= cutoff]
    return sorted(filings, key=lambda f: f.get("endDate") or "", reverse=True)


def extract_annual_financials(reported):
    """Turn Financials As Reported into [{year, revenue, net_income, ...}]."""
    rows = []
    seen_periods = set()
    for filing in recent_filings(reported):
        # Finnhub's "year" is a fiscal label (CRM's FY ending Jan 2026 is 2025 and
        # can collide with the prior filing), so key rows on the period end date.
        end_date = (filing.get("endDate") or "")[:10]
        if end_date in seen_periods:  # e.g. a 10-K/A restating the same period
            continue
        seen_periods.add(end_date)
        report = filing.get("report") or {}
        ic = statement_items(report.get("ic"))
        revenue, revenue_concept = pick_concept(ic, REVENUE_CONCEPTS)
        net_income, ni_concept = pick_concept(ic, NET_INCOME_CONCEPTS)
        if net_income is None:
            net_income, ni_concept = pick_concept(statement_items(report.get("cf")),
                                                  NET_INCOME_CONCEPTS)
        rows.append({
            "year": int(end_date[:4]) if end_date[:4].isdigit() else filing.get("year"),
            "fiscal_year": filing.get("year"),
            "end_date": end_date or None,
            "form": filing.get("form"),
            "revenue": revenue,
            "net_income": net_income,
            "revenue_concept": revenue_concept,
            "net_income_concept": ni_concept,
        })
    return rows[:FINANCIAL_YEARS]


def fetch_comparable(fetcher, ticker, reported, reported_err):
    """Fetch the remaining free endpoints for a chosen ticker.

    Financials As Reported was already fetched during validation and is passed in.
    """
    errors = {}
    today = date.today()
    if reported_err:
        errors["financials_reported"] = reported_err

    def get(endpoint, path, params):
        data, err = fetcher.get(ticker, endpoint, path, params)
        if err:
            errors[endpoint] = err
            print(f"    {endpoint}: ERROR {err}")
        return data

    peers = get("peers", "/stock/peers", {"symbol": ticker, "grouping": "industry"})
    basic = get("basic_financials", "/stock/metric", {"symbol": ticker, "metric": "all"})
    earnings = get("earnings", "/stock/earnings", {"symbol": ticker})
    recs = get("recommendations", "/stock/recommendation", {"symbol": ticker})
    news = get("news", "/company-news",
               {"symbol": ticker,
                "from": (today - timedelta(days=NEWS_DAYS)).isoformat(),
                "to": today.isoformat()})

    basic = basic or {}
    return {
        "peers": [p for p in (peers or []) if p != ticker],
        "metrics": basic.get("metric") or {},
        "metric_series_annual": (basic.get("series") or {}).get("annual") or {},
        "financials_annual": extract_annual_financials(reported),
        "financials_reported_raw": recent_filings(reported)[:FINANCIAL_YEARS],
        "earnings": earnings or [],
        "recommendations": recs or [],
        "news": [{k: item.get(k) for k in NEWS_FIELDS} for item in (news or [])],
        "fetch_errors": errors,
    }


def load_portfolio(path):
    """Return {Company_ID: {portfolio fields}} from the portfolio output, or {}."""
    if not Path(path).exists():
        print(f"Warning: {path} not found; startup portfolio fields will be empty")
        return {}
    # Read as text so names like "NA" or "None" are not turned into NaN
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    portfolio = {}
    for _, row in df.iterrows():
        fields = {k: clean_text(row.get(k)) for k in PORTFOLIO_TEXT_FIELDS}
        fields.update({k: clean_number(row.get(k)) for k in PORTFOLIO_NUMBER_FIELDS})
        if fields["Year Founded"] is not None:
            fields["Year Founded"] = int(fields["Year Founded"])
        portfolio[clean_text(row["Company_ID"])] = fields
    return portfolio


def startup_info(company_id, matches, portfolio):
    first = matches.iloc[0]
    info = {
        "Company_ID": company_id,
        "Domain": clean_text(first.get("Domain")),
        "Country": clean_text(first.get("Country")),
        "Funding_Stage": clean_text(first.get("Funding_Stage")),
        "startup_description": clean_text(first.get("startup_description")),
        "in_portfolio": company_id in portfolio,
    }
    info.update(portfolio.get(company_id)
                or dict.fromkeys(PORTFOLIO_TEXT_FIELDS + PORTFOLIO_NUMBER_FIELDS))
    return info


def process_company(fetcher, company_id, matches, startup):
    """Choose the best-ranked valid ticker and fetch its data.

    Valid = non-empty profile2 AND at least MIN_REVENUE_PERIODS annual periods
    with revenue. If no ticker is valid, fall back to the best-ranked ticker that
    has a profile, with status ok_partial / status_reason limited_financials.
    """
    matches = matches.sort_values("rank")
    result = {
        "Company_ID": company_id,
        "startup": startup,
        "status": "no_valid_match",
        "status_reason": None,
        "chosen_rank": None,
        "ticker": None,
        "display_name": None,
        "failed_tickers": [],
        "llm_match": None,
        "profile": None,
    }

    chosen = None
    fallback = None  # best-ranked ticker with a profile but too little history
    for _, match in matches.iterrows():
        rank = int(match["rank"])
        ticker = str(match["ticker"]).strip().upper()
        if not ticker or ticker == "NAN":
            result["failed_tickers"].append({"rank": rank, "ticker": None, "reason": "empty ticker"})
            continue
        if re.search(r"\s", ticker):  # e.g. Stockholm "TRUE B"; not a Finnhub US symbol
            print(f"  rank {rank} {ticker}: invalid (unsupported_ticker_format)")
            result["failed_tickers"].append(
                {"rank": rank, "ticker": ticker, "reason": "unsupported_ticker_format"})
            continue

        profile, err = fetcher.get(ticker, "profile2", "/stock/profile2", {"symbol": ticker})
        if err or not profile:
            reason = (f"profile2 error: {err}" if err
                      else "profile2 returned empty profile (ticker not found)")
            print(f"  rank {rank} {ticker}: invalid ({reason})")
            result["failed_tickers"].append({"rank": rank, "ticker": ticker, "reason": reason})
            continue

        reported, reported_err = fetch_reported(fetcher, ticker)
        candidate = (match, ticker, profile, reported, reported_err)
        periods = sum(r["revenue"] is not None for r in extract_annual_financials(reported))
        if periods >= MIN_REVENUE_PERIODS:
            print(f"  rank {rank} {ticker}: valid ({periods} annual periods with revenue)")
            chosen = candidate
            break

        reason = (f"limited_financials: {periods} annual period(s) with revenue, "
                  f"need {MIN_REVENUE_PERIODS}")
        if reported_err:
            reason += f" (financials_reported error: {reported_err})"
        print(f"  rank {rank} {ticker}: skipped ({reason})")
        result["failed_tickers"].append({"rank": rank, "ticker": ticker, "reason": reason})
        if fallback is None:
            fallback = candidate

    status_reasons = []
    if chosen is None and fallback is not None:
        chosen = fallback
        status_reasons.append("limited_financials")
        # The fallback ends up used, so it is no longer a skipped ticker
        result["failed_tickers"] = [f for f in result["failed_tickers"]
                                    if f["ticker"] != fallback[1]]
        print(f"  no ticker passed; falling back to {fallback[1]} (limited_financials)")

    if chosen is None:
        print("  no valid match")
    else:
        match, ticker, profile, reported, reported_err = chosen
        result.update({
            "chosen_rank": int(match["rank"]),
            "ticker": ticker,
            "display_name": display_name(profile.get("name")),
            "llm_match": {
                "company_name": clean_text(match.get("company_name")),
                "exchange": clean_text(match.get("exchange")),
                "rationale": clean_text(match.get("similarity_rationale")),
                "similarities": clean_text(match.get("key_similarities")),
                "differences": clean_text(match.get("key_differences")),
                "confidence": clean_number(match.get("confidence")),
                "model": clean_text(match.get("model")),
                "generated_at": clean_text(match.get("generated_at")),
            },
            "profile": {k: profile.get(k) for k in PROFILE_FIELDS},
        })
        result.update(fetch_comparable(fetcher, ticker, reported, reported_err))
        if result["fetch_errors"]:
            status_reasons.append("fetch_errors")
        result["status"] = "ok_partial" if status_reasons else "ok"
        result["status_reason"] = "; ".join(status_reasons) or None

    result["fetched_at"] = utc_now()
    return result


def summary_row(r):
    profile = r.get("profile") or {}
    metrics = r.get("metrics") or {}
    row = {
        "Company_ID": r["Company_ID"],
        "startup_description": r["startup"]["startup_description"],
        "status": r["status"],
        "status_reason": r.get("status_reason"),
        "chosen_rank": r["chosen_rank"],
        "ticker": r["ticker"],
        "company_name": profile.get("name"),
        "display_name": r.get("display_name"),
        "industry": profile.get("finnhubIndustry"),
        "country": profile.get("country"),
        "ipo": profile.get("ipo"),
        "market_cap_usd_m": clean_number(profile.get("marketCapitalization")),
        "llm_confidence": (r.get("llm_match") or {}).get("confidence"),
        "news_count_90d": len(r["news"]) if r["status"] != "no_valid_match" else None,
        "fetched_at": r["fetched_at"],
    }
    for col, key in METRIC_COLUMNS.items():
        row[col] = clean_number(metrics.get(key))
    return row


def to_json_safe(obj):
    """Replace NaN/inf (from pandas) with None so the JSON stays valid."""
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_json_safe(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if hasattr(obj, "item"):  # numpy scalars
        return to_json_safe(obj.item())
    return obj


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default="venturelens_matches.csv")
    parser.add_argument("--limit", type=int, help="only process the first N startups")
    parser.add_argument("--refresh", action="store_true", help="ignore the cache")
    parser.add_argument("--offline", action="store_true",
                        help="never call the API; use cached responses only")
    parser.add_argument("--portfolio", default=PORTFOLIO_CSV,
                        help="portfolio output to join startup details from")
    parser.add_argument("--output-json", default=OUTPUT_JSON)
    parser.add_argument("--output-csv", default=OUTPUT_CSV)
    args = parser.parse_args()
    # Startup names may contain characters the Windows console cannot print
    sys.stdout.reconfigure(errors="replace")

    # Company_ID is a free-text startup name: read as text so names like "NA"
    # are kept, and strip stray whitespace so the portfolio join still matches
    matches = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    matches["Company_ID"] = matches["Company_ID"].str.strip()
    matches["rank"] = pd.to_numeric(matches["rank"], errors="coerce")
    matches = matches[(matches["Company_ID"] != "") & matches["rank"].notna()]
    company_ids = list(dict.fromkeys(matches["Company_ID"]))  # keep input order
    if args.limit:
        company_ids = company_ids[:args.limit]

    portfolio = load_portfolio(args.portfolio)
    fetcher = FinnhubFetcher(refresh=args.refresh, offline=args.offline)
    results = []
    for i, company_id in enumerate(company_ids, 1):
        print(f"[{i}/{len(company_ids)}] {company_id}")
        group = matches[matches["Company_ID"] == company_id]
        startup = startup_info(company_id, group, portfolio)
        results.append(process_company(fetcher, company_id, group, startup))

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(to_json_safe(results), f, indent=2, ensure_ascii=False)
    pd.DataFrame([summary_row(r) for r in results], columns=SUMMARY_COLUMNS) \
        .to_csv(args.output_csv, index=False)

    counts = pd.Series([r["status"] for r in results]).value_counts().to_dict()
    print(f"\nDone: {len(results)} startups {counts}, {fetcher.network_calls} API calls")
    print(f"Wrote {args.output_json} and {args.output_csv}")


if __name__ == "__main__":
    main()
