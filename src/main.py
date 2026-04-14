from pathlib import Path
import pandas as pd

from cleaning import inspect_data, clean_dataset
from classification import select_best_contacts

RAW_PATH = Path("data/raw/linkedin_raw_data.csv")
PROCESSED_PATH = Path("data/output/cleaned_data_without_classification.csv")
FINAL_PATH = Path("data/output/marketing_contacts_clean.csv")

def main() -> None:
    df = pd.read_csv(RAW_PATH)
    inspect_data(df)

    cleaned_df = clean_dataset(df)
    preview_df = cleaned_df.sort_values("source_row_id")[
        ["contact_name", "job_title", "company_name", "linkedin_url", "email"]
    ].copy()

    final_df = select_best_contacts(cleaned_df)

    FINAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    preview_df.to_csv(PROCESSED_PATH, index=False)
    final_df.to_csv(FINAL_PATH, index=False)

    print("---SUMMARY---")
    print(f"Raw rows loaded: {len(df)}")
    print(f"Rows after cleaning: {len(cleaned_df)}")
    print(f"Rows in final output: {len(final_df)}")
    print(f"Saved cleaned file without classification to: {PROCESSED_PATH}")
    print(f"Saved final output to: {FINAL_PATH}")

if __name__ == "__main__":
    main()