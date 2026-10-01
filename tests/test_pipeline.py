import pandas as pd

from src.data_pipeline import build_powerbi_tables, clean_data
from src.train_model import build_decile_table, build_evaluation_table


def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "age": 35,
                "job": "management",
                "marital": "single",
                "education": "tertiary",
                "default": "no",
                "balance": 1500,
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "day": 10,
                "month": "may",
                "duration": 240,
                "campaign": 1,
                "pdays": -1,
                "previous": 0,
                "poutcome": "unknown",
                "y": "yes",
            },
            {
                "age": 61,
                "job": "retired",
                "marital": "married",
                "education": "secondary",
                "default": "no",
                "balance": -10,
                "housing": "no",
                "loan": "no",
                "contact": "telephone",
                "day": 3,
                "month": "oct",
                "duration": 60,
                "campaign": 5,
                "pdays": 30,
                "previous": 2,
                "poutcome": "success",
                "y": "no",
            },
        ]
    )


def test_clean_data_adds_business_fields() -> None:
    clean = clean_data(sample_data())
    assert clean["contact_id"].tolist() == [1, 2]
    assert clean["subscribed"].tolist() == [1, 0]
    assert clean["month_number"].tolist() == [5, 10]
    assert clean["age_band"].tolist() == ["30-39", "60+"]
    assert clean["has_prior_contact"].tolist() == [0, 1]


def test_powerbi_tables_preserve_fact_rows() -> None:
    clean = clean_data(sample_data())
    tables = build_powerbi_tables(clean)
    assert len(tables["fact_campaign"]) == len(clean)
    assert tables["dim_customer"]["customer_id"].is_unique
    assert set(tables["dim_channel"]["contact_channel"]) == {
        "cellular",
        "telephone",
    }


def test_evaluation_table_tracks_rank_capture_and_deciles() -> None:
    clean = clean_data(sample_data())
    y_test = clean["subscribed"]
    probabilities = [0.2, 0.9]
    evaluation = build_evaluation_table(
        clean, clean.index, y_test, probabilities
    )
    assert evaluation.iloc[0]["contact_id"] == 2
    assert evaluation["rank"].tolist() == [1, 2]
    assert evaluation["decile"].between(1, 10).all()
    assert evaluation.iloc[-1]["cumulative_capture_rate"] == 1.0
    deciles = build_decile_table(evaluation)
    assert deciles["prospects"].sum() == 2
