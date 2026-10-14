from pathlib import Path
import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parent
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw"
OUTPUT_FOLDER = PROJECT_FOLDER / "data" / "processed"


def load_csv_files():
    """Read all CSV files in data/raw and combine them."""
    csv_files = sorted(RAW_FOLDER.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_FOLDER}")

    dataframes = []
    for file in csv_files:
        print(f"Reading: {file.name}")
        dataframes.append(pd.read_csv(file))

    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"Total input rows: {len(combined_df)}")
    return combined_df


def standardize_data(df):
    """Trim text, convert numeric columns, and parse dates."""
    df = df.copy()
    required = [
        "order_id", "customer_id", "product", "quantity",
        "unit_price", "order_date", "status"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for col in ["order_id", "customer_id", "product", "status"]:
        df[col] = df[col].astype("string").str.strip()

    # Empty strings become missing values.
    for col in ["order_id", "customer_id", "product", "status"]:
        df[col] = df[col].replace("", pd.NA)

    df["status"] = df["status"].str.lower()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    return df


def validate_data(df):
    """Separate invalid rows and record why each row was rejected."""
    df = df.copy()

    checks = {
        "quantity is missing, non-numeric, or <= 0":
            df["quantity"].isna() | (df["quantity"] <= 0),
        "unit_price is missing, non-numeric, or <= 0":
            df["unit_price"].isna() | (df["unit_price"] <= 0),
        "order_date is invalid or missing":
            df["order_date"].isna(),
        "product is blank or missing":
            df["product"].isna(),
        "order_id is blank or missing":
            df["order_id"].isna(),
        "customer_id is blank or missing":
            df["customer_id"].isna(),
        "status is not completed, cancelled, or pending":
            ~df["status"].isin(["completed", "cancelled", "pending"]),
    }

    reasons = []
    invalid_mask = pd.Series(False, index=df.index)
    for reason, mask in checks.items():
        invalid_mask = invalid_mask | mask
    for index in df.index:
        row_reasons = [reason for reason, mask in checks.items() if mask.loc[index]]
        reasons.append("; ".join(row_reasons))

    df["rejection_reason"] = reasons
    rejected_df = df[invalid_mask].copy()
    valid_df = df[~invalid_mask].copy()
    return valid_df, rejected_df


def remove_duplicates(df):
    """Keep the first exact row and return extra duplicate occurrences."""
    duplicate_mask = df.duplicated(keep="first")
    duplicates_df = df[duplicate_mask].copy()
    clean_df = df[~duplicate_mask].copy()
    return clean_df, duplicates_df


def transform_data(df):
    """Calculate revenue for every clean order."""
    df = df.copy()
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df[
        [
            "order_id", "customer_id", "product", "quantity",
            "unit_price", "order_date", "status", "revenue"
        ]
    ]


def save_outputs(clean_df, rejected_df, duplicates_df, total_input_rows):
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    clean_df.to_csv(OUTPUT_FOLDER / "cleaned_orders.csv", index=False)
    rejected_df.to_csv(OUTPUT_FOLDER / "rejected_orders.csv", index=False)
    duplicates_df.to_csv(OUTPUT_FOLDER / "duplicate_orders.csv", index=False)

    all_revenue = clean_df["revenue"].sum()
    completed_revenue = clean_df.loc[
        clean_df["status"] == "completed", "revenue"
    ].sum()

    summary = (
        "ETL PIPELINE SUMMARY\n"
        "====================\n"
        f"Input rows: {total_input_rows}\n"
        f"Clean rows: {len(clean_df)}\n"
        f"Rejected rows: {len(rejected_df)}\n"
        f"Duplicate rows removed: {len(duplicates_df)}\n"
        f"Revenue across clean orders: {all_revenue:.2f}\n"
        f"Revenue from completed orders: {completed_revenue:.2f}\n"
    )
    (OUTPUT_FOLDER / "summary.txt").write_text(summary, encoding="utf-8")

    print("\nETL completed successfully!")
    print(f"Input rows: {total_input_rows}")
    print(f"Clean rows: {len(clean_df)}")
    print(f"Rejected rows: {len(rejected_df)}")
    print(f"Duplicate rows removed: {len(duplicates_df)}")
    print(f"Revenue across clean orders: {all_revenue:.2f}")
    print(f"Completed-order revenue: {completed_revenue:.2f}")
    print(f"Output folder: {OUTPUT_FOLDER}")


def main():
    combined_df = load_csv_files()
    total_input_rows = len(combined_df)

    standardized_df = standardize_data(combined_df)
    valid_df, rejected_df = validate_data(standardized_df)
    unique_df, duplicates_df = remove_duplicates(valid_df)
    clean_df = transform_data(unique_df)

    save_outputs(clean_df, rejected_df, duplicates_df, total_input_rows)


if __name__ == "__main__":
    main()
