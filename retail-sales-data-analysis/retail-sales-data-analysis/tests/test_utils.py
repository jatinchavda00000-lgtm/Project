# ============================================
# Retail Sales Data Analysis
# File: tests/test_utils.py
# Purpose: Unit tests for src/utils.py
# Framework: pytest
# ============================================

"""
Unit tests for the utils module.

Test coverage:
- get_logger()
- ensure_dir()
- file_exists()
- list_files()
- delete_file()
- copy_file()
- get_timestamp()
- get_date_str()
- Timer (context manager)
- timed (decorator)
- print_section()
- print_dict()
- print_dataframe()
- format_currency()
- format_number()
- format_percent()
- human_readable_size()
- safe_divide()
- safe_to_numeric()
- percent_change()
- save_json() / load_json()
- save_text() / read_text()
- df_to_excel()
- memory_usage()
- df_summary_str()
- chunk_dataframe()
- clean_column_for_sql()
- get_numeric_columns()
- get_categorical_columns()
- retry (decorator)
- suppress_stdout (context manager)

Run:
    pytest tests/test_utils.py -v
"""

import sys
import time
import warnings
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

warnings.filterwarnings("ignore")

# Make src/ importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils import (
    get_logger,
    ensure_dir,
    file_exists,
    list_files,
    delete_file,
    copy_file,
    get_timestamp,
    get_date_str,
    Timer,
    timed,
    print_section,
    print_dict,
    print_dataframe,
    format_currency,
    format_number,
    format_percent,
    human_readable_size,
    safe_divide,
    safe_to_numeric,
    percent_change,
    save_json,
    load_json,
    save_text,
    read_text,
    df_to_excel,
    memory_usage,
    df_summary_str,
    chunk_dataframe,
    clean_column_for_sql,
    get_numeric_columns,
    get_categorical_columns,
    retry,
    suppress_stdout,
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Small well-formed DataFrame for utility tests."""
    return pd.DataFrame({
        "Order_ID": [f"ORD{i:03d}" for i in range(10)],
        "Sales":    [100.0 * i for i in range(1, 11)],
        "Profit":   [10.0 * i for i in range(1, 11)],
        "Category": ["Furniture"] * 5 + ["Technology"] * 5,
        "Region":   ["North"] * 5 + ["South"] * 5,
    })


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """A temporary directory for file I/O tests."""
    d = tmp_path / "test_dir"
    d.mkdir()
    return d


# ============================================
# 1. get_logger()
# ============================================

class TestGetLogger:

    def test_returns_logger(self):
        logger = get_logger("test_logger_1")
        assert logger is not None
        assert logger.name == "test_logger_1"

    def test_same_logger_returned(self):
        a = get_logger("test_same")
        b = get_logger("test_same")
        assert a is b

    def test_has_handler(self):
        logger = get_logger("test_handler")
        assert len(logger.handlers) >= 1


# ============================================
# 2. ensure_dir()
# ============================================

class TestEnsureDir:

    def test_creates_new_dir(self, tmp_path):
        target = tmp_path / "new_folder"
        result = ensure_dir(target)
        assert target.exists()
        assert result == target

    def test_existing_dir_ok(self, tmp_path):
        target = tmp_path / "existing"
        target.mkdir()
        result = ensure_dir(target)
        assert target.exists()
        assert result == target

    def test_creates_nested_dirs(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"
        ensure_dir(target)
        assert target.exists()

    def test_accepts_string_path(self, tmp_path):
        target = str(tmp_path / "from_string")
        ensure_dir(target)
        assert Path(target).exists()


# ============================================
# 3. file_exists()
# ============================================

class TestFileExists:

    def test_existing_file(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("data")
        assert file_exists(f) is True

    def test_missing_file(self, tmp_path):
        f = tmp_path / "missing.txt"
        assert file_exists(f) is False

    def test_directory_not_file(self, tmp_path):
        d = tmp_path / "folder"
        d.mkdir()
        assert file_exists(d) is False


# ============================================
# 4. list_files()
# ============================================

class TestListFiles:

    def test_empty_folder(self, temp_dir):
        result = list_files(temp_dir)
        assert result == []

    def test_lists_matching_pattern(self, temp_dir):
        (temp_dir / "a.csv").write_text("x")
        (temp_dir / "b.csv").write_text("x")
        (temp_dir / "c.txt").write_text("x")
        result = list_files(temp_dir, pattern="*.csv")
        assert len(result) == 2
        assert all(p.suffix == ".csv" for p in result)

    def test_recursive_search(self, temp_dir):
        sub = temp_dir / "sub"
        sub.mkdir()
        (temp_dir / "a.csv").write_text("x")
        (sub / "b.csv").write_text("x")
        result = list_files(temp_dir, pattern="*.csv", recursive=True)
        assert len(result) == 2

    def test_non_existent_folder(self, tmp_path):
        result = list_files(tmp_path / "missing")
        assert result == []


# ============================================
# 5. delete_file()
# ============================================

class TestDeleteFile:

    def test_deletes_existing_file(self, tmp_path):
        f = tmp_path / "del.txt"
        f.write_text("x")
        result = delete_file(f)
        assert result is True
        assert not f.exists()

    def test_returns_false_if_missing(self, tmp_path):
        result = delete_file(tmp_path / "missing.txt")
        assert result is False

    def test_directory_not_deleted(self, tmp_path):
        d = tmp_path / "folder"
        d.mkdir()
        result = delete_file(d)
        assert result is False
        assert d.exists()


# ============================================
# 6. copy_file()
# ============================================

class TestCopyFile:

    def test_copies_file(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("hello")
        dst = tmp_path / "dst.txt"
        result = copy_file(src, dst)
        assert dst.exists()
        assert dst.read_text() == "hello"
        assert result == dst

    def test_creates_parent_dirs(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("hello")
        dst = tmp_path / "new" / "nested" / "dst.txt"
        copy_file(src, dst)
        assert dst.exists()

    def test_preserves_content(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("preserve me")
        dst = tmp_path / "dst.txt"
        copy_file(src, dst)
        assert src.read_text() == dst.read_text()


# ============================================
# 7. get_timestamp() / get_date_str()
# ============================================

class TestTimestamps:

    def test_get_timestamp_format(self):
        ts = get_timestamp()
        assert len(ts) == 15  # YYYYMMDD_HHMMSS
        assert "_" in ts
        assert ts.replace("_", "").isdigit()

    def test_get_timestamp_custom_format(self):
        ts = get_timestamp(fmt="%Y-%m-%d")
        assert len(ts) == 10

    def test_get_date_str_format(self):
        d = get_date_str()
        assert len(d) == 10
        assert d.count("-") == 2


# ============================================
# 8. Timer
# ============================================

class TestTimer:

    def test_measures_elapsed(self):
        with Timer("test", log=False) as t:
            time.sleep(0.05)
        assert t.elapsed >= 0.05

    def test_elapsed_before_exit_zero(self):
        timer = Timer("test", log=False)
        assert timer.elapsed == 0.0

    def test_returns_timer_instance(self):
        with Timer("test", log=False) as t:
            pass
        assert isinstance(t, Timer)


# ============================================
# 9. timed (decorator)
# ============================================

class TestTimedDecorator:

    def test_preserves_return_value(self):
        @timed
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_preserves_function_name(self):
        @timed
        def my_func():
            return 1

        assert my_func.__name__ == "my_func"

    def test_handles_kwargs(self):
        @timed
        def greet(name="world"):
            return f"hello {name}"

        assert greet(name="test") == "hello test"


# ============================================
# 10. print_section()
# ============================================

class TestPrintSection:

    def test_prints_section(self, capsys):
        print_section("Test Title")
        captured = capsys.readouterr().out
        assert "Test Title" in captured
        assert "=" in captured

    def test_custom_width(self, capsys):
        print_section("Hi", width=20)
        captured = capsys.readouterr().out
        lines = captured.strip().split("\n")
        assert len(lines[0]) == 20

    def test_custom_char(self, capsys):
        print_section("Title", char="-")
        captured = capsys.readouterr().out
        assert "------" in captured


# ============================================
# 11. print_dict()
# ============================================

class TestPrintDict:

    def test_prints_keys_and_values(self, capsys):
        print_dict({"alpha": 1, "beta": 2})
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out

    def test_formats_floats(self, capsys):
        print_dict({"value": 1234.5678})
        out = capsys.readouterr().out
        assert "1,234.57" in out

    def test_formats_ints(self, capsys):
        print_dict({"count": 10000})
        out = capsys.readouterr().out
        assert "10,000" in out

    def test_with_title(self, capsys):
        print_dict({"x": 1}, title="My Title")
        out = capsys.readouterr().out
        assert "My Title" in out


# ============================================
# 12. print_dataframe()
# ============================================

class TestPrintDataFrame:

    def test_prints_shape_and_columns(self, sample_df, capsys):
        print_dataframe(sample_df)
        out = capsys.readouterr().out
        assert "Shape" in out
        assert "Columns" in out

    def test_with_title(self, sample_df, capsys):
        print_dataframe(sample_df, title="My Data")
        out = capsys.readouterr().out
        assert "My Data" in out

    def test_respects_rows_limit(self, sample_df, capsys):
        print_dataframe(sample_df, rows=3)
        out = capsys.readouterr().out
        assert "ORD000" in out


# ============================================
# 13. format_currency()
# ============================================

class TestFormatCurrency:

    def test_default_symbol(self):
        assert format_currency(1234.56) == "Rs. 1,234.56"

    def test_custom_symbol(self):
        assert format_currency(100, symbol="$") == "$ 100.00"

    def test_zero(self):
        assert format_currency(0) == "Rs. 0.00"

    def test_negative(self):
        assert format_currency(-500) == "Rs. -500.00"

    def test_invalid_input(self):
        result = format_currency("invalid")
        assert result.startswith("Rs.")


# ============================================
# 14. format_number()
# ============================================

class TestFormatNumber:

    def test_default_decimals(self):
        assert format_number(1234.567) == "1,234.57"

    def test_zero_decimals(self):
        assert format_number(1234.567, decimals=0) == "1,235"

    def test_large_number(self):
        assert format_number(1234567.89) == "1,234,567.89"

    def test_invalid_input(self):
        assert format_number("bad") == "0"


# ============================================
# 15. format_percent()
# ============================================

class TestFormatPercent:

    def test_default_decimals(self):
        assert format_percent(45.678) == "45.68%"

    def test_one_decimal(self):
        assert format_percent(45.678, decimals=1) == "45.7%"

    def test_zero(self):
        assert format_percent(0) == "0.00%"

    def test_invalid_input(self):
        assert format_percent("bad") == "0.00%"


# ============================================
# 16. human_readable_size()
# ============================================

class TestHumanReadableSize:

    def test_bytes(self):
        assert human_readable_size(500) == "500.00 B"

    def test_kilobytes(self):
        result = human_readable_size(1024)
        assert "KB" in result

    def test_megabytes(self):
        result = human_readable_size(1024 * 1024)
        assert "MB" in result

    def test_gigabytes(self):
        result = human_readable_size(1024 ** 3)
        assert "GB" in result

    def test_terabytes(self):
        result = human_readable_size(1024 ** 4)
        assert "TB" in result


# ============================================
# 17. safe_divide()
# ============================================

class TestSafeDivide:

    def test_normal_division(self):
        assert safe_divide(10, 2) == 5.0

    def test_divide_by_zero(self):
        assert safe_divide(10, 0) == 0.0

    def test_divide_by_zero_custom_default(self):
        assert safe_divide(10, 0, default=-1.0) == -1.0

    def test_divide_by_nan(self):
        assert safe_divide(10, float("nan")) == 0.0

    def test_invalid_input(self):
        assert safe_divide("bad", 5) == 0.0


# ============================================
# 18. safe_to_numeric()
# ============================================

class TestSafeToNumeric:

    def test_string_with_rupee(self):
        s = pd.Series(["Rs.100", "Rs.200"])
        result = safe_to_numeric(s)
        assert result.tolist() == [100.0, 200.0]

    def test_string_with_commas(self):
        s = pd.Series(["1,200", "3,400"])
        result = safe_to_numeric(s)
        assert result.tolist() == [1200.0, 3400.0]

    def test_string_with_percent(self):
        s = pd.Series(["10%", "20%"])
        result = safe_to_numeric(s)
        assert result.tolist() == [10.0, 20.0]

    def test_invalid_becomes_default(self):
        s = pd.Series(["abc", "100"])
        result = safe_to_numeric(s)
        assert result.tolist() == [0.0, 100.0]

    def test_already_numeric(self):
        s = pd.Series([1.5, 2.5])
        result = safe_to_numeric(s)
        assert result.tolist() == [1.5, 2.5]


# ============================================
# 19. percent_change()
# ============================================

class TestPercentChange:

    def test_increase(self):
        assert percent_change(100, 150) == 50.0

    def test_decrease(self):
        assert percent_change(100, 50) == -50.0

    def test_no_change(self):
        assert percent_change(100, 100) == 0.0

    def test_zero_old_value(self):
        assert percent_change(0, 100) == 0.0

    def test_negative_old_value(self):
        # Uses abs() so sign is preserved correctly
        assert percent_change(-100, 50) == 150.0


# ============================================
# 20. save_json() / load_json()
# ============================================

class TestJSON:

    def test_save_and_load_dict(self, tmp_path):
        data = {"name": "test", "value": 42, "nested": {"a": 1}}
        path = tmp_path / "data.json"
        save_json(data, path)
        loaded = load_json(path)
        assert loaded == data

    def test_save_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "sub" / "deep" / "data.json"
        save_json({"x": 1}, path)
        assert path.exists()

    def test_save_list(self, tmp_path):
        data = [1, 2, 3]
        path = tmp_path / "list.json"
        save_json(data, path)
        loaded = load_json(path)
        assert loaded == data

    def test_load_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_json(tmp_path / "missing.json")

    def test_handles_non_serializable(self, tmp_path):
        data = {"ts": pd.Timestamp("2024-01-01")}
        path = tmp_path / "ts.json"
        save_json(data, path)
        loaded = load_json(path)
        assert "2024" in loaded["ts"]


# ============================================
# 21. save_text() / read_text()
# ============================================

class TestText:

    def test_save_and_read(self, tmp_path):
        path = tmp_path / "file.txt"
        save_text("Hello, world!", path)
        assert read_text(path) == "Hello, world!"

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "a" / "b" / "file.txt"
        save_text("nested", path)
        assert path.exists()

    def test_read_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_text(tmp_path / "missing.txt")

    def test_multiline(self, tmp_path):
        path = tmp_path / "multi.txt"
        save_text("Line1\nLine2\nLine3", path)
        content = read_text(path)
        assert content.count("\n") == 2


# ============================================
# 22. df_to_excel()
# ============================================

class TestDfToExcel:

    def test_single_sheet(self, tmp_path, sample_df):
        path = tmp_path / "out.xlsx"
        df_to_excel({"Sheet1": sample_df}, path)
        assert path.exists()

    def test_multiple_sheets(self, tmp_path, sample_df):
        path = tmp_path / "multi.xlsx"
        df_to_excel({"A": sample_df, "B": sample_df.head(3)}, path)
        assert path.exists()

    def test_creates_parent_dirs(self, tmp_path, sample_df):
        path = tmp_path / "new" / "deep" / "out.xlsx"
        df_to_excel({"S": sample_df}, path)
        assert path.exists()

    def test_sheet_name_truncated(self, tmp_path, sample_df):
        long_name = "A" * 50
        path = tmp_path / "trunc.xlsx"
        df_to_excel({long_name: sample_df}, path)
        assert path.exists()


# ============================================
# 23. memory_usage() / df_summary_str()
# ============================================

class TestMemoryAndSummary:

    def test_memory_usage_returns_string(self, sample_df):
        result = memory_usage(sample_df)
        assert isinstance(result, str)
        assert any(unit in result for unit in ["B", "KB", "MB"])

    def test_summary_contains_shape(self, sample_df):
        result = df_summary_str(sample_df, name="Test")
        assert "Test" in result
        assert "10 rows" in result

    def test_summary_contains_missing(self, sample_df):
        result = df_summary_str(sample_df)
        assert "Missing" in result

    def test_summary_contains_duplicates(self, sample_df):
        result = df_summary_str(sample_df)
        assert "Duplicates" in result


# ============================================
# 24. chunk_dataframe()
# ============================================

class TestChunkDataframe:

    def test_splits_into_chunks(self, sample_df):
        chunks = list(chunk_dataframe(sample_df, chunk_size=3))
        assert len(chunks) == 4  # 10 rows / 3 = 4 chunks

    def test_chunk_sizes(self, sample_df):
        chunks = list(chunk_dataframe(sample_df, chunk_size=3))
        assert len(chunks[0]) == 3
        assert len(chunks[-1]) == 1

    def test_preserves_all_rows(self, sample_df):
        chunks = list(chunk_dataframe(sample_df, chunk_size=3))
        total = sum(len(c) for c in chunks)
        assert total == len(sample_df)

    def test_empty_dataframe(self):
        df = pd.DataFrame({"A": []})
        chunks = list(chunk_dataframe(df, chunk_size=5))
        assert chunks == []

    def test_chunk_size_larger_than_df(self, sample_df):
        chunks = list(chunk_dataframe(sample_df, chunk_size=100))
        assert len(chunks) == 1


# ============================================
# 25. clean_column_for_sql()
# ============================================

class TestCleanColumnForSQL:

    def test_removes_spaces(self):
        assert clean_column_for_sql("Order ID") == "Order_ID"

    def test_removes_dashes(self):
        assert clean_column_for_sql("Total-Sales") == "Total_Sales"

    def test_removes_special_chars(self):
        assert clean_column_for_sql("Category@Type") == "Category_Type"

    def test_prefix_if_starts_with_digit(self):
        result = clean_column_for_sql("2024 Profit")
        assert result.startswith("col_")

    def test_already_clean(self):
        assert clean_column_for_sql("Sales") == "Sales"


# ============================================
# 26. get_numeric_columns() / get_categorical_columns()
# ============================================

class TestColumnGetters:

    def test_numeric_columns(self, sample_df):
        result = get_numeric_columns(sample_df)
        assert "Sales" in result
        assert "Profit" in result
        assert "Category" not in result

    def test_categorical_columns(self, sample_df):
        result = get_categorical_columns(sample_df)
        assert "Category" in result
        assert "Region" in result
        assert "Sales" not in result

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        assert get_numeric_columns(df) == []
        assert get_categorical_columns(df) == []


# ============================================
# 27. retry (decorator)
# ============================================

class TestRetryDecorator:

    def test_succeeds_on_first_try(self):
        calls = {"n": 0}

        @retry(times=3, delay=0.01)
        def good():
            calls["n"] += 1
            return "ok"

        assert good() == "ok"
        assert calls["n"] == 1

    def test_retries_on_exception(self):
        calls = {"n": 0}

        @retry(times=3, delay=0.01)
        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ValueError("boom")
            return "ok"

        assert flaky() == "ok"
        assert calls["n"] == 3

    def test_raises_after_exhausting(self):
        calls = {"n": 0}

        @retry(times=2, delay=0.01)
        def always_fails():
            calls["n"] += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            always_fails()
        assert calls["n"] == 2

    def test_preserves_function_name(self):
        @retry(times=2)
        def my_func():
            return 1

        assert my_func.__name__ == "my_func"


# ============================================
# 28. suppress_stdout (context manager)
# ============================================

class TestSuppressStdout:

    def test_suppresses_output(self, capsys):
        with suppress_stdout():
            print("this should not appear")
        captured = capsys.readouterr()
        assert "this should not appear" not in captured.out

    def test_restores_stdout(self, capsys):
        with suppress_stdout():
            print("hidden")
        print("visible")
        captured = capsys.readouterr()
        assert "visible" in captured.out


# ============================================
# 29. Integration tests
# ============================================

class TestIntegration:

    def test_save_load_json_roundtrip(self, tmp_path):
        original = {
            "kpis": {"sales": 1000, "profit": 200},
            "meta": {"rows": 100, "api_used": False},
        }
        path = tmp_path / "roundtrip.json"
        save_json(original, path)
        loaded = load_json(path)
        assert loaded == original

    def test_save_excel_then_verify(self, tmp_path, sample_df):
        path = tmp_path / "excel_test.xlsx"
        df_to_excel({"Data": sample_df}, path)
        loaded = pd.read_excel(path, sheet_name="Data")
        assert loaded.shape[0] == len(sample_df)
        assert loaded.shape[1] == sample_df.shape[1]

    def test_ensure_dir_then_save(self, tmp_path):
        folder = tmp_path / "created" / "on" / "the" / "fly"
        ensure_dir(folder)
        path = folder / "file.json"
        save_json({"ok": True}, path)
        assert path.exists()
        assert load_json(path) == {"ok": True}


# ============================================
# 30. Edge cases
# ============================================

class TestEdgeCases:

    def test_format_currency_none(self):
        result = format_currency(None)
        assert result == "Rs. 0.00"

    def test_format_number_none(self):
        assert format_number(None) == "0"

    def test_safe_divide_none(self):
        assert safe_divide(None, 5) == 0.0

    def test_human_readable_size_zero(self):
        assert human_readable_size(0) == "0.00 B"

    def test_get_logger_with_level(self):
        import logging
        logger = get_logger("edge_logger", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_chunk_dataframe_zero_size(self, sample_df):
        # Zero chunk size would cause infinite loop — function should
        # still yield at least one chunk via range step
        with pytest.raises((ValueError, TypeError)):
            list(chunk_dataframe(sample_df, chunk_size=0))


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import pytest as _pytest
    sys.exit(_pytest.main([__file__, "-v", "--tb=short"]))