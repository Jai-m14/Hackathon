#!/usr/bin/env python3
"""
analyze_sentiment.py
--------------------
Performs comprehensive media and social sentiment analysis on companies provided in a CSV.

Uses:
1. Google News RSS: Mainstream media and press coverage
2. Hacker News (Algolia API): Tech community discussions, comments & points
3. LLM / GPT Engine (e.g., GPT-6 Astra, GPT-4o, OpenAI-compatible Astra gateways):
   - Generates exact sentiment scores (-1.0 to 1.0)
   - Sentiment label (Very Bullish -> Very Bearish)
   - Executive AI reasoning & investment sentiment summary
   - Key risks identified from coverage
   - Key catalysts / positive drivers
4. Local Fallback: If no API key is provided, seamlessly falls back to NLTK VADER.

Configuration:
- Set your key in .env or environment variable:
    OPENAI_API_KEY=your_key_here
    # or
    ASTRA_API_KEY=your_key_here
- Or pass via CLI:
    python analyze_sentiment.py -i companies.csv --api-key YOUR_KEY
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

# Load .env file if available
try:
    from dotenv import load_dotenv
    # Look for .env in current dir, script dir, and parent dir
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
except ImportError:
    pass

# Try importing OpenAI client
try:
    from openai import OpenAI
    HAS_OPENAI_LIB = True
except ImportError:
    HAS_OPENAI_LIB = False

# Try importing NLTK VADER as guaranteed local fallback
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)
    sia = SentimentIntensityAnalyzer()
    
    # Financial domain lexicon additions
    FINANCIAL_LEXICON_UPDATES = {
        "soars": 2.4, "surges": 2.4, "beats": 2.0, "outperforms": 2.6,
        "breakthrough": 2.5, "profitable": 2.4, "profitability": 2.2,
        "windfall": 2.2, "tailwind": 1.8, "plummet": -2.6, "plunges": -2.6,
        "slashes": -2.2, "layoffs": -2.8, "downsizing": -2.0, "lawsuit": -2.2,
        "antitrust": -2.4, "breach": -2.6, "hack": -2.5, "fraud": -3.2,
        "headwind": -1.8, "fire sale": -3.0, "bankrupt": -3.2, "bankruptcy": -3.2,
    }
    sia.lexicon.update(FINANCIAL_LEXICON_UPDATES)
except Exception:
    sia = None


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def clean_company_name_for_query(name: str) -> str:
    """Cleans legal suffixes and brackets for high-precision search."""
    clean = re.sub(r"\(.*?\)", "", str(name))
    clean = re.sub(
        r"\b(Inc|Corp|LLC|Ltd|Co|Corporation|Technologies|Tech)\b\.?",
        "",
        clean,
        flags=re.IGNORECASE,
    )
    return clean.strip() or str(name).strip()


def fetch_google_news(company_name: str, max_items: int = 15) -> list[dict]:
    """Fetches recent news articles from Google News RSS."""
    query = clean_company_name_for_query(company_name)
    encoded = urllib.parse.quote(f'"{query}"')
    url = f"https://news.google.com/rss/search?q={encoded}+when:45d&hl=en-US&gl=US&ceid=US:en"
    articles = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item")[:max_items]:
                title = item.findtext("title", default="").strip()
                pub_date = item.findtext("pubDate", default="").strip()
                source = item.findtext("source", default="").strip()
                if title:
                    articles.append({
                        "title": title,
                        "source": source or "News Media",
                        "pub_date": pub_date,
                        "type": "media",
                    })
    except Exception:
        pass

    if not articles:
        try:
            url_fallback = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
            resp = requests.get(url_fallback, headers=HEADERS, timeout=12)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:max_items]:
                    title = item.findtext("title", default="").strip()
                    if title:
                        articles.append({
                            "title": title,
                            "source": "News Media",
                            "pub_date": "",
                            "type": "media",
                        })
        except Exception:
            pass

    return articles


def fetch_hacker_news(company_name: str, max_items: int = 10) -> list[dict]:
    """Fetches tech and community discussions from Hacker News."""
    query = clean_company_name_for_query(company_name)
    url = "https://hn.algolia.com/api/v1/search"
    posts = []

    try:
        params = {"query": query, "tags": "story", "hitsPerPage": max_items}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            for hit in data.get("hits", []):
                title = hit.get("title") or ""
                points = hit.get("points") or 0
                comments = hit.get("num_comments") or 0
                if title:
                    posts.append({
                        "title": title,
                        "source": f"Hacker News ({points} pts, {comments} cmts)",
                        "pub_date": hit.get("created_at", "")[:10],
                        "type": "social",
                    })
    except Exception:
        pass

    return posts


def get_llm_sentiment_analysis(
    company_name: str,
    news_items: list[dict],
    social_items: list[dict],
    api_key: str,
    base_url: str = None,
    model: str = "gpt-6-astra",
) -> dict | None:
    """
    Uses GPT / Astra API to evaluate news and social coverage and return structured JSON sentiment.
    """
    if not api_key:
        return None

    news_text = "\n".join([f"- [News] {item['title']} (Source: {item['source']})" for item in news_items[:12]])
    social_text = "\n".join([f"- [Social] {item['title']} (Context: {item['source']})" for item in social_items[:8]])

    coverage_summary = f"Mainstream Media Coverage:\n{news_text or 'None'}\n\nSocial & Community Discussions:\n{social_text or 'None'}"

    prompt = f"""You are an elite quantitative and growth investment analyst.
Perform an objective media and social sentiment analysis for the company: "{company_name}".

Analyze the following recent headlines and discussions:
{coverage_summary}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "overall_sentiment_score": <float between -1.000 and 1.000, where +1.0 is maximum positive, 0.0 is neutral, -1.0 is maximum negative>,
  "sentiment_label": <string: "Very Bullish" | "Bullish" | "Neutral" | "Bearish" | "Very Bearish">,
  "media_sentiment_score": <float between -1.000 and 1.000>,
  "social_sentiment_score": <float between -1.000 and 1.000>,
  "positive_pct": <float between 0.0 and 100.0>,
  "neutral_pct": <float between 0.0 and 100.0>,
  "negative_pct": <float between 0.0 and 100.0>,
  "sentiment_reasoning": <concise 1-2 sentence executive explanation of overall sentiment drivers>,
  "key_risks_identified": <concise summary of major concerns, lawsuits, slowing growth, or negative sentiment seen in coverage>,
  "key_catalysts_identified": <concise summary of growth catalysts, partnerships, or positive sentiment drivers>,
  "top_positive_headline": <string or empty>,
  "top_negative_headline": <string or empty>
}}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    endpoint = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"

    models_to_try = [model, "gpt-6-astra", "gpt-4o", "gpt-4o-mini"]
    # De-duplicate while preserving order
    seen = set()
    models_to_try = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

    for m in models_to_try:
        payload = {
            "model": m,
            "messages": [
                {"role": "system", "content": "You are a financial sentiment analysis engine. You output strictly JSON."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=25)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                # Normalize values
                parsed["overall_sentiment_score"] = round(float(parsed.get("overall_sentiment_score", 0.0)), 3)
                parsed["media_sentiment_score"] = round(float(parsed.get("media_sentiment_score", 0.0)), 3)
                parsed["social_sentiment_score"] = round(float(parsed.get("social_sentiment_score", 0.0)), 3)
                return parsed
            elif resp.status_code in (400, 404):
                # Try next fallback model
                continue
            else:
                print(f"    [!] LLM API returned status {resp.status_code}: {resp.text[:150]}")
                break
        except Exception as e:
            print(f"    [!] LLM request exception with model {m}: {e}")
            continue

    return None


def get_vader_fallback_analysis(company_name: str, news_items: list[dict], social_items: list[dict]) -> dict:
    """Local sentiment analysis fallback using VADER lexicon."""
    all_items = news_items + social_items

    def score_item(t):
        return sia.polarity_scores(t)["compound"] if sia and t else 0.0

    news_scores = [score_item(item["title"]) for item in news_items]
    social_scores = [score_item(item["title"]) for item in social_items]
    all_scores = news_scores + social_scores

    news_count = len(news_items)
    social_count = len(social_items)
    total_count = len(all_items)

    media_score = round(sum(news_scores) / news_count, 3) if news_count > 0 else 0.0
    social_score = round(sum(social_scores) / social_count, 3) if social_count > 0 else 0.0

    if news_count > 0 and social_count > 0:
        overall_score = round(0.65 * media_score + 0.35 * social_score, 3)
    elif news_count > 0:
        overall_score = media_score
    elif social_count > 0:
        overall_score = social_score
    else:
        overall_score = 0.0

    if total_count == 0:
        label = "Neutral (No Coverage)"
    elif overall_score >= 0.35:
        label = "Very Bullish"
    elif overall_score >= 0.10:
        label = "Bullish"
    elif overall_score <= -0.35:
        label = "Very Bearish"
    elif overall_score <= -0.10:
        label = "Bearish"
    else:
        label = "Neutral"

    pos_items = [s for s in all_scores if s > 0.05]
    neg_items = [s for s in all_scores if s < -0.05]
    neu_items = [s for s in all_scores if -0.05 <= s <= 0.05]

    pos_pct = round((len(pos_items) / total_count) * 100, 1) if total_count > 0 else 0.0
    neg_pct = round((len(neg_items) / total_count) * 100, 1) if total_count > 0 else 0.0
    neu_pct = round((len(neu_items) / total_count) * 100, 1) if total_count > 0 else 0.0

    top_pos = ""
    top_neg = ""
    if all_items:
        pairs = list(zip(all_items, all_scores))
        pairs.sort(key=lambda x: x[1], reverse=True)
        if pairs[0][1] > 0.05:
            top_pos = pairs[0][0]["title"]
        if pairs[-1][1] < -0.05:
            top_neg = pairs[-1][0]["title"]

    return {
        "overall_sentiment_score": overall_score,
        "sentiment_label": label,
        "media_sentiment_score": media_score,
        "social_sentiment_score": social_score,
        "positive_pct": pos_pct,
        "neutral_pct": neu_pct,
        "negative_pct": neg_pct,
        "sentiment_reasoning": f"Derived via quantitative NLP analysis across {total_count} articles/posts.",
        "key_risks_identified": "Identified from negative media spikes." if neg_pct > 25 else "None prominent",
        "key_catalysts_identified": "Positive momentum indicated in recent press." if pos_pct > 25 else "Standard operations",
        "top_positive_headline": top_pos,
        "top_negative_headline": top_neg,
    }


def analyze_company(
    company_name: str,
    api_key: str = None,
    base_url: str = None,
    model: str = "gpt-6-astra",
    max_news: int = 15,
    max_social: int = 10,
) -> dict:
    """Gathers feeds and analyzes sentiment using GPT / Astra with VADER fallback."""
    news_items = fetch_google_news(company_name, max_items=max_news)
    social_items = fetch_hacker_news(company_name, max_items=max_social)
    all_items = news_items + social_items

    # 1. Try GPT / Astra LLM Analysis
    llm_result = None
    if api_key:
        llm_result = get_llm_sentiment_analysis(
            company_name=company_name,
            news_items=news_items,
            social_items=social_items,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

    # 2. If no LLM result, use fallback
    if llm_result:
        res = llm_result
        res["analysis_engine"] = f"GPT / Astra ({model})"
    else:
        res = get_vader_fallback_analysis(company_name, news_items, social_items)
        res["analysis_engine"] = "Local NLP VADER"

    # Common metrics
    res["news_articles_count"] = len(news_items)
    res["social_posts_count"] = len(social_items)
    res["total_coverage_count"] = len(all_items)
    res["sample_headlines"] = " | ".join([item["title"] for item in all_items[:3]])

    return res


def find_company_name_column(df: pd.DataFrame) -> str:
    """Finds best matching company column."""
    candidates = [
        "company_name", "company", "name", "Company_Name",
        "Company", "Name", "ticker", "Ticker", "startup_name",
        "Startup", "organization"
    ]
    for col in candidates:
        if col in df.columns:
            return col
    for col in df.columns:
        if df[col].dtype == object and col.lower() not in ("id", "company_id", "country", "city", "domain", "sector"):
            return col
    return df.columns[0]


def process_csv(
    input_csv: str,
    output_csv: str = None,
    api_key: str = None,
    base_url: str = None,
    model: str = "gpt-6-astra",
    max_news: int = 15,
    max_social: int = 10,
    delay: float = 0.4,
):
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    # Resolve API Key from argument or environment
    resolved_api_key = (
        api_key
        or os.getenv("ASTRA_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("GPT_API_KEY")
    )
    resolved_base_url = base_url or os.getenv("ASTRA_BASE_URL") or os.getenv("OPENAI_BASE_URL")

    print(f"Loading '{input_csv}'...")
    df = pd.read_csv(input_csv)
    company_col = find_company_name_column(df)
    print(f"Target company column: '{company_col}' ({len(df)} companies)")

    if resolved_api_key:
        masked = resolved_api_key[:6] + "..." + resolved_api_key[-4:] if len(resolved_api_key) > 10 else "***"
        print(f"AI Engine: GPT / Astra enabled (Key: {masked}, Model: {model})")
    else:
        print("AI Engine: No API key detected. Running high-precision local NLP fallback.")
        print("Tip: Provide your key in .env or via --api-key to enable GPT Astra reasoning.")

    results = []
    print("\n--- Running Sentiment Analysis ---")
    for idx, row in df.iterrows():
        name = str(row[company_col]).strip()
        print(f"[{idx+1}/{len(df)}] Analyzing: {name}...")
        data = analyze_company(
            company_name=name,
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            model=model,
            max_news=max_news,
            max_social=max_social,
        )
        print(
            f"       Score: {data['overall_sentiment_score']} ({data['sentiment_label']}) | "
            f"Engine: {data['analysis_engine']} | "
            f"Coverage: {data['total_coverage_count']} mentions"
        )
        if data.get("sentiment_reasoning"):
            print(f"       Insight: {data['sentiment_reasoning'][:120]}...")
        results.append(data)

        if delay > 0 and idx < len(df) - 1:
            time.sleep(delay)

    sentiment_df = pd.DataFrame(results)
    enriched_df = pd.concat([df.reset_index(drop=True), sentiment_df.reset_index(drop=True)], axis=1)

    if not output_csv:
        base, ext = os.path.splitext(input_csv)
        output_csv = f"{base}_sentiment{ext}"

    enriched_df.to_csv(output_csv, index=False)
    print(f"\n[+] Successfully saved sentiment analysis to:\n    {output_csv}")
    return output_csv


def main():
    parser = argparse.ArgumentParser(
        description="Run GPT / Astra media and social sentiment analysis on companies in a CSV."
    )
    parser.add_argument(
        "-i", "--input",
        help="Input CSV path (defaults to sample_selected_companies.csv)",
        default=os.path.join(os.path.dirname(__file__), "sample_selected_companies.csv"),
    )
    parser.add_argument(
        "-o", "--output",
        help="Output CSV path (defaults to <input>_sentiment.csv)",
        default=None,
    )
    parser.add_argument(
        "-k", "--api-key",
        help="GPT / Astra API Key (or set OPENAI_API_KEY / ASTRA_API_KEY in .env)",
        default=None,
    )
    parser.add_argument(
        "--base-url",
        help="Custom API base URL if using an Astra gateway or proxy",
        default=None,
    )
    parser.add_argument(
        "--model",
        help="Model identifier (default: gpt-6-astra, fallback to gpt-4o)",
        default="gpt-6-astra",
    )
    parser.add_argument(
        "--max-news",
        type=int,
        default=15,
        help="Max Google News articles per company (default: 15)",
    )
    parser.add_argument(
        "--max-social",
        type=int,
        default=10,
        help="Max Hacker News posts per company (default: 10)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.4,
        help="Delay in seconds between requests (default: 0.4s)",
    )

    args = parser.parse_args()
    process_csv(
        input_csv=args.input,
        output_csv=args.output,
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        max_news=args.max_news,
        max_social=args.max_social,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
