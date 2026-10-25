"""Multi-format export capabilities for vlrdevapi models.

Provides native zero-dependency export to CSV and Markdown, as well as optional
export to Pandas, Polars, Excel, and Apache Parquet.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from vlrdevapi.exceptions import MissingDependencyError


def _require_pandas() -> Any:
    """Import and return pandas, or raise a helpful MissingDependencyError."""
    try:
        import pandas as pd
        return pd
    except ImportError:
        raise MissingDependencyError(
            "pandas is required for this operation. "
            "Install it via: pip install 'vlrdevapi[pandas]' or uv add 'vlrdevapi[pandas]'"
        ) from None


def _require_polars() -> Any:
    """Import and return polars, or raise a helpful MissingDependencyError."""
    try:
        import polars as pl
        return pl
    except ImportError:
        raise MissingDependencyError(
            "polars is required for this operation. "
            "Install it via: pip install 'vlrdevapi[polars]' or uv add 'vlrdevapi[polars]'"
        ) from None


def _require_openpyxl() -> Any:
    """Import and return openpyxl, or raise a helpful MissingDependencyError."""
    try:
        import openpyxl
        return openpyxl
    except ImportError:
        raise MissingDependencyError(
            "openpyxl is required for Excel (.xlsx) export. "
            "Install it via: pip install 'vlrdevapi[excel]' or uv add 'vlrdevapi[excel]'"
        ) from None


def _require_pyarrow() -> Any:
    """Import and return pyarrow, or raise a helpful MissingDependencyError."""
    try:
        import pyarrow
        return pyarrow
    except ImportError:
        raise MissingDependencyError(
            "pyarrow is required for Parquet (.parquet) export. "
            "Install it via: pip install 'vlrdevapi[parquet]' (or 'vlrdevapi[arrow]') or uv add 'vlrdevapi[parquet]'"
        ) from None


import json


def _format_csv_value(val: Any) -> Any:
    """Format record values cleanly for CSV output."""
    if val is None:
        return ""
    if isinstance(val, (list, tuple)):
        if not val:
            return ""
        if all(isinstance(x, (str, int, float)) for x in val):
            return "; ".join(str(x) for x in val)
        return json.dumps(val)
    if isinstance(val, dict):
        return json.dumps(val)
    return val


def records_to_csv(records: list[dict[str, Any]], path: str | Path | None = None) -> str | None:
    """Export a list of records to CSV format with zero external dependencies.

    Args:
        records: List of dictionaries representing table rows.
        path: Optional file path to write to. If None, returns CSV string.

    Returns:
        CSV string if path is None, or None if written to file.
    """
    if not records:
        if path:
            Path(path).write_text("", encoding="utf-8")
            return None
        return ""

    fieldnames: list[str] = []
    for r in records:
        for k in r:
            if k not in fieldnames:
                fieldnames.append(k)

    # Format nested lists/dicts cleanly
    clean_records = [
        {k: _format_csv_value(r.get(k)) for k in fieldnames}
        for r in records
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(clean_records)
    csv_str = output.getvalue()

    if path:
        Path(path).write_text(csv_str, encoding="utf-8")
        return None
    return csv_str


def records_to_markdown(records: list[dict[str, Any]], columns: list[str] | None = None) -> str:
    """Render a list of records as an aligned GitHub Flavored Markdown table.

    Zero external dependencies.

    Args:
        records: List of dictionaries representing table rows.
        columns: Optional list of column keys to include (in order).

    Returns:
        Formatted Markdown table string.
    """
    if not records:
        return ""

    if columns is None:
        columns = []
        for r in records:
            for k in r:
                if k not in columns:
                    columns.append(k)

    if not columns:
        return ""

    def _escape_md(s: str) -> str:
        return s.replace("|", "\\|")

    def _format_md_val(val: Any) -> str:
        if val is None:
            return ""
        if isinstance(val, (list, tuple)):
            if all(isinstance(x, (str, int, float)) for x in val):
                res = ", ".join(str(x) for x in val)
            else:
                res = json.dumps(val)
        elif isinstance(val, dict):
            res = json.dumps(val)
        else:
            res = str(val).replace("\n", " ").strip()
        return _escape_md(res)

    escaped_columns = [_escape_md(str(c)) for c in columns]
    widths = {col: max(len(esc_col), 3) for col, esc_col in zip(columns, escaped_columns)}
    formatted_rows: list[list[str]] = []
    for r in records:
        row_vals: list[str] = []
        for col in columns:
            val_str = _format_md_val(r.get(col))
            widths[col] = max(widths[col], len(val_str))
            row_vals.append(val_str)
        formatted_rows.append(row_vals)

    header_line = "| " + " | ".join(esc_col.ljust(widths[col]) for col, esc_col in zip(columns, escaped_columns)) + " |"
    separator_line = "| " + " | ".join("-" * widths[col] for col in columns) + " |"
    data_lines = [
        "| " + " | ".join(val.ljust(widths[col]) for col, val in zip(columns, row)) + " |"
        for row in formatted_rows
    ]

    return "\n".join([header_line, separator_line, *data_lines])


class ExportableModel(BaseModel):
    """Base Pydantic model with built-in export to JSON, CSV, Markdown, Pandas, Polars, Excel, and Parquet."""

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Hook for models to define how their data flattens into tabular records.

        Subclasses override this to implement domain-aware tabular flattening.
        Defaults to returning a single record with model fields in JSON-compatible mode.
        """
        return [self.model_dump(mode="json")]

    def to_json(
        self,
        path: str | Path | None = None,
        indent: int = 2,
        orient: str = "records",
        **kwargs: Any,
    ) -> str | None:
        """Export data as JSON string or write to a JSON file.

        Args:
            path: Optional file path to write to. If None, returns JSON string.
            indent: Indentation level for pretty-printing (default: 2).
            orient: 'records' (default) exports flattened tabular records.
                    'model' exports the full hierarchical Pydantic model tree.
            **kwargs: Extra parameters passed to to_records() or model_dump_json().

        Returns:
            JSON string if path is None, or None if written to file.
        """
        if orient == "model":
            json_str = self.model_dump_json(indent=indent)
        else:
            records = self.to_records(**kwargs)
            json_str = json.dumps(records, indent=indent, default=str)

        if path:
            Path(path).write_text(json_str, encoding="utf-8")
            return None
        return json_str

    def to_dict(self, orient: str = "records", **kwargs: Any) -> Any:
        """Export data as a Python dictionary or list of record dictionaries.

        Args:
            orient: 'records' (default) returns list of tabular dict records.
                    'model' returns the complete Pydantic model dictionary tree.
        """
        if orient == "model":
            return self.model_dump(mode="json", **kwargs)
        return self.to_records(**kwargs)

    def to_csv(self, path: str | Path | None = None, **kwargs: Any) -> str | None:
        """Export tabular records to CSV format.

        Uses standard library csv (zero dependencies).
        """
        records = self.to_records(**kwargs)
        return records_to_csv(records, path=path)

    def to_markdown(self, columns: list[str] | None = None, **kwargs: Any) -> str:
        """Export tabular records as a GitHub Flavored Markdown (GFM) table.

        Zero dependencies.
        """
        records = self.to_records(**kwargs)
        return records_to_markdown(records, columns=columns)

    def to_df(self, **kwargs: Any) -> Any:
        """Export tabular records to a pandas DataFrame.

        Requires pandas. Install with: pip install 'vlrdevapi[pandas]'
        """
        pd = _require_pandas()
        return pd.DataFrame(self.to_records(**kwargs))

    def to_dataframe(self, **kwargs: Any) -> Any:
        """Alias for to_df()."""
        return self.to_df(**kwargs)

    def to_polars(self, **kwargs: Any) -> Any:
        """Export tabular records to a Polars DataFrame.

        Requires polars. Install with: pip install 'vlrdevapi[polars]'
        """
        pl = _require_polars()
        return pl.DataFrame(self.to_records(**kwargs))

    def to_excel(
        self,
        path: str | Path,
        sheet_name: str = "Sheet1",
        index: bool = False,
        **kwargs: Any,
    ) -> None:
        """Export tabular records to an Excel (.xlsx) file.

        Requires openpyxl and pandas. Install with: pip install 'vlrdevapi[excel]'
        """
        _require_openpyxl()
        df = self.to_df(**kwargs)
        # Excel/openpyxl does not support timezone-aware datetimes. Strip tzinfo for compatibility.
        for col in df.select_dtypes(include=["datetimetz"]).columns:
            df[col] = df[col].dt.tz_localize(None)
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda v: v.replace(tzinfo=None) if hasattr(v, "tzinfo") and v.tzinfo is not None else v
                )
        df.to_excel(path, sheet_name=sheet_name, index=index, engine="openpyxl")

    def to_parquet(self, path: str | Path, index: bool = False, **kwargs: Any) -> None:
        """Export tabular records to an Apache Parquet (.parquet) file.

        Requires pyarrow and pandas. Install with: pip install 'vlrdevapi[parquet]'
        """
        _require_pyarrow()
        df = self.to_df(**kwargs)
        df.to_parquet(path, index=index, engine="pyarrow")
