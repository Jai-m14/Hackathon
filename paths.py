"""Every file and folder path VentureLens uses, defined in one place.

Paths are absolute and built from this file's location, so scripts work no matter
which folder they are run from. Import from anywhere in the repo:

    import paths
    df = pd.read_csv(paths.PORTFOLIO_CSV)

Scripts in pipeline/ put the repo root on sys.path first so ``import paths`` works.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Config
ENV_FILE = ROOT / ".env"  # API keys; git-ignored (copy .env.example)

# Folders
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"  # source datasets used by the pipeline
ARCHIVE_DIR = DATA_DIR / "archive"  # retired Kaggle data, kept for reference
OUTPUTS_DIR = ROOT / "outputs"  # every generated file
TEST_RUNS_DIR = OUTPUTS_DIR / "test_runs"  # small --limit runs kept for reference
DOCS_DIR = ROOT / "docs"
FIXTURES_DIR = ROOT / "tests" / "fixtures"  # sample inputs for quick runs
CACHE_DIR = ROOT / "cache"  # git-ignored API response caches
LLM_CACHE_DIR = CACHE_DIR / "llm_matching"
FINNHUB_CACHE_DIR = CACHE_DIR / "finnhub"

# Raw inputs
STARTUPS_CSV = RAW_DIR / "Startups.csv"
FOUNDERS_CSV = RAW_DIR / "Founders.csv"

# Outputs, in pipeline order
# 1. pipeline/score_startups.py
PORTFOLIO_CSV = OUTPUTS_DIR / "venturelens_portfolio_output.csv"  # selected startups + weights
SCORED_CSV = OUTPUTS_DIR / "venturelens_scored_companies.csv"  # every startup with scores
SELECTED_COMPANIES_CSV = OUTPUTS_DIR / "selected_companies.csv"  # portfolio in sentiment schema
# 2. pipeline/match_comparables.py
MATCHES_CSV = OUTPUTS_DIR / "venturelens_matches.csv"  # 3 public comparables per startup
# 3. pipeline/fetch_finnhub.py
COMPARABLE_DATA_JSON = OUTPUTS_DIR / "venturelens_comparable_data.json"  # full data; charts.py reads this
COMPARABLES_SUMMARY_CSV = OUTPUTS_DIR / "venturelens_comparables_summary.csv"  # one row per startup
# 4. pipeline/analyze_sentiment.py (default output is <input>_sentiment.csv)
PORTFOLIO_SENTIMENT_CSV = OUTPUTS_DIR / "venturelens_portfolio_output_sentiment.csv"

# Fixtures
SAMPLE_MATCHES_CSV = FIXTURES_DIR / "sample_matches.csv"
