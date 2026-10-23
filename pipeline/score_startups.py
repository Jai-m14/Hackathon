"""VentureLens: transparent valuation and allocation model for the Y Combinator dataset.

Run (defaults to data/raw/Startups.csv and data/raw/Founders.csv):
    py pipeline/score_startups.py
    py pipeline/score_startups.py path/to/Startups.csv path/to/Founders.csv

Writes outputs/venturelens_portfolio_output.csv, outputs/venturelens_scored_companies.csv
and outputs/selected_companies.csv.

Startups.csv has no ARR, valuation, runway or headcount, so each input of the
original model is replaced by the closest observable proxy:

    original field            ->  YC proxy
    Revenue_ARR_Millions      ->  Investor_Count   (non-YC backers = market demand)
    Valuation_USD_Millions    ->  Total_Raised_USD_Millions (disclosed rounds)
    Acquisition_Status        ->  Status == "Operating"
    Funding_Stage             ->  stage bucket derived from total raised
    Domain                    ->  sector bucket derived from Categories
    Runway_Score              ->  Survival_Score  (years survived since YC batch)
    Resilience_Score          ->  Backing_Score   (tier-1 investors + founding team)
    AI_Score                  ->  Tech_Score      (sector growth profile)

This is an educational screening model, not financial advice.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # repo root, for paths.py
import paths  # noqa: E402

CAPITAL_USD = 100_000
CASH_WEIGHT = 0.10
MAX_POSITION = 0.25
MIN_POSITION = 0.04
MIN_COMPS = 10  # 688 companies vs 50k in the old dataset, so peer groups are smaller

STAGE_SCORE = {
    "Pre-IPO": 0.25,
    "Series C+": 0.50,
    "Series B": 0.67,
    "Series A": 0.83,
    "Seed": 1.00,
}
# Stage bucket edges on total disclosed funding (USD millions).
STAGE_BINS = [0, 2, 15, 50, 200, np.inf]
STAGE_LABELS = ["Seed", "Series A", "Series B", "Series C+", "Pre-IPO"]

# Categories -> coarse domain. The first domain whose keywords match a company wins.
DOMAIN_KEYWORDS = {
    "AI & Data": ["artificial intelligence", "machine learning", "big data", "analytics",
                  "data", "search", "natural language"],
    "FinTech": ["finance", "payments", "bitcoin", "banking", "insurance", "accounting",
                "crowdfunding", "lending"],
    "Enterprise SaaS": ["saas", "enterprise", "software", "cloud", "developer", "security",
                        "web hosting", "api", "productivity", "recruiting", "legal"],
    "Health & Education": ["health", "medical", "biotech", "education", "fitness"],
    "Hardware": ["hardware", "robotics", "3d", "manufacturing", "energy", "automotive"],
    "Commerce": ["e-commerce", "marketplace", "advertising", "marketing", "travel",
                 "retail", "real estate", "logistics", "delivery", "food"],
    "Consumer & Social": ["social", "messaging", "games", "music", "video", "photo",
                          "mobile", "curated web", "media", "entertainment", "dating"],
}
TECH_SCORE = {
    "AI & Data": 1.00,
    "Enterprise SaaS": 0.83,
    "FinTech": 0.83,
    "Health & Education": 0.67,
    "Hardware": 0.67,
    "Commerce": 0.50,
    "Consumer & Social": 0.33,
    "Other": 0.50,
}
TIER1_INVESTORS = {
    "Sequoia Capital", "Andreessen Horowitz", "Accel Partners", "Greylock Partners",
    "Benchmark", "Kleiner Perkins Caufield & Byers", "Founders Fund", "Khosla Ventures",
    "Index Ventures", "Union Square Ventures", "General Catalyst Partners",
    "First Round Capital", "Google Ventures", "New Enterprise Associates",
    "Charles River Ventures", "Redpoint Ventures", "Lightspeed Venture Partners",
    "Bessemer Venture Partners", "SV Angel", "Yuri Milner", "DST Global", "Draper Fisher Jurvetson",
}


def robust_median(s: pd.Series) -> float:
    """Median after removing extreme 1% tails."""
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) == 0:
        return np.nan
    lo, hi = s.quantile([0.01, 0.99])
    return float(s.clip(lo, hi).median())


def total_raised(text) -> float:
    """'$1200000, undisclosed amount, $3,000,000' -> 4200000.0 (undisclosed rounds count as 0)."""
    if pd.isna(text):
        return 0.0
    return sum(float(a.replace(",", "")) for a in re.findall(r"\$([\d,]+)", str(text)))


def split_list(text) -> list[str]:
    if pd.isna(text):
        return []
    return list(dict.fromkeys(x.strip() for x in str(text).split(",") if x.strip()))


def assign_domain(categories) -> str:
    cats = " | ".join(split_list(categories)).lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(k in cats for k in keywords):
            return domain
    return "Other"


def load_data(startups_path: str, founders_path: str) -> pd.DataFrame:
    df = pd.read_csv(startups_path).copy()
    df = df.rename(columns={"Satus": "Status", "Company": "Company_ID"})
    df = df.drop_duplicates(subset="Company_ID")

    df["Total_Raised_USD_Millions"] = df["Amounts raised in different funding rounds"].map(total_raised) / 1e6
    investors = df["Investors"].map(split_list)
    df["Investor_Count"] = investors.map(lambda xs: sum(x != "Y Combinator" for x in xs))
    df["Tier1_Investor_Count"] = investors.map(lambda xs: sum(x in TIER1_INVESTORS for x in xs))
    df["Domain"] = df["Categories"].map(assign_domain)
    df["Funding_Stage"] = pd.cut(df["Total_Raised_USD_Millions"], STAGE_BINS,
                                 labels=STAGE_LABELS, right=False).astype(str)

    founders = pd.read_csv(founders_path)
    team = founders.groupby("Company").agg(
        Founder_Count=("Founder", "count"),
        Female_Founders=("Gender", lambda g: int((g == "Female").sum())),
    )
    df = df.merge(team, left_on="Company_ID", right_index=True, how="left")
    # Fall back to the Founders column in Startups.csv when Founders.csv has no match.
    df["Founder_Count"] = df["Founder_Count"].fillna(
        df["Founders"].map(lambda f: len(split_list(f)) or np.nan)
    )

    # A company with no disclosed funding or no outside backers cannot be priced.
    df = df[(df["Total_Raised_USD_Millions"] > 0) & (df["Investor_Count"] > 0)].copy()
    df["Observed_Multiple"] = df["Total_Raised_USD_Millions"] / df["Investor_Count"]
    # Avoid a tiny number of extreme observations dominating medians.
    df["Observed_Multiple"] = df["Observed_Multiple"].clip(upper=df["Observed_Multiple"].quantile(0.99))
    return df


def add_valuation(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate fair funding from comparable-company $-raised-per-backer multiples."""
    overall_multiple = robust_median(df["Observed_Multiple"])
    domain_multiple = df.groupby("Domain")["Observed_Multiple"].transform(robust_median)
    stage_multiple = df.groupby("Funding_Stage")["Observed_Multiple"].transform(robust_median)
    pair_multiple = df.groupby(["Domain", "Funding_Stage"])["Observed_Multiple"].transform(robust_median)
    pair_count = df.groupby(["Domain", "Funding_Stage"])["Company_ID"].transform("count")

    # Prefer domain-stage peers; fall back when the peer group is too small.
    multiple = pair_multiple.where(pair_count >= MIN_COMPS, domain_multiple)
    multiple = multiple.fillna(stage_multiple).fillna(overall_multiple)

    df["Peer_Multiple"] = multiple
    df["Fair_Value_USD_Millions"] = df["Investor_Count"] * df["Peer_Multiple"]
    df["Upside_to_Fair_Value"] = (
        df["Fair_Value_USD_Millions"] / df["Total_Raised_USD_Millions"] - 1
    )
    return df


def minmax(s: pd.Series) -> pd.Series:
    lo, hi = s.quantile(0.05), s.quantile(0.95)
    if hi <= lo:
        return pd.Series(0.5, index=s.index)
    return ((s.clip(lo, hi) - lo) / (hi - lo)).clip(0, 1)


def add_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Create an explainable growth-investor score from available fields."""
    as_of_year = df["Y Combinator Year"].max() + 1
    df["Years_Since_YC"] = as_of_year - df["Y Combinator Year"]

    df["Valuation_Score"] = minmax(df["Upside_to_Fair_Value"])
    df["Survival_Score"] = (df["Years_Since_YC"] / 5).clip(0, 1)
    df["Backing_Score"] = (
        0.7 * (df["Tier1_Investor_Count"] / 3).clip(0, 1)
        + 0.3 * (df["Founder_Count"] / 3).clip(0, 1).fillna(0.5)
    )
    df["Tech_Score"] = df["Domain"].map(TECH_SCORE).fillna(0.5)
    df["Stage_Score"] = df["Funding_Stage"].map(STAGE_SCORE).fillna(0.5)

    # Transparent weighted score; change weights in one place for sensitivity tests.
    df["Risk_Adjusted_Score"] = (
        0.35 * df["Valuation_Score"]
        + 0.25 * df["Survival_Score"]
        + 0.20 * df["Backing_Score"]
        + 0.10 * df["Tech_Score"]
        + 0.10 * df["Stage_Score"]
    )
    return df


def cap_and_floor(weights: pd.Series, total: float, lo: float, hi: float) -> pd.Series:
    """Water-fill: scale to `total`, pin positions at the floor/cap, redistribute, repeat."""
    w = weights / weights.sum() * total
    for _ in range(len(w)):
        w = w.clip(lo, hi)
        free = (w > lo + 1e-12) & (w < hi - 1e-12)
        gap = total - w.sum()
        if abs(gap) < 1e-12 or not free.any():
            break
        w[free] += gap * w[free] / w[free].sum()
    return w


def allocate(df: pd.DataFrame, capital: float = CAPITAL_USD) -> pd.DataFrame:
    """Allocate capital in USD by conviction x relative size, reserving cash and enforcing a cap.

    Allocation_Score_i = Risk_Adjusted_Score_i * Scale_Factor_i
    Scale_Factor_i     = sqrt(Funding_Factor_i * Size_Factor_i)
    Funding_Factor_i   = ln(1 + raised_i in $k) / mean_j ln(1 + raised_j in $k)
    Size_Factor_i      = ln(1 + backers_i)      / mean_j ln(1 + backers_j)

    Log scaling keeps a $500M company from getting 1000x the weight of a $500k one,
    while still tilting toward companies that are larger and better funded (more
    de-risked). Weights are normalised to the investable 90% and water-filled
    between MIN_POSITION and MAX_POSITION.
    """
    selected = df[df["Status"].eq("Operating")].copy()
    selected = selected.sort_values("Risk_Adjusted_Score", ascending=False).head(10)

    log_funding = np.log1p(selected["Total_Raised_USD_Millions"] * 1_000)
    log_size = np.log1p(selected["Investor_Count"])
    selected["Funding_Factor"] = log_funding / log_funding.mean()
    selected["Size_Factor"] = log_size / log_size.mean()
    selected["Scale_Factor"] = np.sqrt(selected["Funding_Factor"] * selected["Size_Factor"])
    selected["Allocation_Score"] = (
        selected["Risk_Adjusted_Score"].clip(lower=0.01) * selected["Scale_Factor"]
    )

    selected["Weight"] = cap_and_floor(
        selected["Allocation_Score"], 1 - CASH_WEIGHT, MIN_POSITION, MAX_POSITION
    )
    # Whole dollars; any rounding remainder goes to the top-ranked position.
    dollars = (selected["Weight"] * capital).round().astype(int)
    dollars.iloc[0] += int(round(capital * (1 - CASH_WEIGHT))) - dollars.sum()
    selected["Allocation_USD"] = dollars

    cash = pd.DataFrame([{
        "Company_ID": "CASH",
        "Domain": "Cash reserve",
        "Weight": CASH_WEIGHT,
        "Allocation_USD": int(round(capital * CASH_WEIGHT)),
        "Risk_Adjusted_Score": np.nan,
    }])
    return pd.concat([selected, cash], ignore_index=True)


def export_for_sentiment(portfolio: pd.DataFrame, path: str) -> None:
    """Write the selected companies in the schema pipeline/analyze_sentiment.py reads."""
    picks = portfolio[portfolio["Company_ID"].ne("CASH")]
    pd.DataFrame({
        "company_name": picks["Company_ID"],
        "domain": picks["Domain"],
        "country": picks["Headquarters (Country)"].fillna("USA"),
        "funding_stage": picks["Funding_Stage"],
        "website": picks["Website"],
    }).to_csv(path, index=False)


def main(startups_path: str, founders_path: str) -> None:
    df = add_scores(add_valuation(load_data(startups_path, founders_path)))
    portfolio = allocate(df)
    cols = ["Company_ID", "Domain", "Funding_Stage", "Total_Raised_USD_Millions",
            "Investor_Count", "Fair_Value_USD_Millions", "Upside_to_Fair_Value",
            "Risk_Adjusted_Score", "Scale_Factor", "Weight", "Allocation_USD"]
    print("Top companies by transparent risk-adjusted score:")
    print(portfolio[[c for c in cols if c in portfolio]].to_string(index=False))
    paths.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    portfolio.to_csv(paths.PORTFOLIO_CSV, index=False)
    df.to_csv(paths.SCORED_CSV, index=False)
    export_for_sentiment(portfolio, paths.SELECTED_COMPANIES_CSV)


if __name__ == "__main__":
    if len(sys.argv) not in (1, 3):
        raise SystemExit("Usage: py pipeline/score_startups.py [Startups.csv Founders.csv]")
    main(*(sys.argv[1:] or [paths.STARTUPS_CSV, paths.FOUNDERS_CSV]))
