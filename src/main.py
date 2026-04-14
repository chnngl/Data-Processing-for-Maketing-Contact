from pathlib import Path
import pandas as pd

from cleaning import inspect_data, clean_dataset

RAW_PATH = Path("data/raw/linkedin_raw_data.csv")
OUTPUT_PATH = Path("data/output/cleaned_data_without_ranking.csv")
REVIEW_PATH = Path("data/output/cleaning_review.csv")

def inspect_data(df: pd.DataFrame) -> None:
    print("---SHAPE---")
    print(df.shape)
    print()

    print("---COLUMN TYPES---")
    print(df.dtypes)
    print()

    print("---MISSING VALUES---")
    print(df.isna().sum())
    print()

    print("---SAMPLE ROWS---")
    print(df.head(10).to_string(index=False))
    print()

#missing values: name, company name, profile_url or email

def inspect_column(df: pd.DataFrame, col: str) -> None:
    series = df[col].dropna().astype(str).str.strip()
    print(f"\n---COLUMN: {col}---")

    print("First 10 values:")
    print(series.head(10).to_list())

    print("\nUnique sample values:")
    print(series.unique()[:15])

    print("\nTop value counts:")
    print(series.value_counts().head(10))

#summary of issued found:
#extra space, title, all capitalization, N/A or - in name column, linkedin ads also found
#mutiple values in headline, some with html entity &, irrelevant position like software engineer, pronouns attached, extra info after -
#inconsistent company name and incomplete profile url
#phone number as email, personal email exists
#duplicate names, emails, or profile urls

def main() -> None:
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 60)

    df = pd.read_csv(RAW_PATH)
    inspect_data(df)

    cleaned_df = clean_dataset(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(OUTPUT_PATH, index=False)

    #for col in ["raw_name", "headline", "company_name", "email", "profile_url"]:
    #   inspect_column(df, col)

    print()
    print("=== CLEANING SUMMARY ===")
    print(f"Raw rows loaded: {len(df)}")
    print(f"Rows after cleaning: {len(cleaned_df)}")
    print(f"Saved file to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()