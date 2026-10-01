from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "bank-full.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
POWERBI_DIR = ROOT / "data" / "powerbi"

MONTH_ORDER = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def age_band(age: pd.Series) -> pd.Series:
    return pd.cut(
        age,
        bins=[17, 29, 39, 49, 59, 120],
        labels=["18-29", "30-39", "40-49", "50-59", "60+"],
    ).astype("string")


def balance_band(balance: pd.Series) -> pd.Series:
    return pd.cut(
        balance,
        bins=[-np.inf, 0, 500, 1500, 5000, np.inf],
        labels=["<=0", "1-500", "501-1,500", "1,501-5,000", "5,000+"],
    ).astype("string")


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    expected = {
        "age",
        "job",
        "marital",
        "education",
        "default",
        "balance",
        "housing",
        "loan",
        "contact",
        "day",
        "month",
        "duration",
        "campaign",
        "pdays",
        "previous",
        "poutcome",
        "y",
    }
    missing = expected.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = raw.copy()
    df.columns = [column.strip().lower() for column in df.columns]
    df.insert(0, "contact_id", np.arange(1, len(df) + 1, dtype=int))
    df["customer_id"] = "C" + df["contact_id"].astype(str).str.zfill(6)
    df["subscribed"] = df["y"].eq("yes").astype(int)
    df["month_number"] = df["month"].map(MONTH_ORDER).astype(int)
    df["month_name"] = df["month"].str.title()
    df["age_band"] = age_band(df["age"])
    df["balance_band"] = balance_band(df["balance"])
    df["has_prior_contact"] = df["pdays"].ne(-1).astype(int)
    df["contact_duration_minutes"] = (df["duration"] / 60).round(2)
    df["campaign_intensity"] = pd.cut(
        df["campaign"],
        bins=[0, 1, 2, 4, np.inf],
        labels=["1 contact", "2 contacts", "3-4 contacts", "5+ contacts"],
    ).astype("string")
    return df.drop(columns=["y"])


def build_powerbi_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    dim_customer = df[
        [
            "customer_id",
            "age",
            "age_band",
            "job",
            "marital",
            "education",
            "balance",
            "balance_band",
            "default",
            "housing",
            "loan",
        ]
    ].copy()

    dim_month = (
        df[["month_number", "month_name"]]
        .drop_duplicates()
        .sort_values("month_number")
        .reset_index(drop=True)
    )
    dim_channel = (
        df[["contact"]]
        .drop_duplicates()
        .sort_values("contact")
        .reset_index(drop=True)
        .rename(columns={"contact": "contact_channel"})
    )
    dim_channel.insert(0, "channel_id", range(1, len(dim_channel) + 1))
    channel_lookup = dict(
        zip(dim_channel["contact_channel"], dim_channel["channel_id"], strict=True)
    )

    fact_campaign = df[
        [
            "contact_id",
            "customer_id",
            "month_number",
            "day",
            "duration",
            "contact_duration_minutes",
            "campaign",
            "campaign_intensity",
            "pdays",
            "previous",
            "poutcome",
            "has_prior_contact",
            "subscribed",
        ]
    ].copy()
    fact_campaign["channel_id"] = df["contact"].map(channel_lookup).astype(int)

    return {
        "dim_customer": dim_customer,
        "dim_month": dim_month,
        "dim_channel": dim_channel,
        "fact_campaign": fact_campaign,
    }


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Missing {RAW_FILE}. Download bank-full.csv from the UCI Bank Marketing dataset."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(RAW_FILE, sep=";")
    clean = clean_data(raw)
    clean.to_csv(PROCESSED_DIR / "bank_marketing_clean.csv", index=False)

    for name, table in build_powerbi_tables(clean).items():
        table.to_csv(POWERBI_DIR / f"{name}.csv", index=False)

    quality = pd.DataFrame(
        {
            "check": [
                "row_count",
                "duplicate_contact_ids",
                "missing_values",
                "subscription_rate",
            ],
            "value": [
                len(clean),
                int(clean["contact_id"].duplicated().sum()),
                int(clean.isna().sum().sum()),
                round(float(clean["subscribed"].mean()), 4),
            ],
        }
    )
    quality.to_csv(PROCESSED_DIR / "data_quality_summary.csv", index=False)
    print(
        f"Processed {len(clean):,} campaign contacts; "
        f"subscription rate={clean['subscribed'].mean():.2%}"
    )


if __name__ == "__main__":
    main()

