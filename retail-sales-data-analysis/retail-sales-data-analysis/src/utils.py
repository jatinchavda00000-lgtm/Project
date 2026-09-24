# ============================================
# Retail Sales Data Analysis
# File: src/utils.py
# Purpose: Common helper functions used across the project
# ============================================

"""
Ye file project ke saare helper/utility functions rakhti hai.
Koi API nahi. Sirf reusable code.

Utility Functions:
- ensure_dir()             : Folder create karna (agar nahi hai)
- file_exists()            : File check
- get_timestamp()          : Current timestamp string
- print_section()          : Sundar header print
- print_dict()             : Dictionary sundar tarike se print
- format_currency()        : Rs. format karna
- format_number()          : Comma separated number
- safe_divide()            : Division by zero se bachna
- human_readable_size()    : Bytes -> KB/MB/GB
- Timer (class)            : Code timing context manager
- timed()                  : Decorator for timing functions
- save_json()              : Dict -> JSON file
- load_json()              : JSON file -> Dict
- save_text()              : Text file save
- read_text()              : Text file read
- df_to_excel()            : Multiple DataFrames -> Excel (multi-sheet)
- list_files()             : Folder ke files list
- chunk_dataframe()        : DataFrame ko chunks me todna
- memory_usage()           : DataFrame ki memory
- df_summary_str()         : DataFrame ka short summary string
- safe_to_numeric()        : Column ko safely numeric banana
- clean_column_for_sql()   : Column name SQL-safe banana
- retry()                  : Function ko retry karna on exception
"""

import functools
import json
import logging
import os
import shutil
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator

import numpy as np
import pandas as pd


# ============================================
# LOGGER
# ============================================

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Standard logger banata hai.

    Args:
        name: logger name (usually __name__)
        level: logging level

    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = get_logger(__name__)


# ============================================
# 1. FILE / FOLDER HELPERS
# ============================================

def ensure_dir(path: Path | str) -> Path:
    """
    Folder create karta hai agar exist nahi karta.

    Args:
        path: folder path

    Returns:
        Path object
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def file_exists(path: Path | str) -> bool:
    """File exist karti hai ya nahi."""
    return Path(path).is_file()


def list_files(
    folder: Path | str,
    pattern: str = "*",
    recursive: bool = False,
) -> list:
    """
    Folder ke files list karta hai.

    Args:
        folder: folder path
        pattern: glob pattern (e.g., '*.csv')
        recursive: subfolders me bhi dhundhna

    Returns:
        list of Path objects
    """
    folder = Path(folder)
    if not folder.exists():
        return []
    if recursive:
        return sorted(folder.rglob(pattern))
    return sorted(folder.glob(pattern))


def delete_file(path: Path | str) -> bool:
    """File delete karta hai (agar exist karti hai)."""
    p = Path(path)
    if p.exists() and p.is_file():
        p.unlink()
        return True
    return False


def copy_file(src: Path | str, dst: Path | str) -> Path:
    """File ko ek jagah se doosri jagah copy karta hai."""
    src = Path(src)
    dst = Path(dst)
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return dst


# ============================================
# 2. TIME / TIMESTAMP
# ============================================

def get_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """Current timestamp string return karta hai."""
    return datetime.now().strftime(fmt)


def get_date_str(fmt: str = "%Y-%m-%d") -> str:
    """Current date string."""
    return datetime.now().strftime(fmt)


class Timer:
    """
    Context manager - code block ka time measure karta hai.

    Usage:
        with Timer("Data load"):
            df = load_csv(...)
    """

    def __init__(self, label: str = "Task", log: bool = True):
        self.label = label
        self.log = log
        self.start_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start_time
        if self.log:
            logger.info(f"[{self.label}] took {self.elapsed:.3f}s")
        return False


def timed(func: Callable) -> Callable:
    """
    Decorator - function ka execution time log karta hai.

    Usage:
        @timed
        def my_function():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__}() took {elapsed:.3f}s")
        return result
    return wrapper


# ============================================
# 3. PRINT HELPERS
# ============================================

def print_section(title: str, width: int = 70, char: str = "=") -> None:
    """Sundar section header print karta hai."""
    print(char * width)
    print(title.center(width))
    print(char * width)


def print_dict(data: dict, indent: int = 2, title: str | None = None) -> None:
    """Dictionary ko sundar tarike se print karta hai."""
    if title:
        print_section(title)
    pad = " " * indent
    for key, value in data.items():
        if isinstance(value, float):
            print(f"{pad}{key:<25}: {value:,.2f}")
        elif isinstance(value, int):
            print(f"{pad}{key:<25}: {value:,}")
        else:
            print(f"{pad}{key:<25}: {value}")


def print_dataframe(df: pd.DataFrame, title: str | None = None, rows: int = 10) -> None:
    """DataFrame ko sundar tarike se print karta hai."""
    if title:
        print_section(title)
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print()
    print(df.head(rows).to_string())
    print()


# ============================================
# 4. FORMATTING HELPERS
# ============================================

def format_currency(value: float, symbol: str = "Rs.") -> str:
    """Number ko currency format me dikhata hai."""
    try:
        return f"{symbol} {value:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol} 0.00"


def format_number(value: float, decimals: int = 2) -> str:
    """Number ko comma-separated format me dikhata hai."""
    try:
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "0"


def format_percent(value: float, decimals: int = 2) -> str:
    """Number ko percentage format me dikhata hai."""
    try:
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def human_readable_size(num_bytes: float) -> str:
    """Bytes ko KB / MB / GB me convert karta hai."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


# ============================================
# 5. MATH HELPERS
# ============================================

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Division by zero se safe."""
    try:
        if b == 0 or pd.isna(b):
            return default
        return a / b
    except (TypeError, ValueError):
        return default


def safe_to_numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    """
    Safely converts a Series to numeric values.
    Removes Rs., $, commas, spaces, and % symbols.
    Invalid values are replaced with the default value.
    """
    s = series.copy()
    s = s.astype(str).str.strip()
    s = s.str.replace(r"(?i)rs\.?", "", regex=True)
    s = s.str.replace(r"[$,\s]", "", regex=True)
    s = s.str.replace("%", "", regex=False)

    result = pd.to_numeric(s, errors="coerce")
    return result.fillna(default).astype(float)

def percent_change(old: float, new: float) -> float:
    """Percentage change calculate karta hai."""
    if old == 0:
        return 0.0
    return ((new - old) / abs(old)) * 100


# ============================================
# 6. JSON / TEXT FILE HELPERS
# ============================================

def save_json(data: dict | list, path: Path | str, indent: int = 2) -> Path:
    """Dict/List ko JSON file me save karta hai."""
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
    logger.info(f"JSON saved: {path}")
    return path


def load_json(path: Path | str) -> dict | list:
    """JSON file load karta hai."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_text(text: str, path: Path | str) -> Path:
    """Text file save karta hai."""
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    logger.info(f"Text saved: {path}")
    return path


def read_text(path: Path | str) -> str:
    """Text file read karta hai."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================
# 7. EXCEL HELPERS
# ============================================

def df_to_excel(
    sheets: dict[str, pd.DataFrame],
    path: Path | str,
    index: bool = False,
) -> Path:
    """
    Multiple DataFrames ko ek Excel file me multi-sheet save karta hai.

    Args:
        sheets: {'SheetName': DataFrame, ...}
        path: output .xlsx path
        index: index save karna hai ya nahi

    Returns:
        Path
    """
    path = Path(path)
    ensure_dir(path.parent)

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_name, index=index)

            worksheet = writer.sheets[safe_name]
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max() if len(df) else 0,
                    len(str(col)),
                ) + 2
                worksheet.set_column(i, i, min(max_len, 40))

    logger.info(f"Excel saved: {path} ({len(sheets)} sheets)")
    return path


# ============================================
# 8. DATAFRAME HELPERS
# ============================================

def memory_usage(df: pd.DataFrame) -> str:
    """DataFrame ki memory usage return karta hai."""
    mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    return human_readable_size(mb * 1024 * 1024)


def df_summary_str(df: pd.DataFrame, name: str = "DataFrame") -> str:
    """DataFrame ka short summary string."""
    return (
        f"{name}: {df.shape[0]:,} rows x {df.shape[1]} cols | "
        f"Missing: {int(df.isnull().sum().sum())} | "
        f"Duplicates: {int(df.duplicated().sum())} | "
        f"Memory: {memory_usage(df)}"
    )


def chunk_dataframe(
    df: pd.DataFrame,
    chunk_size: int = 1000,
) -> Iterator[pd.DataFrame]:
    """
    DataFrame ko chunks me todta hai (bade data ke liye).

    Yields:
        pd.DataFrame chunks
    """
    total = len(df)
    for start in range(0, total, chunk_size):
        yield df.iloc[start:start + chunk_size]


def clean_column_for_sql(name: str) -> str:
    """Column name ko SQL-safe banata hai."""
    clean = str(name).strip()
    clean = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in clean)
    if clean and clean[0].isdigit():
        clean = "col_" + clean
    return clean


def get_numeric_columns(df: pd.DataFrame) -> list:
    """DataFrame ke numeric columns list karta hai."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> list:
    """DataFrame ke categorical columns list karta hai."""
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


# ============================================
# 9. RETRY HELPER
# ============================================

def retry(
    times: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator - function ko multiple times try karta hai on exception.

    Usage:
        @retry(times=3, delay=1)
        def unstable_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{times} failed: {e}"
                    )
                    if attempt < times:
                        time.sleep(delay)
            logger.error(f"{func.__name__} failed after {times} attempts.")
            raise last_exc
        return wrapper
    return decorator


# ============================================
# 10. CONTEXT MANAGERS
# ============================================

@contextmanager
def suppress_stdout():
    """stdout suppress karta hai (verbose libraries ke liye)."""
    import sys
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout


# ============================================
# 11. MAIN (self-test)
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("UTILS - SELF TEST")
    print("=" * 70)

    # --- Test 1: get_timestamp ---
    print("\n[TEST 1] get_timestamp()")
    ts = get_timestamp()
    print(f"  Timestamp: {ts}")
    assert len(ts) == 15

    # --- Test 2: ensure_dir + file_exists ---
    print("\n[TEST 2] ensure_dir() / file_exists()")
    test_dir = ensure_dir("output/_utils_test")
    print(f"  Created: {test_dir} | Exists: {test_dir.exists()}")

    # --- Test 3: format helpers ---
    print("\n[TEST 3] format_currency / format_number / format_percent")
    print(f"  Currency: {format_currency(1234567.89)}")
    print(f"  Number:   {format_number(1234567.89)}")
    print(f"  Percent:  {format_percent(45.678)}")

    # --- Test 4: human_readable_size ---
    print("\n[TEST 4] human_readable_size()")
    print(f"  1024 bytes       -> {human_readable_size(1024)}")
    print(f"  1048576 bytes    -> {human_readable_size(1048576)}")
    print(f"  1073741824 bytes -> {human_readable_size(1073741824)}")

    # --- Test 5: safe_divide ---
    print("\n[TEST 5] safe_divide()")
    print(f"  10 / 2  = {safe_divide(10, 2)}")
    print(f"  10 / 0  = {safe_divide(10, 0)}")
    print(f"  10 / nan= {safe_divide(10, float('nan'))}")

    # --- Test 6: percent_change ---
    print("\n[TEST 6] percent_change()")
    print(f"  100 -> 150 : {percent_change(100, 150):.2f}%")
    print(f"  150 -> 100 : {percent_change(150, 100):.2f}%")

    # --- Test 7: Timer ---
    print("\n[TEST 7] Timer context manager")
    with Timer("Sleep 0.1s", log=True) as t:
        time.sleep(0.1)
    print(f"  Elapsed: {t.elapsed:.3f}s")

    # --- Test 8: timed decorator ---
    print("\n[TEST 8] timed() decorator")

    @timed
    def dummy_task():
        time.sleep(0.05)
        return "done"

    result = dummy_task()
    print(f"  Result: {result}")

    # --- Test 9: JSON save/load ---
    print("\n[TEST 9] save_json / load_json")
    test_json = Path("output/_utils_test/test.json")
    data = {"name": "Retail", "rows": 1000, "profit": 12345.67}
    save_json(data, test_json)
    loaded = load_json(test_json)
    print(f"  Loaded: {loaded}")
    assert loaded["name"] == "Retail"

    # --- Test 10: save_text / read_text ---
    print("\n[TEST 10] save_text / read_text")
    test_txt = Path("output/_utils_test/test.txt")
    save_text("Hello, Retail Sales!", test_txt)
    content = read_text(test_txt)
    print(f"  Content: {content}")

    # --- Test 11: DataFrame summary ---
    print("\n[TEST 11] df_summary_str / memory_usage")
    sample_df = pd.DataFrame({
        "A": range(100),
        "B": np.random.rand(100),
        "C": ["x"] * 100,
    })
    print(f"  {df_summary_str(sample_df, 'Sample')}")

    # --- Test 12: chunk_dataframe ---
    print("\n[TEST 12] chunk_dataframe()")
    chunks = list(chunk_dataframe(sample_df, chunk_size=30))
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Sizes: {[len(c) for c in chunks]}")

    # --- Test 13: safe_to_numeric ---
    print("\n[TEST 13] safe_to_numeric()")
    messy = pd.Series(["Rs.1,200", "Rs.3,400", "invalid", "500"])
    clean = safe_to_numeric(messy)
    print(f"  Original: {list(messy)}")
    print(f"  Cleaned:  {list(clean)}")

    # --- Test 14: clean_column_for_sql ---
    print("\n[TEST 14] clean_column_for_sql()")
    names = ["Order ID", "Total-Sales", "2024 Profit", "Category@Type"]
    for n in names:
        print(f"  '{n}' -> '{clean_column_for_sql(n)}'")

    # --- Test 15: df_to_excel ---
    print("\n[TEST 15] df_to_excel()")
    sheets = {
        "Sales": sample_df.head(10),
        "Summary": pd.DataFrame({"Metric": ["Total"], "Value": [1000]}),
    }
    xlsx_path = df_to_excel(sheets, "output/_utils_test/multi.xlsx")
    print(f"  Excel saved: {xlsx_path}")

    # --- Test 16: list_files ---
    print("\n[TEST 16] list_files()")
    files = list_files("output/_utils_test", pattern="*")
    print(f"  Files found: {len(files)}")
    for f in files:
        print(f"    - {f.name}")

    # --- Test 17: print_section / print_dict ---
    print("\n[TEST 17] print_section / print_dict")
    print_section("DEMO SECTION")
    print_dict({"Sales": 1234567.89, "Profit": 45678.12, "Orders": 500})

    # --- Cleanup ---
    print("\n[CLEANUP] Removing test files...")
    shutil.rmtree("output/_utils_test", ignore_errors=True)
    print("  Done.")

    print("\n" + "=" * 70)
    print("[OK] utils.py - All tests passed.")
    print("=" * 70)