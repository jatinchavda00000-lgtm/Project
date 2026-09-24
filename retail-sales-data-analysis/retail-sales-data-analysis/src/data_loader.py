# ============================================
# Retail Sales Data Analysis
# File: src/data_loader.py
# Purpose: Load data from CSV, Excel, SQL (no API)
# ============================================

"""
This file contains all data loading functions.
Data source is only CSV / Excel / SQL dump - no API.

Functions:
- load_csv()          : Load CSV file
- load_excel()        : Load Excel file
- load_from_sql()     : Load from SQL database
- save_to_csv()       : Save DataFrame to CSV
- save_to_sql()       : Save DataFrame to SQL table
- get_data_info()     : Print summary of data
- preview_data()      : View head/tail of data
"""

import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path

from config import (
    RAW_DATA_FILE,
    CLEAN_DATA_FILE,
    ACTIVE_DB_CONNECTION,
    TABLE_NAME,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_LEVEL,
)

# ============================================
# LOGGING SETUP
# ============================================

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


# ============================================
# 1. LOAD CSV
# ============================================

def load_csv(file_path: Path | str = RAW_DATA_FILE) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame.

    Args:
        file_path: Path to the CSV file

    Returns:
        pd.DataFrame: Loaded data

    Raises:
        FileNotFoundError: if file does not exist
        pd.errors.EmptyDataError: if file is empty
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"CSV file not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
        logger.info(f"CSV loaded: {file_path.name} | Shape: {df.shape}")
        return df
    except pd.errors.EmptyDataError:
        logger.error(f"CSV file is empty: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error while loading CSV: {e}")
        raise


# ============================================
# 2. LOAD EXCEL
# ============================================

def load_excel(
    file_path: Path | str,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    """
    Loads an Excel file into a DataFrame.

    Args:
        file_path: Path to the Excel file (.xlsx / .xls)
        sheet_name: Sheet name or index (default 0 = first sheet)

    Returns:
        pd.DataFrame: Loaded data
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"Excel file not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info(
            f"Excel loaded: {file_path.name} | "
            f"Sheet: {sheet_name} | Shape: {df.shape}"
        )
        return df
    except Exception as e:
        logger.error(f"Error while loading Excel: {e}")
        raise


# ============================================
# 3. LOAD FROM SQL
# ============================================

def load_from_sql(
    query: str,
    connection_string: str = ACTIVE_DB_CONNECTION,
) -> pd.DataFrame:
    """
    Loads data from a SQL database.

    Args:
        query: SQL SELECT query
        connection_string: DB connection string
            (default: SQLite from config)

    Returns:
        pd.DataFrame: Query result
    """
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        logger.info(f"SQL query executed | Rows returned: {len(df)}")
        return df
    except SQLAlchemyError as e:
        logger.error(f"SQL error: {e}")
        raise
    except Exception as e:
        logger.error(f"SQL load error: {e}")
        raise


# ============================================
# 4. SAVE TO CSV
# ============================================

def save_to_csv(
    df: pd.DataFrame,
    file_path: Path | str,
    index: bool = False,
) -> None:
    """
    Saves a DataFrame to a CSV file.

    Args:
        df: DataFrame
        file_path: output CSV path
        index: whether to save the index column
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_csv(file_path, index=index)
        logger.info(f"CSV saved: {file_path} | Shape: {df.shape}")
    except Exception as e:
        logger.error(f"CSV save error: {e}")
        raise


# ============================================
# 5. SAVE TO SQL
# ============================================

def save_to_sql(
    df: pd.DataFrame,
    table_name: str = TABLE_NAME,
    connection_string: str = ACTIVE_DB_CONNECTION,
    if_exists: str = "replace",
) -> None:
    """
    Saves a DataFrame to a SQL table.

    Args:
        df: DataFrame
        table_name: target table name
        connection_string: DB connection string
        if_exists: 'replace' | 'append' | 'fail'
    """
    try:
        engine = create_engine(connection_string)
        df.to_sql(
            table_name,
            engine,
            if_exists=if_exists,
            index=False,
        )
        logger.info(
            f"SQL table saved: {table_name} | Rows: {len(df)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"SQL save error: {e}")
        raise


# ============================================
# 6. GET DATA INFO
# ============================================

def get_data_info(df: pd.DataFrame, name: str = "DataFrame") -> dict:
    """
    Returns a basic summary of the data.

    Args:
        df: DataFrame
        name: label for logging

    Returns:
        dict with shape, columns, dtypes, missing counts, memory
    """
    info = {
        "name": name,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "total_missing": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / (1024 * 1024), 2
        ),
    }

    logger.info(
        f"{name} info | Rows: {info['rows']} | "
        f"Cols: {info['columns']} | "
        f"Missing: {info['total_missing']} | "
        f"Dupes: {info['duplicates']}"
    )
    return info


# ============================================
# 7. PREVIEW DATA
# ============================================

def preview_data(
    df: pd.DataFrame,
    rows: int = 5,
    name: str = "DataFrame",
) -> None:
    """
    Prints the head, tail, and a random sample of the data.
    Useful for a quick check in the terminal.

    Args:
        df: DataFrame
        rows: number of rows to show
        name: label
    """
    print("=" * 70)
    print(f"PREVIEW: {name}")
    print("=" * 70)
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    print(f"\n--- HEAD ({rows} rows) ---")
    print(df.head(rows).to_string())

    print(f"\n--- TAIL ({rows} rows) ---")
    print(df.tail(rows).to_string())

    print(f"\n--- RANDOM SAMPLE ({rows} rows) ---")
    sample_size = min(rows, len(df))
    print(df.sample(sample_size, random_state=42).to_string())

    print("\n--- DTYPES ---")
    print(df.dtypes.to_string())

    print("\n--- MISSING VALUES ---")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) == 0:
        print("No missing values found.")
    else:
        print(missing.to_string())

    print("=" * 70)


# ============================================
# 8. LOAD CLEAN DATA (convenience)
# ============================================

def load_clean_data() -> pd.DataFrame:
    """Loads the processed clean CSV (for dashboard/analysis)."""
    if not Path(CLEAN_DATA_FILE).exists():
        logger.warning(
            f"Clean data not found: {CLEAN_DATA_FILE}. "
            f"Run data_cleaning.py first."
        )
        raise FileNotFoundError(
            f"Clean data file not found: {CLEAN_DATA_FILE}"
        )
    return load_csv(CLEAN_DATA_FILE)


# ============================================
# 9. MAIN (testing)
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DATA LOADER - SELF TEST")
    print("=" * 70)

    # Create a sample DataFrame for testing
    sample_df = pd.DataFrame(
        {
            "Order_ID": ["ORD001", "ORD002", "ORD003"],
            "Order_Date": ["2024-01-15", "2024-02-20", "2024-03-10"],
            "Product_Name": ["Chair", "Table", "Lamp"],
            "Sales": [1500.0, 2500.0, 800.0],
            "Profit": [300.0, 500.0, 120.0],
        }
    )

    print("\n[TEST 1] get_data_info()")
    info = get_data_info(sample_df, name="Sample")
    for k, v in info.items():
        print(f"  {k}: {v}")

    print("\n[TEST 2] save_to_csv()")
    test_path = Path("output") / "test_sample.csv"
    save_to_csv(sample_df, test_path)
    print(f"  Saved to: {test_path}")

    print("\n[TEST 3] load_csv()")
    loaded = load_csv(test_path)
    print(f"  Loaded shape: {loaded.shape}")

    print("\n[TEST 4] save_to_sql()")
    save_to_sql(sample_df, table_name="test_table", if_exists="replace")
    print("  Saved to SQLite: test_table")

    print("\n[TEST 5] load_from_sql()")
    result = load_from_sql("SELECT * FROM test_table")
    print(f"  Rows from SQL: {len(result)}")

    print("\n[TEST 6] preview_data()")
    preview_data(sample_df, rows=2, name="Sample")

    print("\n" + "=" * 70)
    print("[OK] data_loader.py - All tests passed.")
    print("=" * 70)