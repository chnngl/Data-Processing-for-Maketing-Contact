from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/linkedin_raw_data.csv")

def inspect_data(df: pd.DataFrame) -> None:
    print("=== SHAPE ===")
    print(df.shape)
    print()

    print("=== COLUMN TYPES ===")
    print(df.dtypes)
    print()

    print("=== MISSING VALUES ===")
    print(df.isna().sum())
    print()

    print("=== SAMPLE ROWS ===")
    print(df.head(10).to_string(index=False))
    print()

def main() -> None:
    df = pd.read_csv(RAW_PATH)
    inspect_data(df)

if __name__ == "__main__":
    main()