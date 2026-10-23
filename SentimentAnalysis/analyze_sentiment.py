#!/usr/bin/env python3
"""
analyze_sentiment.py
--------------------
Performs dual-entity sentiment and reputation analysis on startups and their founders
using live media (Google News RSS), tech community discussions (Hacker News), and
the UO OpenAI Portal (GPT-6 Astra / Azure OpenAI).

Dual Intelligence:
1. Company Sentiment: Brand recognition, traction, news coverage, market risks.
2. Founder Sentiment: Leadership credibility, track record, public perception, executive reputation.
3. Synthesized Score: Weighted investment sentiment combining both company and founding team.

Data Sources:
- Startups.csv (Kaggle dataset with Company, Categories, Founders, Location, Description)
- Founders.csv (Kaggle dataset mapping Founder, Company, Gender)
- Fallback support for any CSV with company and founder columns.

AI Gateway:
- UO OpenAI Portal: https://app-uoaihack2ix6ak.azurewebsites.net
- Model: gpt-6-astra (Azure OpenAI gateway)
- Local Fallback: NLTK VADER with financial and startup domain lexicon.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

import pandas as pd
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    # Check current directory, script directory, and parent directory
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    load_dotenv(os.path.join(os.getcwd(), ".env"))
except ImportError:
    pass

# Try importing NLTK VADER as guaranteed local fallback
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)
    sia = SentimentIntensityAnalyzer()
    
    # Financial and founder domain lexicon additions
    FINANCIAL_FOUNDER_LEXICON = {
        "soars": 2.4, "surges": 2.4, "beats": 2.0, "outperforms": 2.6,
        "breakthrough": 2.5, "profitable": 2.4, "profitability": 2.2,
        "windfall": 2.2, "tailwind": 1.8, "unicorn": 2.5, "visionary": 2.8,
        "innovative": 2.2, "acclaimed": 2.4, "serial entrepreneur": 2.0,
        "plummet": -2.6, "plunges": -2.6, "slashes": -2.2, "layoffs": -2.8,
        "downsizing": -2.0, "lawsuit": -2.5, "fraud": -3.5, "scandal": -3.2,
        "ousted": -3.0, "resigns": -2.0, "controversy": -2.4, "antitrust": -2.4,
        "breach": -2.6, "hack": -2.5, "headwind": -1.8, "bankrupt": -3.2,
    }
    sia.lexicon.update(FINANCIAL_FOUNDER_LEXICON)
except Exception:
    sia = None

# Configuration Constants
DEFAULT_UO_ENDPOINT = "https://app-uoaihack2ix6ak.azurewebsites.net"
DEFAULT_ASTRA_MODEL = "gpt-6-astra"
DEFAULT_AZURE_API_VERSION = "2024-02-15-preview"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

LLM_AUTH_FAILED = False


def clean_query_term(term: str) -> str:
    """Cleans legal suffixes and brackets for clean search query terms."""
    clean = re.sub(r"\(.*?\)", "", str(term))
    clean = re.sub(
        r"\b(Inc|Corp|LLC|Ltd|Co|Corporation|Technologies|Tech)\b\.?",
        "",
        clean,
        flags=re.IGNORECASE,
    )
    return clean.strip() or str(term).strip()


def parse_founders_list(founders_val) -> list[str]:
    """Parses a comma- or semicolon-delimited list of founders into clean individual names."""
    if not founders_val or pd.isna(founders_val):
        return []
    raw = str(founders_val)
    parts = re.split(r"[,;/|]|\band\b", raw)
    cleaned = []
    for p in parts:
        name = p.strip()
        if name and len(name) > 1 and name.lower() not in ("none", "n/a", "unknown", "nan"):
            cleaned.append(name)
    return cleaned


def build_founder_lookup(founders_csv_path: str = None) -> dict[str, list[str]]:
    """
    Builds a case-insensitive company -> list of founders mapping from Founders.csv.
    """
    candidates = [
        founders_csv_path,
        "Founders.csv",
        os.path.join(os.path.dirname(__file__), "Founders.csv"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "Founders.csv"),
    ]
    target_path = None
    for c in candidates:
        if c and os.path.exists(c):
            target_path = c
            break

    lookup = {}
    if not target_path:
        return lookup

    try:
        fdf = pd.read_csv(target_path)
        # Expect columns: Founder, Company
        comp_col = next((c for c in fdf.columns if "comp" in c.lower()), "Company")
        fnd_col = next((c for c in fdf.columns if "found" in c.lower() or "person" in c.lower()), "Founder")

        for _, row in fdf.iterrows():
            comp = str(row[comp_col]).strip() if pd.notna(row.get(comp_col)) else ""
            fnd = str(row[fnd_col]).strip() if pd.notna(row.get(fnd_col)) else ""
            if comp and fnd and fnd.lower() not in ("nan", "none"):
                key = comp.lower()
                if key not in lookup:
                    lookup[key] = []
                if fnd not in lookup[key]:
                    lookup[key].append(fnd)
    except Exception as e:
        print(f"[!] Note: Could not parse Founders.csv ({e})")

    # Also index founders from Startups.csv if available
    for s_path in [
        "Startups.csv",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "Startups.csv"),
        os.path.join(os.path.dirname(__file__), "Startups.csv"),
    ]:
        if os.path.exists(s_path):
            try:
                sdf = pd.read_csv(s_path)
                s_comp = next((c for c in sdf.columns if "comp" in c.lower()), None)
                s_fnd = next((c for c in sdf.columns if "found" in c.lower()), None)
                if s_comp and s_fnd:
                    for _, row in sdf.iterrows():
                        c_name = str(row[s_comp]).strip() if pd.notna(row.get(s_comp)) else ""
                        c_key = c_name.lower()
                        if c_key and (c_key not in lookup or not lookup[c_key]):
                            f_list = parse_founders_list(row.get(s_fnd))
                            if f_list:
                                lookup[c_key] = f_list
            except Exception:
                pass
            break

    return lookup


def fetch_google_news(query: str, fallback_queries: list[str] = None, max_items: int = 10) -> list[dict]:
    """Fetches recent news articles from Google News RSS with query fallbacks."""
    queries_to_try = [query] + (fallback_queries or [])
    articles = []
    seen_titles = set()

    for q in queries_to_try:
        clean_q = clean_query_term(q)
        encoded = urllib.parse.quote(clean_q)
        for url in [
            f"https://news.google.com/rss/search?q={encoded}+when:90d&hl=en-US&gl=US&ceid=US:en",
            f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en",
        ]:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=8)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    for item in root.findall(".//item"):
                        title = item.findtext("title", default="").strip()
                        pub_date = item.findtext("pubDate", default="").strip()
                        source = item.findtext("source", default="").strip()
                        if title and title not in seen_titles:
                            seen_titles.add(title)
                            articles.append({
                                "title": title,
                                "source": source or "News Media",
                                "pub_date": pub_date,
                                "type": "media",
                            })
                            if len(articles) >= max_items:
                                return articles
            except Exception:
                pass
            if len(articles) >= 2:
                break
        if len(articles) >= 2:
            break

    return articles


def fetch_hacker_news(query: str, fallback_queries: list[str] = None, max_items: int = 8) -> list[dict]:
    """Fetches community tech discussions from Hacker News via the official Algolia API."""
    queries_to_try = [query] + (fallback_queries or [])
    posts = []
    seen_titles = set()

    for q in queries_to_try:
        clean_q = clean_query_term(q)
        encoded = urllib.parse.quote(clean_q)
        url = f"https://hn.algolia.com/api/v1/search?query={encoded}&tags=story&hitsPerPage={max_items}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for hit in data.get("hits", []):
                    title = hit.get("title")
                    points = hit.get("points", 0)
                    num_comments = hit.get("num_comments", 0)
                    created_at = hit.get("created_at", "")
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        posts.append({
                            "title": title,
                            "source": f"Hacker News ({points} pts, {num_comments} comments)",
                            "pub_date": created_at,
                            "type": "social",
                        })
                        if len(posts) >= max_items:
                            return posts
        except Exception:
            pass
        if len(posts) >= 2:
            break

    return posts


def parse_llm_json(raw_text: str) -> dict:
    """Robustly extracts and parses JSON from LLM response text."""
    clean = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        clean = match.group(0)
    return json.loads(clean)


def get_llm_dual_sentiment_analysis(
    company_name: str,
    founders_str: str,
    company_news: list[dict],
    company_social: list[dict],
    founder_news: list[dict],
    founder_social: list[dict],
    company_description: str = "",
    categories: str = "",
    api_key: str = None,
    base_url: str = None,
    model: str = DEFAULT_ASTRA_MODEL,
) -> dict | None:
    """
    Evaluates both company and founder sentiment using GPT-6 Astra via the UO OpenAI Portal.
    """
    global LLM_AUTH_FAILED
    if not api_key or LLM_AUTH_FAILED:
        return None

    # Format company coverage
    comp_news_txt = "\n".join([f"- [News] {item['title']} (Source: {item['source']})" for item in company_news[:8]])
    comp_social_txt = "\n".join([f"- [Social] {item['title']} (Context: {item['source']})" for item in company_social[:6]])
    company_coverage = f"Company Media Coverage:\n{comp_news_txt or 'None found'}\n\nCompany Social Discussions:\n{comp_social_txt or 'None found'}"

    # Format founder coverage
    fnd_news_txt = "\n".join([f"- [News] {item['title']} (Source: {item['source']})" for item in founder_news[:8]])
    fnd_social_txt = "\n".join([f"- [Social] {item['title']} (Context: {item['source']})" for item in founder_social[:6]])
    founder_coverage = f"Founder Media Coverage:\n{fnd_news_txt or 'None found'}\n\nFounder Social Discussions:\n{fnd_social_txt or 'None found'}"

    context_snippet = ""
    if company_description:
        context_snippet += f"\nDescription: {company_description}"
    if categories:
        context_snippet += f"\nCategories/Sectors: {categories}"

    prompt = f"""You are an elite venture capital analyst conducting investment due diligence.
Perform a thorough dual-entity sentiment analysis on the startup and its founder(s):
- Company: "{company_name}"{context_snippet}
- Founder(s): "{founders_str or 'Leadership Team'}"

{company_coverage}

{founder_coverage}

Analyze both the company's business traction/reputation AND the founder(s)' leadership/reputation.
Respond ONLY with a valid JSON object matching this exact schema:
{{
  "overall_sentiment_score": <float between -1.000 and 1.000, combined weighted score (60% company, 40% founder)>,
  "sentiment_label": <string: "Very Bullish" | "Bullish" | "Neutral" | "Bearish" | "Very Bearish">,
  "company_sentiment_score": <float between -1.000 and 1.000>,
  "founder_sentiment_score": <float between -1.000 and 1.000>,
  "founder_reputation_label": <string: "Exceptional / Visionary" | "Positive Track Record" | "Neutral / Early Stage" | "Controversial / High Risk">,
  "company_summary_reasoning": <concise 1-2 sentence executive explanation of company market traction, news, and brand sentiment>,
  "founder_summary_reasoning": <concise 1-2 sentence executive explanation of founder reputation, leadership credibility, or controversies>,
  "key_company_risks": <concise summary of major company/market risks, competition, or slowing growth>,
  "key_founder_risks": <concise summary of founder/execution risks, leadership changes, or past controversies>,
  "growth_catalysts": <concise summary of key positive drivers, partnerships, or funding momentum>,
  "top_company_headline": <string or empty>,
  "top_founder_headline": <string or empty>
}}
"""

    headers = {
        "api-key": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    target_base = (
        base_url
        or os.getenv("OPENAI_ENDPOINT")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("ASTRA_BASE_URL")
        or DEFAULT_UO_ENDPOINT
    )

    api_version = os.getenv("AZURE_OPENAI_API_VERSION") or DEFAULT_AZURE_API_VERSION
    is_azure = "azurewebsites.net" in target_base or "openai.azure.com" in target_base
    models_to_try = [model, DEFAULT_ASTRA_MODEL, "gpt-4o", "gpt-4o-mini"]
    seen = set()
    models_to_try = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

    for m in models_to_try:
        if is_azure:
            endpoint = f"{target_base.rstrip('/')}/openai/deployments/{m}/chat/completions?api-version={api_version}"
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a venture capital due diligence AI engine. You output strictly JSON."},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "max_completion_tokens": 850,
            }
        else:
            endpoint = f"{target_base.rstrip('/')}/chat/completions"
            payload = {
                "model": m,
                "messages": [
                    {"role": "system", "content": "You are a venture capital due diligence AI engine. You output strictly JSON."},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "max_completion_tokens": 850,
            }

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=25)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = parse_llm_json(content)
                parsed["overall_sentiment_score"] = round(float(parsed.get("overall_sentiment_score", 0.0)), 3)
                parsed["company_sentiment_score"] = round(float(parsed.get("company_sentiment_score", 0.0)), 3)
                parsed["founder_sentiment_score"] = round(float(parsed.get("founder_sentiment_score", 0.0)), 3)
                return parsed
            elif resp.status_code == 401:
                print("    [!] API key rejected (HTTP 401 Unauthorized).")
                print("        Seamlessly continuing with high-precision local NLP engine.")
                LLM_AUTH_FAILED = True
                return None
            elif resp.status_code in (400, 404):
                continue
            else:
                print(f"    [!] LLM API returned status {resp.status_code}: {resp.text[:120]}")
                break
        except Exception as e:
            print(f"    [!] LLM connection note with model {m}: {e}")
            continue

    return None


def get_vader_fallback_dual_analysis(
    company_name: str,
    founders_str: str,
    company_items: list[dict],
    founder_items: list[dict],
) -> dict:
    """Fallback local sentiment scoring using NLTK VADER when offline or no API key."""
    def score_items(items):
        if not items or not sia:
            return 0.0, "", ""
        scores = []
        top_pos, top_neg = "", ""
        best_pos, worst_neg = -1.0, 1.0
        for item in items:
            text = item.get("title", "")
            pol = sia.polarity_scores(text)
            comp = pol["compound"]
            scores.append(comp)
            if comp > best_pos:
                best_pos = comp
                top_pos = text
            if comp < worst_neg:
                worst_neg = comp
                top_neg = text
        avg = sum(scores) / len(scores) if scores else 0.0
        return avg, top_pos, top_neg

    comp_score, top_comp_pos, _ = score_items(company_items)
    fnd_score, top_fnd_pos, _ = score_items(founder_items)

    # Blend: 60% company, 40% founder (or 100% company if no founder items)
    if founder_items:
        overall_score = round(0.6 * comp_score + 0.4 * fnd_score, 3)
    else:
        overall_score = round(comp_score, 3)

    if overall_score >= 0.35:
        label = "Very Bullish"
    elif overall_score >= 0.10:
        label = "Bullish"
    elif overall_score <= -0.35:
        label = "Very Bearish"
    elif overall_score <= -0.10:
        label = "Bearish"
    else:
        label = "Neutral"

    if fnd_score >= 0.30:
        fnd_label = "Exceptional / Visionary"
    elif fnd_score >= 0.05:
        fnd_label = "Positive Track Record"
    elif fnd_score <= -0.15:
        fnd_label = "Controversial / High Risk"
    else:
        fnd_label = "Neutral / Early Stage"

    return {
        "overall_sentiment_score": overall_score,
        "sentiment_label": label,
        "company_sentiment_score": round(comp_score, 3),
        "founder_sentiment_score": round(fnd_score, 3),
        "founder_reputation_label": fnd_label,
        "company_summary_reasoning": f"Local NLP assessed {len(company_items)} company mentions with average sentiment {round(comp_score, 2)}.",
        "founder_summary_reasoning": f"Local NLP assessed {len(founder_items)} founder mentions for {founders_str or 'Leadership'} with score {round(fnd_score, 2)}.",
        "key_company_risks": "Standard market risks." if comp_score >= 0 else "Negative sentiment detected in recent media.",
        "key_founder_risks": "No public leadership controversies identified." if fnd_score >= 0 else "Leadership scrutiny noted in discussions.",
        "growth_catalysts": "Positive press and community interest." if overall_score > 0 else "Under-the-radar operations.",
        "top_company_headline": top_comp_pos,
        "top_founder_headline": top_fnd_pos,
    }


def analyze_startup_and_founders(
    company_name: str,
    founders_list: list[str],
    company_description: str = "",
    categories: str = "",
    city: str = "",
    country: str = "",
    api_key: str = None,
    base_url: str = None,
    model: str = DEFAULT_ASTRA_MODEL,
    max_news: int = 10,
    max_social: int = 8,
) -> dict:
    """
    Gathers coverage and executes dual sentiment analysis for both company and founders.
    """
    clean_comp = clean_query_term(company_name)
    founders_str = ", ".join(founders_list) if founders_list else ""

    # Build company search queries
    comp_fallbacks = []
    if categories:
        primary_cat = str(categories).split(",")[0].strip()
        comp_fallbacks.append(f"{clean_comp} {primary_cat}")
    if city or country:
        loc = f"{city} {country}".strip()
        comp_fallbacks.append(f"{clean_comp} startup {loc}")
    comp_fallbacks.append(f"{clean_comp} startup")

    # Fetch company coverage
    comp_news = fetch_google_news(clean_comp, fallback_queries=comp_fallbacks, max_items=max_news)
    comp_social = fetch_hacker_news(clean_comp, fallback_queries=comp_fallbacks, max_items=max_social)

    # Build founder search queries
    fnd_news, fnd_social = [], []
    if founders_list:
        # Search for primary founder and founders with company context
        primary_founder = founders_list[0]
        fnd_fallbacks = [
            f"{primary_founder} {clean_comp}",
            f"{primary_founder} founder",
            f"{primary_founder} startup",
        ]
        fnd_news = fetch_google_news(f'"{primary_founder}"', fallback_queries=fnd_fallbacks, max_items=max_news)
        fnd_social = fetch_hacker_news(primary_founder, fallback_queries=fnd_fallbacks, max_items=max_social)

    # 1. Try GPT / Astra LLM Analysis
    llm_result = None
    if api_key:
        llm_result = get_llm_dual_sentiment_analysis(
            company_name=company_name,
            founders_str=founders_str,
            company_news=comp_news,
            company_social=comp_social,
            founder_news=fnd_news,
            founder_social=fnd_social,
            company_description=company_description,
            categories=categories,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

    if llm_result:
        res = llm_result
        res["analysis_engine"] = f"GPT / Astra ({model})"
    else:
        res = get_vader_fallback_dual_analysis(
            company_name=company_name,
            founders_str=founders_str,
            company_items=comp_news + comp_social,
            founder_items=fnd_news + fnd_social,
        )
        res["analysis_engine"] = "Local NLP VADER"

    # Common metrics
    res["founders_analyzed"] = founders_str or "N/A"
    res["company_news_count"] = len(comp_news)
    res["company_social_count"] = len(comp_social)
    res["founder_news_count"] = len(fnd_news)
    res["founder_social_count"] = len(fnd_social)
    res["total_coverage_count"] = len(comp_news) + len(comp_social) + len(fnd_news) + len(fnd_social)

    sample_items = [i["title"] for i in (comp_news + fnd_news)[:3]]
    res["sample_headlines"] = " | ".join(sample_items) if sample_items else "No recent articles found"

    return res


def find_company_and_founder_columns(df: pd.DataFrame) -> tuple[str, str | None]:
    """Finds the best matching Company and Founders column names."""
    # Company candidates
    comp_candidates = ["Company", "company", "Company_Name", "company_name", "Startup", "startup_name", "Name", "name"]
    comp_col = next((c for c in comp_candidates if c in df.columns), None)
    if not comp_col:
        for c in df.columns:
            if df[c].dtype == object and c.lower() not in ("country", "city", "domain", "sector", "gender"):
                comp_col = c
                break
    comp_col = comp_col or df.columns[0]

    # Founder candidates
    fnd_candidates = ["Founders", "founders", "Founder", "founder", "Founding_Team", "CEO", "ceo"]
    fnd_col = next((c for c in fnd_candidates if c in df.columns), None)

    return comp_col, fnd_col


def process_startups_csv(
    input_csv: str,
    founders_csv: str = None,
    output_csv: str = None,
    api_key: str = None,
    base_url: str = None,
    model: str = DEFAULT_ASTRA_MODEL,
    limit: int = None,
    max_news: int = 10,
    max_social: int = 8,
    delay: float = 0.5,
) -> str:
    """
    Processes startups CSV and runs dual sentiment analysis on company and founders.
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    # Resolve API Key
    resolved_api_key = (
        api_key
        or os.getenv("ASTRA_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("GPT_API_KEY")
    )
    resolved_base_url = (
        base_url
        or os.getenv("OPENAI_ENDPOINT")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("ASTRA_BASE_URL")
        or DEFAULT_UO_ENDPOINT
    )

    print(f"\n=======================================================")
    print(f"  VentureLens Dual Sentiment Engine (Company & Founder)")
    print(f"=======================================================")
    print(f"Loading input: '{input_csv}'...")
    df = pd.read_csv(input_csv)

    comp_col, fnd_col = find_company_and_founder_columns(df)
    print(f"Detected Company column: '{comp_col}'")
    if fnd_col:
        print(f"Detected Founders column: '{fnd_col}'")

    # Load Founders.csv lookup for cross-referencing
    founder_lookup = build_founder_lookup(founders_csv)
    if founder_lookup:
        print(f"Loaded Founders.csv lookup with {len(founder_lookup)} company-founder mappings.")

    if limit and limit > 0:
        df = df.head(limit).copy()
        print(f"Limiting analysis to first {limit} companies.")

    if resolved_api_key:
        masked = resolved_api_key[:6] + "..." + resolved_api_key[-4:] if len(resolved_api_key) > 10 else "***"
        print(f"AI Engine: GPT / Astra enabled (Key: {masked}, Model: {model})")
        print(f"Endpoint:  {resolved_base_url}")
    else:
        print("AI Engine: Running high-precision local NLP fallback (NLTK VADER).")
        print("Tip: Provide your key in .env or via --api-key to enable GPT-6 Astra reasoning.")

    results = []
    total = len(df)
    print(f"\n--- Starting Analysis for {total} Companies & Founders ---")

    for idx, row in df.iterrows():
        comp_name = str(row[comp_col]).strip() if pd.notna(row.get(comp_col)) else f"Company_{idx}"

        # Determine founders
        founders = []
        if fnd_col and pd.notna(row.get(fnd_col)):
            founders = parse_founders_list(row[fnd_col])

        # Cross-reference with Founders.csv if missing
        if not founders and comp_name.lower() in founder_lookup:
            founders = founder_lookup[comp_name.lower()]

        # Metadata context
        desc = str(row.get("Description", "")) if "Description" in row and pd.notna(row.get("Description")) else ""
        cats = str(row.get("Categories", "")) if "Categories" in row and pd.notna(row.get("Categories")) else ""
        city = str(row.get("Headquarters (City)", "")) if "Headquarters (City)" in row and pd.notna(row.get("Headquarters (City)")) else ""
        country = str(row.get("Headquarters (Country)", "")) if "Headquarters (Country)" in row and pd.notna(row.get("Headquarters (Country)")) else ""

        fnd_display = ", ".join(founders) if founders else "Unknown / Not Listed"
        print(f"\n[{idx+1}/{total}] Company: '{comp_name}' | Founder(s): '{fnd_display}'")

        data = analyze_startup_and_founders(
            company_name=comp_name,
            founders_list=founders,
            company_description=desc,
            categories=cats,
            city=city,
            country=country,
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            model=model,
            max_news=max_news,
            max_social=max_social,
        )

        print(
            f"       Combined: {data['overall_sentiment_score']} ({data['sentiment_label']}) | "
            f"Company: {data['company_sentiment_score']} | Founder: {data['founder_sentiment_score']} ({data['founder_reputation_label']})"
        )
        if data.get("company_summary_reasoning"):
            print(f"       Company Insight: {data['company_summary_reasoning'][:110]}...")
        if data.get("founder_summary_reasoning"):
            print(f"       Founder Insight: {data['founder_summary_reasoning'][:110]}...")

        results.append(data)

        if delay > 0 and idx < total - 1:
            time.sleep(delay)

    sentiment_df = pd.DataFrame(results)
    enriched_df = pd.concat([df.reset_index(drop=True), sentiment_df.reset_index(drop=True)], axis=1)

    if not output_csv:
        base, ext = os.path.splitext(input_csv)
        output_csv = f"{base}_sentiment{ext}"

    enriched_df.to_csv(output_csv, index=False)
    print(f"\n[+] Successfully saved dual sentiment analysis to:\n    {output_csv}")
    return output_csv


def find_default_startups_file() -> str:
    """Finds the most appropriate default input CSV."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "selected_companies.csv"),
        "selected_companies.csv",
        "Startups.csv",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "Startups.csv"),
        os.path.join(os.path.dirname(__file__), "Startups.csv"),
        "venturelens_portfolio_output.csv",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "Startups.csv"


def main():
    parser = argparse.ArgumentParser(
        description="Run GPT-6 Astra dual sentiment analysis on both startup companies and their founders."
    )
    parser.add_argument(
        "-i", "--input",
        help="Input CSV path (defaults to selected_companies.csv or Startups.csv)",
        default=find_default_startups_file(),
    )
    parser.add_argument(
        "-f", "--founders-file",
        help="Path to Founders.csv (for cross-referencing company founders)",
        default=None,
    )
    parser.add_argument(
        "-o", "--output",
        help="Output CSV path (defaults to <input>_sentiment.csv)",
        default=None,
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        help="Limit to first N companies (ideal for testing or demos)",
        default=None,
    )
    parser.add_argument(
        "-k", "--api-key",
        help="GPT / Astra API Key (or set OPENAI_API_KEY / ASTRA_API_KEY in .env)",
        default=None,
    )
    parser.add_argument(
        "--base-url",
        help="Custom API base URL (defaults to UO OpenAI Portal endpoint)",
        default=None,
    )
    parser.add_argument(
        "--model",
        help="Model identifier (default: gpt-6-astra)",
        default=DEFAULT_ASTRA_MODEL,
    )
    parser.add_argument(
        "--max-news",
        type=int,
        default=10,
        help="Max Google News articles per entity (default: 10)",
    )
    parser.add_argument(
        "--max-social",
        type=int,
        default=8,
        help="Max Hacker News posts per entity (default: 8)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.4,
        help="Delay in seconds between requests (default: 0.4s)",
    )

    args = parser.parse_args()
    process_startups_csv(
        input_csv=args.input,
        founders_csv=args.founders_file,
        output_csv=args.output,
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        limit=args.limit,
        max_news=args.max_news,
        max_social=args.max_social,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
