from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "bank_marketing_clean.csv"
POWERBI_DIR = ROOT / "data" / "powerbi"
REPORT_DIR = ROOT / "reports" / "generated"
MODEL_DIR = ROOT / "models"

# Duration is deliberately excluded: it is only known after a call ends.
NUMERIC_FEATURES = ["age", "balance", "campaign", "pdays", "previous", "month_number", "day"]
CATEGORICAL_FEATURES = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "poutcome",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ]
    )


def candidate_models() -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline(
            [
                ("preprocessor", build_preprocessor()),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1500,
                        random_state=42,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("preprocessor", build_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=250,
                        min_samples_leaf=5,
                        class_weight="balanced_subsample",
                        n_jobs=-1,
                        random_state=42,
                    ),
                ),
            ]
        ),
    }


def choose_threshold(y_true: pd.Series, probabilities: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    beta_sq = 4
    f2 = (1 + beta_sq) * precision * recall / (beta_sq * precision + recall + 1e-12)
    best_index = int(np.nanargmax(f2[:-1]))
    return float(thresholds[best_index])


def evaluate(
    name: str, model: Pipeline, x_test: pd.DataFrame, y_test: pd.Series
) -> tuple[dict[str, float | int | str | list[list[int]]], np.ndarray]:
    probabilities = model.predict_proba(x_test)[:, 1]
    threshold = choose_threshold(y_test, probabilities)
    predictions = (probabilities >= threshold).astype(int)
    return (
        {
            "model": name,
            "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
            "pr_auc": round(float(average_precision_score(y_test, probabilities)), 4),
            "precision": round(float(precision_score(y_test, predictions)), 4),
            "recall": round(float(recall_score(y_test, predictions)), 4),
            "f1": round(float(f1_score(y_test, predictions)), 4),
            "threshold": round(threshold, 4),
            "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        },
        probabilities,
    )


def make_priority_segments(probabilities: pd.Series) -> pd.Series:
    high_cut = probabilities.quantile(0.90)
    medium_cut = probabilities.quantile(0.70)
    return pd.Series(
        np.select(
            [probabilities >= high_cut, probabilities >= medium_cut],
            ["High priority", "Medium priority"],
            default="Low priority",
        ),
        index=probabilities.index,
    )


def build_evaluation_table(
    source: pd.DataFrame,
    test_index: pd.Index,
    y_test: pd.Series,
    probabilities: np.ndarray,
) -> pd.DataFrame:
    evaluation = source.loc[
        test_index,
        [
            "contact_id",
            "customer_id",
            "age_band",
            "job",
            "education",
            "contact",
            "month_name",
        ],
    ].copy()
    evaluation["actual_subscribed"] = y_test.loc[test_index].astype(int)
    evaluation["propensity_score"] = probabilities
    evaluation = evaluation.sort_values("propensity_score", ascending=False).reset_index(
        drop=True
    )
    evaluation["rank"] = np.arange(1, len(evaluation) + 1)
    evaluation["population_share"] = evaluation["rank"] / len(evaluation)
    evaluation["decile"] = np.ceil(evaluation["population_share"] * 10).astype(int)
    evaluation["cumulative_subscribers"] = evaluation["actual_subscribed"].cumsum()
    total_subscribers = max(int(evaluation["actual_subscribed"].sum()), 1)
    evaluation["cumulative_capture_rate"] = (
        evaluation["cumulative_subscribers"] / total_subscribers
    )
    baseline_rate = max(float(evaluation["actual_subscribed"].mean()), 1e-12)
    evaluation["cumulative_response_rate"] = (
        evaluation["cumulative_subscribers"] / evaluation["rank"]
    )
    evaluation["cumulative_lift"] = (
        evaluation["cumulative_response_rate"] / baseline_rate
    )
    return evaluation


def build_decile_table(evaluation: pd.DataFrame) -> pd.DataFrame:
    return (
        evaluation.groupby("decile", as_index=False)
        .agg(
            prospects=("contact_id", "count"),
            subscribers=("actual_subscribed", "sum"),
            response_rate=("actual_subscribed", "mean"),
            average_score=("propensity_score", "mean"),
            cumulative_capture_rate=("cumulative_capture_rate", "max"),
        )
        .assign(
            baseline_rate=float(evaluation["actual_subscribed"].mean()),
            lift=lambda table: table["response_rate"] / table["baseline_rate"],
        )
    )


def feature_importance(model: Pipeline) -> pd.DataFrame:
    names = model.named_steps["preprocessor"].get_feature_names_out()
    estimator = model.named_steps["model"]
    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    else:
        values = np.abs(estimator.coef_[0])
    return (
        pd.DataFrame({"feature": names, "importance": values})
        .sort_values("importance", ascending=False)
        .head(25)
        .reset_index(drop=True)
    )


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError("Run `python -m src.data_pipeline` first.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_FILE)
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES],
        df["subscribed"],
        test_size=0.25,
        random_state=42,
        stratify=df["subscribed"],
    )

    results: list[dict[str, float | int | str | list[list[int]]]] = []
    fitted: dict[str, Pipeline] = {}
    for name, model in candidate_models().items():
        model.fit(x_train, y_train)
        metrics, _ = evaluate(name, model, x_test, y_test)
        results.append(metrics)
        fitted[name] = model

    best_metrics = max(results, key=lambda item: float(item["pr_auc"]))
    best_name = str(best_metrics["model"])
    best_model = fitted[best_name]

    test_probabilities = best_model.predict_proba(x_test)[:, 1]
    evaluation = build_evaluation_table(df, x_test.index, y_test, test_probabilities)
    evaluation.to_csv(POWERBI_DIR / "evaluation_predictions.csv", index=False)
    build_decile_table(evaluation).to_csv(
        REPORT_DIR / "decile_performance.csv", index=False
    )

    all_probabilities = pd.Series(
        best_model.predict_proba(df[FEATURES])[:, 1],
        index=df.index,
        name="propensity_score",
    )
    scores = df[
        [
            "contact_id",
            "customer_id",
            "age_band",
            "job",
            "education",
            "contact",
            "month_name",
            "subscribed",
        ]
    ].copy()
    scores["propensity_score"] = all_probabilities.round(4)
    scores["priority_segment"] = make_priority_segments(all_probabilities)
    scores.to_csv(POWERBI_DIR / "model_scores.csv", index=False)

    feature_importance(best_model).to_csv(
        REPORT_DIR / "feature_importance.csv", index=False
    )
    pd.DataFrame(results).drop(columns=["confusion_matrix"]).to_csv(
        REPORT_DIR / "model_comparison.csv", index=False
    )
    with (REPORT_DIR / "model_metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "selected_model": best_name,
                "data_leakage_control": "duration excluded from all models",
                "models": results,
            },
            handle,
            indent=2,
        )

    joblib.dump(best_model, MODEL_DIR / "propensity_model.joblib")

    test_predictions = (
        test_probabilities >= float(best_metrics["threshold"])
    ).astype(int)
    report = classification_report(y_test, test_predictions, digits=4)
    (REPORT_DIR / "classification_report.txt").write_text(report, encoding="utf-8")

    print(
        f"Selected {best_name}: PR-AUC={best_metrics['pr_auc']}, "
        f"ROC-AUC={best_metrics['roc_auc']}, recall={best_metrics['recall']}"
    )


if __name__ == "__main__":
    main()
