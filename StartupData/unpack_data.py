import os
import zipfile
import pandas as pd

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HACKATHON_DIR = os.path.dirname(BASE_DIR)
OLD_DATA_DIR = os.path.join(HACKATHON_DIR, "old_kaggle_csv")
ZIP_PATH = os.path.join(OLD_DATA_DIR, "archive (6).zip")
RAW_OUTPUT_CSV = os.path.join(OLD_DATA_DIR, "global_tech_startups_2026.csv")
ENRICHED_OUTPUT_CSV = os.path.join(OLD_DATA_DIR, "global_tech_startups_with_sectors.csv")

# Sector mapping definitions
DOMAIN_TO_BROAD_SECTOR = {
    "Generative AI": "Information Technology",
    "Cybersecurity": "Information Technology",
    "FinTech": "Financial Services",
    "Web3/Crypto": "Financial Services",
    "HealthTech": "Healthcare & Life Sciences",
    "ClimateTech": "CleanTech & Energy",
    "Robotics": "Industrials & Automation",
    "SpaceTech": "Aerospace & Defense",
    "Autonomous Vehicles": "Transportation & Mobility",
    "EdTech": "Education",
}

DOMAIN_TO_SECTOR_NAME = {
    "Generative AI": "Generative AI & Machine Learning",
    "Cybersecurity": "Cybersecurity & InfoSec",
    "FinTech": "Financial Technology (FinTech)",
    "Web3/Crypto": "Blockchain & Web3",
    "HealthTech": "HealthTech & Digital Health",
    "ClimateTech": "ClimateTech & Sustainability",
    "Robotics": "Robotics & Hardware Automation",
    "SpaceTech": "Aerospace & DeepTech",
    "Autonomous Vehicles": "Autonomous Mobility & Systems",
    "EdTech": "Education Technology (EdTech)",
}

def unpack_and_enrich():
    print(f"Reading {ZIP_PATH}...")
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Archive not found: {ZIP_PATH}")

    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        csv_filename = [name for name in z.namelist() if name.endswith('.csv')][0]
        print(f"Extracting {csv_filename}...")
        
        # Save raw CSV
        z.extract(csv_filename, path=BASE_DIR)
        print(f"Raw file saved to: {RAW_OUTPUT_CSV}")

        # Read into dataframe
        with z.open(csv_filename) as f:
            df = pd.read_csv(f)

    print(f"Initial shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Add broad sector and sector description
    df["Sector"] = df["Domain"].map(DOMAIN_TO_SECTOR_NAME).fillna("Other")
    df["Broad_Sector"] = df["Domain"].map(DOMAIN_TO_BROAD_SECTOR).fillna("Other")

    # Add one-hot binary indicator columns for each domain/sector
    unique_domains = sorted(df["Domain"].dropna().unique())
    for domain in unique_domains:
        # Create a clean column name like sector_fintech, sector_generative_ai
        col_slug = "sector_" + domain.lower().replace(" ", "_").replace("/", "_")
        df[col_slug] = (df["Domain"] == domain).astype(int)

    # Reorder columns: keep identifiers and sectors together
    core_cols = [
        "Company_ID",
        "Domain",
        "Sector",
        "Broad_Sector",
        "Founding_Year",
        "Country",
        "City",
        "Funding_Stage",
        "Total_Funding_USD_Millions",
        "Valuation_USD_Millions",
        "Revenue_ARR_Millions",
        "Monthly_Burn_Rate_Millions",
        "Runway_Months_2024",
        "Peak_Headcount_2023",
        "Layoffs_2024_2025",
        "Current_Headcount_2026",
        "Investor_Tier",
        "AI_Adoption_Level",
        "Acquisition_Status",
    ]
    
    indicator_cols = [
        col for col in df.columns if col.startswith("sector_")
    ]
    
    ordered_cols = core_cols + indicator_cols
    df = df[ordered_cols]

    print(f"Enriched shape: {df.shape}")
    print(f"Total columns: {len(df.columns)}")

    # Save to enriched CSV
    df.to_csv(ENRICHED_OUTPUT_CSV, index=False)
    print(f"Successfully created enriched CSV: {ENRICHED_OUTPUT_CSV}")

    # Summary
    print("\n--- Sector Distribution ---")
    print(df["Broad_Sector"].value_counts())
    print("\n--- First 3 Rows ---")
    print(df[["Company_ID", "Domain", "Sector", "Broad_Sector"] + indicator_cols[:3]].head(3))

if __name__ == "__main__":
    unpack_and_enrich()
