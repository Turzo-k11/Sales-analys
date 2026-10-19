"""Supermart Grocery Sales – reproducible exploratory sales analysis.

Based on the user's original Colab notebook. Run with:
    python supermarket_sales_analysis_improved.py --input SupermartGrocerySales.csv

Outputs summary CSVs and PNG charts to ./sales_analysis_output by default.
Requires: pandas, numpy, matplotlib.

Important: one row is treated as one sales record, NOT necessarily one item sold.
Order counts are computed only when an Order ID is available.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save charts without requiring a graphical interface
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MONTH_ORDER = list(range(1, 13))
REQUIRED = {"Order Date", "Category", "Sub Category", "Region", "Sales", "Profit", "Discount"}


def load_and_prepare(path: Path) -> pd.DataFrame:
    """Read and validate data, keeping original identifiers and dates."""
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}. Provide --input path/to/file.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    missing = sorted(REQUIRED - set(df.columns))
    if missing:
        raise ValueError(f"Missing expected columns: {', '.join(missing)}")
    if df.empty:
        raise ValueError("Input CSV is empty")

    print(f"Rows loaded: {len(df):,}; duplicated full rows: {df.duplicated().sum():,}")
    print("Missing values by column:\n", df.isna().sum().to_string())

    for col in ["Sales", "Profit", "Discount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # This dataset uses two date conventions depending on separator:
    # DD-MM-YYYY for hyphens and MM/DD/YYYY for slashes.
    # A generic format="mixed" incorrectly interprets ambiguous hyphenated dates.
    raw_dates = df["Order Date"].astype("string").str.strip()
    hyphen = raw_dates.str.contains("-", regex=False, na=False)
    slash = raw_dates.str.contains("/", regex=False, na=False)
    dates = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    dates.loc[hyphen] = pd.to_datetime(raw_dates.loc[hyphen], format="%d-%m-%Y", errors="coerce")
    dates.loc[slash] = pd.to_datetime(raw_dates.loc[slash], format="%m/%d/%Y", errors="coerce")
    print(f"Date formats: {hyphen.sum():,} day-first hyphen, {slash.sum():,} month-first slash; invalid: {dates.isna().sum():,}")
    df["Order Date"] = dates
    crucial = ["Order Date", "Sales", "Profit", "Category", "Sub Category", "Region"]
    invalid = df[crucial].isna().any(axis=1)
    if invalid.any():
        print(f"WARNING: Excluding {invalid.sum():,} rows with missing/invalid critical values")
        df = df.loc[~invalid].copy()
    if df.empty:
        raise ValueError("No valid rows remain after checking critical fields")
    df["Year"] = df["Order Date"].dt.year
    df["Month Number"] = df["Order Date"].dt.month
    df["Year Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Weekday"] = df["Order Date"].dt.day_name()
    return df


def save_summary(table: pd.DataFrame, filename: str, output: Path) -> None:
    table.to_csv(output / filename, index=False)
    print(f"Saved {filename}")


def bar_chart(table: pd.DataFrame, x: str, y: str, title: str, path: Path,
              horizontal: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    if horizontal:
        ax.barh(table[x].astype(str), table[y])
        ax.invert_yaxis()
        ax.set_xlabel(y)
    else:
        ax.bar(table[x].astype(str), table[y])
        ax.tick_params(axis="x", labelrotation=35)
        ax.set_ylabel(y)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def group_financials(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = df.groupby(columns, dropna=False).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"),
        Records=("Sales", "size"),
    ).reset_index()
    result["Profit Margin %"] = np.where(
        result["Sales"] != 0, 100 * result["Profit"] / result["Sales"], np.nan
    )
    return result


def analyze(df: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    overview = pd.DataFrame([{
        "Sales": df["Sales"].sum(),
        "Profit": df["Profit"].sum(),
        "Profit Margin %": 100 * df["Profit"].sum() / df["Sales"].sum() if df["Sales"].sum() else np.nan,
        "Records": len(df),
        "Distinct Orders": df["Order ID"].nunique() if "Order ID" in df else np.nan,
    }])
    save_summary(overview, "overview.csv", output)
    print("\nOverall indicators:\n", overview.to_string(index=False))

    summaries = [
        (["Category"], "category.csv", "Sales by Category", "category_sales.png"),
        (["Sub Category"], "subcategory.csv", "Sales by Subcategory", "subcategory_sales.png"),
        (["Region"], "region.csv", "Profit by Region", "region_profit.png"),
        (["Year"], "year.csv", "Sales by Year", "year_sales.png"),
        (["Year Month"], "year_month.csv", "Sales by Year-Month", "monthly_sales.png"),
        (["Weekday"], "weekday.csv", "Records by Weekday", "weekday_records.png"),
        (["Region", "Category"], "region_category.csv", None, None),
        (["Year", "Month Number"], "profit_year_month.csv", None, None),
    ]
    for cols, filename, title, chart in summaries:
        tab = group_financials(df, cols)
        if cols == ["Weekday"]:
            order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            tab["Weekday"] = pd.Categorical(tab["Weekday"], categories=order, ordered=True)
            tab = tab.sort_values("Weekday")
        elif cols in (["Category"], ["Sub Category"], ["Region"]):
            tab = tab.sort_values("Sales", ascending=False)
        else:
            tab = tab.sort_values(cols)
        save_summary(tab, filename, output)
        if chart:
            measure = "Profit" if cols == ["Region"] else "Records" if cols == ["Weekday"] else "Sales"
            bar_chart(tab, cols[0], measure, title, output / chart,
                      horizontal=cols == ["Sub Category"])

    # Cross-tab of profit per calendar year/month, without an undefined variable.
    monthly = group_financials(df, ["Year", "Month Number"])
    pivot = monthly.pivot(index="Year", columns="Month Number", values="Profit").reindex(columns=MONTH_ORDER)
    fig, ax = plt.subplots(figsize=(12, 5))
    image = ax.imshow(pivot.to_numpy(dtype=float), aspect="auto")
    ax.set_xticks(range(12), labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    ax.set_title("Profit by Year and Month (blank = no records)")
    fig.colorbar(image, ax=ax, label="Profit")
    fig.tight_layout()
    fig.savefig(output / "profit_heatmap.png", dpi=160)
    plt.close(fig)

    # Correlation describes association, not causality.
    for x, name in [("Sales", "sales_profit"), ("Discount", "discount_profit")]:
        clean = df[[x, "Profit"]].dropna()
        corr = clean[x].corr(clean["Profit"]) if len(clean) > 1 else np.nan
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(clean[x], clean["Profit"], alpha=.35, s=12)
        ax.set(xlabel=x, ylabel="Profit", title=f"{x} vs Profit (Pearson r = {corr:.2f})")
        fig.tight_layout()
        fig.savefig(output / f"{name}.png", dpi=160)
        plt.close(fig)
        print(f"{x} vs Profit correlation: {corr:.3f}")
    print(f"\nCompleted. Output folder: {output.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Supermart Grocery Sales CSV")
    parser.add_argument("--input", type=Path, default=Path("Supermart Grocery Sales - Retail Analytics Dataset.csv"), help="Input CSV file")
    parser.add_argument("--output", type=Path, default=Path("sales_analysis_output"), help="Output directory")
    args = parser.parse_args()
    analyze(load_and_prepare(args.input), args.output)


if __name__ == "__main__":
    main()
