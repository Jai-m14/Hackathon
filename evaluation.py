"""VentureLens: transparent valuation and allocation model for the hackathon dataset.

Run:
    python valuation_model.py global_tech_startups_2026.csv

All monetary values in the input are USD millions.
This is an educational screening model, not financial advice.
"""
from __future__ import annotations

import sys
import numpy as np
import pandas as pd

CASH_WEIGHT = 0.10
MAX_POSITION = 0.25
MIN_COMPS = 30

AI_SCORE = {"None": 0.00, "Low": 0.33, "Medium": 0.67, "High": 1.00}
STAGE_SCORE = {
    "Pre-IPO": 0.25,
    "Series C+": 0.50,
    "Series B": 0.67,
    "Series A": 0.83,
    "Seed": 1.00,
}


def robust_median(s: pd.Series) -> float:
    """Median after removing extreme 1% tails."""
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) == 0:
        return np.nan
    lo, hi = s.quantile([0.01, 0.99])
    return float(s.clip(lo, hi).median())


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path).copy()
    df = df.drop_duplicates(subset="Company_ID")
    # A company with no ARR cannot be valued using an ARR multiple.
    df = df[df["Revenue_ARR_Millions"] > 0].copy()
    df["Observed_Multiple"] = (
        df["Valuation_USD_Millions"] / df["Revenue_ARR_Millions"]
    )
    # Avoid a tiny number of synthetic/extreme observations dominating medians.
    df["Observed_Multiple"] = df["Observed_Multiple"].clip(upper=df["Observed_Multiple"].quantile(0.99))
    return df


def add_valuation(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate fair value from comparable-company ARR multiples."""
    overall_multiple = robust_median(df["Observed_Multiple"])
    domain_multiple = df.groupby("Domain")["Observed_Multiple"].transform(robust_median)
    stage_multiple = df.groupby("Funding_Stage")["Observed_Multiple"].transform(robust_median)
    pair_multiple = df.groupby(["Domain", "Funding_Stage"])["Observed_Multiple"].transform(robust_median)
    pair_count = df.groupby(["Domain", "Funding_Stage"])["Company_ID"].transform("count")

    # Prefer domain-stage peers; fall back when the peer group is too small.
    multiple = pair_multiple.where(pair_count >= MIN_COMPS, domain_multiple)
    multiple = multiple.fillna(stage_multiple).fillna(overall_multiple)

    df["Peer_ARR_Multiple"] = multiple
    df["Fair_Value_USD_Millions"] = df["Revenue_ARR_Millions"] * df["Peer_ARR_Multiple"]
    df["Upside_to_Fair_Value"] = (
        df["Fair_Value_USD_Millions"] / df["Valuation_USD_Millions"] - 1
    )
    return df


def minmax(s: pd.Series) -> pd.Series:
    lo, hi = s.quantile(0.05), s.quantile(0.95)
    if hi <= lo:
        return pd.Series(0.5, index=s.index)
    return ((s.clip(lo, hi) - lo) / (hi - lo)).clip(0, 1)


def add_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Create an explainable growth-investor score from available fields."""
    df["Valuation_Score"] = minmax(df["Upside_to_Fair_Value"])
    df["Runway_Score"] = (df["Runway_Months_2024"] / 24).clip(0, 1)
    df["Resilience_Score"] = (
        df["Current_Headcount_2026"] / df["Peak_Headcount_2023"].replace(0, np.nan)
    ).clip(0, 1).fillna(0)
    df["AI_Score"] = df["AI_Adoption_Level"].map(AI_SCORE).fillna(0.5)
    df["Stage_Score"] = df["Funding_Stage"].map(STAGE_SCORE).fillna(0.5)

    # Transparent weighted score; change weights in one place for sensitivity tests.
    df["Risk_Adjusted_Score"] = (
        0.35 * df["Valuation_Score"]
        + 0.25 * df["Runway_Score"]
        + 0.20 * df["Resilience_Score"]
        + 0.10 * df["AI_Score"]
        + 0.10 * df["Stage_Score"]
    )
    return df


def allocate(df: pd.DataFrame, capital: float = 100.0) -> pd.DataFrame:
    """Allocate capital in USD millions, reserving cash and enforcing a cap."""
    investable = capital * (1 - CASH_WEIGHT)
    selected = df[df["Acquisition_Status"].eq("Independent")].copy()
    selected = selected.sort_values("Risk_Adjusted_Score", ascending=False).head(10)

    # Positive score weights; normalization gives a reproducible portfolio.
    raw = selected["Risk_Adjusted_Score"].clip(lower=0.01)
    selected["Weight"] = raw / raw.sum() * (1 - CASH_WEIGHT)
    selected["Weight"] = selected["Weight"].clip(upper=MAX_POSITION)
    # Redistribute any leftover weight once, among positions below the cap.
    leftover = (1 - CASH_WEIGHT) - selected["Weight"].sum()
    eligible = selected["Weight"] < MAX_POSITION
    if leftover > 1e-9 and eligible.any():
        selected.loc[eligible, "Weight"] += leftover / eligible.sum()

    selected["Allocation_USD_Millions"] = selected["Weight"] * capital
    cash = pd.DataFrame([{
        "Company_ID": "CASH",
        "Domain": "Cash reserve",
        "Weight": CASH_WEIGHT,
        "Allocation_USD_Millions": capital * CASH_WEIGHT,
        "Risk_Adjusted_Score": np.nan,
    }])
    return pd.concat([selected, cash], ignore_index=True)


def main(path: str) -> None:
    df = add_scores(add_valuation(load_data(path)))
    portfolio = allocate(df)
    cols = ["Company_ID", "Domain", "Funding_Stage", "Valuation_USD_Millions",
            "Fair_Value_USD_Millions", "Upside_to_Fair_Value",
            "Risk_Adjusted_Score", "Weight", "Allocation_USD_Millions"]
    print("Top companies by transparent risk-adjusted score:")
    print(portfolio[[c for c in cols if c in portfolio]].to_string(index=False))
    portfolio.to_csv("venturelens_portfolio_output.csv", index=False)
    df.to_csv("venturelens_scored_companies.csv", index=False)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python valuation_model.py global_tech_startups_2026.csv")
    main(sys.argv[1])
