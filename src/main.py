from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/linkedin_raw_data.csv")

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

#extra space, title, or all capitalization in name column
#mutiple values in headline, some with html entity &, irrelevant position like software engineer
#phone number as email
#incomplete profile url
#duplicate names, emails, profile urls


def check_duplicate_urls(df: pd.DataFrame) -> None:
    print("---DUPLICATE PROFILE URLS---")
    dupes = df[df["profile_url"].notna() & df["profile_url"].duplicated(keep=False)]
    print(dupes[["raw_name", "company_name", "headline", "email", "profile_url", "scraped_at"]]
          .sort_values("profile_url")
          .to_string(index=False))
    print()

def check_duplicate_name_company(df: pd.DataFrame) -> None:
    print("---DUPLICATE NAME at SAME COMPANY---")
    temp = df.copy()

    #remove extra space and turn to lowercase
    temp["raw_name_clean"] = temp["raw_name"].astype(str).str.strip().str.lower()
    temp["company_name_clean"] = temp["company_name"].astype(str).str.strip().str.lower()

    #show all rows where the same cleaned name and company appears more than once
    dupes = temp[temp.duplicated(subset=["raw_name_clean", "company_name_clean"], keep=False)]
    print(dupes[["raw_name", "company_name", "headline", "email", "profile_url", "scraped_at"]]
          .sort_values(["raw_name", "company_name", "scraped_at"])
          .to_string(index=False))
    print()

def main() -> None:
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 60)

    df = pd.read_csv(RAW_PATH)
    inspect_data(df)
    for col in ["raw_name", "headline", "company_name", "email", "profile_url"]:
        inspect_column(df, col)

    check_duplicate_urls(df)
    check_duplicate_name_company(df)

if __name__ == "__main__":
    main()