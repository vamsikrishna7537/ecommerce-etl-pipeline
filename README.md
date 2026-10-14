# E-commerce ETL Pipeline with Python and Pandas

A beginner-friendly ETL project that reads multiple CSV files, combines them, standardizes messy data, validates rows, removes exact duplicates, calculates revenue, and saves the results.

## Skills demonstrated

- Extract data from multiple CSV files
- Combine data with Pandas
- Clean text and convert data types
- Validate quantities, prices, dates, product names, IDs, and status
- Keep rejected rows with reasons
- Detect and remove exact duplicate rows
- Calculate order revenue
- Save processed data and a summary report

## Tech stack

- Python 3.11+
- Pandas

## Project structure

```text
ecommerce-etl-pipeline/
├── data/
│   ├── raw/
│   │   ├── orders_day1.csv
│   │   ├── orders_day2.csv
│   │   └── orders_day3.csv
│   └── processed/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ETL Workflow

```text
Raw CSV Files
     |
     v
Extract and Combine
     |
     v
Standardize and Validate
     |
     v
Separate Invalid Records
     |
     v
Remove Exact Duplicates
     |
     v
Calculate Revenue
     |
     v
Save Processed Outputs

## Run the project

1. Install Python 3.11 or newer.
2. Open this folder in PyCharm or a terminal.
3. Create and activate a virtual environment (recommended):

   Windows:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```

   macOS/Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

4. Install the dependency:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the pipeline:
   ```bash
   python main.py
   ```

The script reads all `.csv` files in `data/raw/`. It uses paths relative to `main.py`, so it can run from another working directory too.

## Input columns

Each input CSV must contain: `order_id`, `customer_id`, `product`, `quantity`, `unit_price`, `order_date`, and `status`.

Allowed statuses are `completed`, `cancelled`, and `pending`.

## Data quality rules

A row is rejected when quantity or unit price is missing, non-numeric, zero, or negative; the date is invalid; product/order/customer ID is blank; or status is not allowed. Rejected records include a `rejection_reason` field. Exact duplicate rows among valid rows are written separately, and the first occurrence is retained.

## Generated output files

Files are written to `data/processed/`:

- `cleaned_orders.csv` — clean unique records plus calculated `revenue`
- `rejected_orders.csv` — records that failed validation and the reason
- `duplicate_orders.csv` — extra exact duplicate occurrences removed
- `summary.txt` — row counts and revenue totals

Revenue is calculated as `quantity * unit_price`. The summary includes revenue across all clean orders and revenue from completed orders only.

## GitHub tips

- Keep sample input CSVs in `data/raw/`.
- Generated outputs are ignored by Git by default.
- Do not commit `.venv`, passwords, API keys, or private datasets.

## Future improvements

- Add unit tests with `pytest`
- Add structured logging
- Load the clean data into PostgreSQL
- Schedule the pipeline
