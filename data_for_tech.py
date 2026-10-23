import pandas as pd
import numpy as np

df = pd.read_csv("global_tech_startups_2026.csv")

# 删除重复公司
df = df.drop_duplicates(subset="Company_ID")

# 只保留有正 ARR 和估值的公司
df = df[
    (df["Revenue_ARR_Millions"] > 0) &
    (df["Valuation_USD_Millions"] > 0)
].copy()

# 投资候选池：只考虑仍然独立的公司
candidates = df[
    df["Acquisition_Status"] == "Independent"
].copy()

# 计算当前 ARR multiple
candidates["Observed_Multiple"] = (
    candidates["Valuation_USD_Millions"] /
    candidates["Revenue_ARR_Millions"]
)

print(candidates.shape)
print(candidates["Observed_Multiple"].describe())


def robust_median(series):
    series = series.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if len(series) == 0:
        return np.nan

    lower = series.quantile(0.01)
    upper = series.quantile(0.99)

    clipped = series.clip(lower, upper)

    return clipped.median()


peer_multiples = (
    candidates
    .groupby(["Domain", "Funding_Stage"])
    ["Observed_Multiple"]
    .agg(
        Peer_Count="count",
        Peer_Median="median",
        Peer_P25=lambda x: x.quantile(0.25),
        Peer_P75=lambda x: x.quantile(0.75)
    )
    .reset_index()
)

candidates = candidates.merge(
    peer_multiples,
    on=["Domain", "Funding_Stage"],
    how="left"
)

domain_multiples = (
    candidates
    .groupby("Domain")["Observed_Multiple"]
    .apply(robust_median)
)

stage_multiples = (
    candidates
    .groupby("Funding_Stage")["Observed_Multiple"]
    .apply(robust_median)
)

overall_multiple = robust_median(
    candidates["Observed_Multiple"]
)

def choose_multiple(row):
    # 优先使用 domain + stage peer
    if row["Peer_Count"] >= 30:
        return row["Peer_Median"]

    # 如果组合样本太少，退回 domain median
    if row["Domain"] in domain_multiples.index:
        return domain_multiples[row["Domain"]]

    # 再退回 funding stage median
    if row["Funding_Stage"] in stage_multiples.index:
        return stage_multiples[row["Funding_Stage"]]

    return overall_multiple

candidates["Selected_Peer_Multiple"] = candidates.apply(
    choose_multiple,
    axis=1
)


# 计算三个估值情景
candidates["Downside_Value"] = (
    candidates["Revenue_ARR_Millions"] *
    candidates["Peer_P25"]
)

candidates["Base_Fair_Value"] = (
    candidates["Revenue_ARR_Millions"] *
    candidates["Peer_Median"]
)

candidates["Upside_Value"] = (
    candidates["Revenue_ARR_Millions"] *
    candidates["Peer_P75"]
)

candidates["Valuation_Upside"] = (
    candidates["Base_Fair_Value"] /
    candidates["Valuation_USD_Millions"]
    - 1
)


candidates["Runway_Score"] = (
    candidates["Runway_Months_2024"] / 24
).clip(0, 1)

candidates["Headcount_Resilience"] = (
    candidates["Current_Headcount_2026"] /
    candidates["Peak_Headcount_2023"].replace(0, np.nan)
).clip(0, 1).fillna(0)

candidates["Layoff_Rate"] = (
    candidates["Layoffs_2024_2025"] /
    candidates["Peak_Headcount_2023"].replace(0, np.nan)
).clip(0, 1).fillna(0)

candidates["Layoff_Score"] = (
    1 - candidates["Layoff_Rate"]
)


ai_scores = {
    "None": 0.00,
    "Low": 0.33,
    "Medium": 0.67,
    "High": 1.00
}

candidates["AI_Score"] = (
    candidates["AI_Adoption_Level"]
    .map(ai_scores)
    .fillna(0.5)
)


def minmax_score(series):
    lower = series.quantile(0.05)
    upper = series.quantile(0.95)

    if upper <= lower:
        return pd.Series(
            0.5,
            index=series.index
        )

    score = (
        (series.clip(lower, upper) - lower) /
        (upper - lower)
    )

    return score.clip(0, 1)

candidates["Valuation_Score"] = minmax_score(
    candidates["Valuation_Upside"]
)


candidates["Investment_Score"] = (
    0.45 * candidates["Valuation_Score"] +
    0.25 * candidates["Runway_Score"] +
    0.15 * candidates["Headcount_Resilience"] +
    0.10 * candidates["AI_Score"] +
    0.05 * candidates["Layoff_Score"]
)


investable = candidates[
    (candidates["Runway_Months_2024"] >= 6) &
    (candidates["Current_Headcount_2026"] > 0) &
    (candidates["Investment_Score"] > 0)
].copy()


# 排除 runway 太短的公司
investable = investable[
    investable["Runway_Months_2024"] >= 6
]

# 排除大规模裁员公司
investable = investable[
    investable["Layoff_Rate"] <= 0.50
]


capital = 100_000
cash_weight = 0.10
max_position = 0.25

selected = (
    investable
    .sort_values("Investment_Score", ascending=False)
    .head(10)
    .copy()
)

# 只使用正分数
selected["Raw_Weight"] = (
    selected["Investment_Score"].clip(lower=0.01)
)

# 分配剩余的 90% 资本
selected["Weight"] = (
    selected["Raw_Weight"] /
    selected["Raw_Weight"].sum()
) * (1 - cash_weight)

# 限制单家公司最大仓位
selected["Weight"] = selected["Weight"].clip(
    upper=max_position
)

selected["Allocation_USD"] = (
    selected["Weight"] * capital
)

portfolio = selected[
    [
        "Company_ID",
        "Domain",
        "Funding_Stage",
        "Revenue_ARR_Millions",
        "Valuation_USD_Millions",
        "Base_Fair_Value",
        "Valuation_Upside",
        "Investment_Score",
        "Weight",
        "Allocation_USD"
    ]
].copy()

cash_row = pd.DataFrame([{
    "Company_ID": "CASH",
    "Domain": "Cash Reserve",
    "Funding_Stage": "",
    "Revenue_ARR_Millions": np.nan,
    "Valuation_USD_Millions": np.nan,
    "Base_Fair_Value": np.nan,
    "Valuation_Upside": np.nan,
    "Investment_Score": np.nan,
    "Weight": cash_weight,
    "Allocation_USD": capital * cash_weight
}])

portfolio = pd.concat(
    [portfolio, cash_row],
    ignore_index=True
)

print(portfolio)