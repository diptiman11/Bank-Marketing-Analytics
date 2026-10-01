from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "bank_marketing_clean.csv"
METRICS_FILE = ROOT / "reports" / "generated" / "model_metrics.json"
OUTPUT_FILE = ROOT / "reports" / "generated" / "business_insights.md"


def pct(value: float) -> str:
    return f"{value:.1%}"


def main() -> None:
    df = pd.read_csv(DATA_FILE)
    metrics = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    selected = next(
        item for item in metrics["models"] if item["model"] == metrics["selected_model"]
    )

    job = (
        df.groupby("job", as_index=False)["subscribed"]
        .agg(["count", "mean"])
        .query("count >= 500")
        .sort_values("mean", ascending=False)
        .head(3)
    )
    month = (
        df.groupby(["month_number", "month_name"], as_index=False)["subscribed"]
        .agg(["count", "mean"])
        .query("count >= 500")
        .sort_values("mean", ascending=False)
        .head(3)
    )
    channel = (
        df.groupby("contact", as_index=False)["subscribed"]
        .agg(["count", "mean"])
        .sort_values("mean", ascending=False)
    )
    prior = df.groupby("poutcome")["subscribed"].agg(["count", "mean"]).sort_values(
        "mean", ascending=False
    )

    lines = [
        "# Business insight summary",
        "",
        "## Executive summary",
        "",
        f"- The dataset contains **{len(df):,}** historical campaign contacts.",
        f"- Overall term-deposit subscription rate: **{pct(df['subscribed'].mean())}**.",
        f"- Selected pre-contact model: **{metrics['selected_model']}** "
        f"(PR-AUC {selected['pr_auc']}, ROC-AUC {selected['roc_auc']}).",
        "- Call duration is excluded from prediction because it is unavailable before contact and would leak post-call information.",
        "",
        "## Strong observed segments",
        "",
    ]
    for row in job.itertuples():
        lines.append(
            f"- Job: **{row.job}** — {pct(row.mean)} conversion across {row.count:,} contacts."
        )
    for row in month.itertuples():
        lines.append(
            f"- Month: **{row.month_name}** — {pct(row.mean)} conversion across {row.count:,} contacts."
        )
    lines.extend(["", "## Channel performance", ""])
    for row in channel.itertuples():
        lines.append(
            f"- **{row.contact}** — {pct(row.mean)} conversion across {row.count:,} contacts."
        )
    lines.extend(["", "## Previous campaign signal", ""])
    for row in prior.itertuples():
        lines.append(
            f"- Previous outcome **{row.Index}** — {pct(row.mean)} conversion across {row.count:,} contacts."
        )
    lines.extend(
        [
            "",
            "## Recommended actions",
            "",
            "1. Use propensity scores to prioritize the top 10% of prospects, then compare conversion and contact cost against the current broad-contact strategy.",
            "2. Treat the model as a prioritization aid rather than an automatic approval or exclusion rule.",
            "3. Test channel and timing recommendations through a controlled campaign before operational rollout.",
            "4. Monitor conversion, false-negative rate, segment fairness, and model drift after each campaign cycle.",
            "",
            "## Limitations",
            "",
            "- This is a public historical dataset from a Portuguese bank, not current Australian customer data.",
            "- No persistent customer identifier is supplied; generated customer IDs represent campaign rows, not verified unique individuals.",
            "- The analysis demonstrates a portfolio workflow and should not be used for real customer decisions without governance and validation.",
        ]
    )
    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
