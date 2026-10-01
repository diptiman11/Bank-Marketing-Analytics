# Bank Marketing Analytics and Propensity Modeling

An end-to-end portfolio project that analyzes a bank's historical direct-marketing
campaigns and builds a pre-contact propensity model to prioritize prospective
customers.

The project covers data cleaning, SQL dimensional modeling, business analysis,
machine learning, model interpretation, Power BI-ready exports, and an interactive
Streamlit dashboard with English, Simplified Chinese, and Traditional Chinese
interfaces.

## Business question

A marketing team has limited calling capacity. The project asks:

1. Which customer and campaign segments historically converted at higher rates?
2. Which contact channels, months, and contact frequencies performed best?
3. Which prospects should be prioritized before the next campaign?
4. How can the recommendation remain interpretable and avoid data leakage?

## Important modeling decision

`duration` is excluded from every predictive model. Call duration is only known
after a call ends, so using it to prioritize customers before contact would leak
future information and produce unrealistic performance.

## Dataset

- Source: [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)
- Records: 45,211 campaign contacts
- Target: whether the client subscribed to a term deposit
- License: CC BY 4.0

This is public historical data from a Portuguese banking institution. It is not
current Australian banking data and does not contain real identifiers.

## Architecture

```text
UCI CSV
  -> Python validation and feature engineering
  -> clean analytical dataset
  -> Power BI-ready star-schema CSVs
  -> pre-contact propensity models
  -> priority segments, model evidence, business report
  -> Streamlit dashboard
```

## Project structure

```text
data/raw/          Source files and data dictionary
data/processed/    Clean data and quality checks (generated)
data/powerbi/      Fact/dimension tables and model scores (generated)
dashboard/         Interactive Streamlit application
models/            Trained model artifact (generated)
reports/generated/ Model metrics and business findings (generated)
sql/               PostgreSQL schema and analysis queries
src/               Reproducible pipeline, modeling, and reporting code
tests/             Pipeline tests
```

## Quick start

```bash
make setup
make all
make dashboard
```

Then open the local URL printed by Streamlit, normally
`http://localhost:8501`.

## Generated outputs

- `data/processed/bank_marketing_clean.csv`
- `data/processed/data_quality_summary.csv`
- `data/powerbi/dim_customer.csv`
- `data/powerbi/dim_month.csv`
- `data/powerbi/dim_channel.csv`
- `data/powerbi/fact_campaign.csv`
- `data/powerbi/model_scores.csv`
- `data/powerbi/evaluation_predictions.csv`
- `reports/generated/model_comparison.csv`
- `reports/generated/decile_performance.csv`
- `reports/generated/feature_importance.csv`
- `reports/generated/business_insights.md`
- `models/propensity_model.joblib`

## Power BI setup

Import the CSV files in `data/powerbi/` and create these relationships:

- `dim_customer[customer_id]` 1 -> many `fact_campaign[customer_id]`
- `dim_month[month_number]` 1 -> many `fact_campaign[month_number]`
- `dim_channel[channel_id]` 1 -> many `fact_campaign[channel_id]`
- `model_scores[contact_id]` 1 -> 1 `fact_campaign[contact_id]`

Suggested report pages:

1. Executive overview
2. Customer segments
3. Channel and campaign analysis
4. Propensity and priority list

Useful DAX measures:

```DAX
Campaign Contacts = COUNTROWS(fact_campaign)
Subscriptions = SUM(fact_campaign[subscribed])
Conversion Rate = DIVIDE([Subscriptions], [Campaign Contacts])
Average Contact Attempts = AVERAGE(fact_campaign[campaign])
High Priority Prospects =
    CALCULATE(
        COUNTROWS(model_scores),
        model_scores[priority_segment] = "High priority"
    )
```

## Model evaluation

The pipeline compares class-weighted logistic regression and random forest.
The selected model is based on PR-AUC because only about 12% of contacts result
in subscription. Precision, recall, F1, ROC-AUC, confusion matrix, and a
recall-oriented F2 threshold are also recorded.

Current reproducible results:

| Model | ROC-AUC | PR-AUC | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic regression | 0.7536 | 0.3709 | 0.2393 | 0.6604 | 0.3513 |
| Random forest | **0.7967** | **0.4511** | **0.3292** | 0.6452 | **0.4360** |

The random forest is selected for scoring. At the recall-oriented threshold it
identifies 64.5% of historical subscribers while materially improving precision
over logistic regression.

The dashboard also evaluates model ranking on the independent test set through:

- cumulative gain and random-targeting comparison;
- score-decile response rates and lift;
- a campaign-capacity simulator that compares model-ranked targeting with the
  expected result of random targeting;
- downloadable high-, medium-, and low-priority prospect lists.

Dashboard language can be changed between English, Simplified Chinese, and
Traditional Chinese. The selected locale is preserved in the `lang` URL
parameter.

## Selected findings

- Overall historical subscription rate: **11.7%**.
- Student and retired segments recorded the strongest conversion among
  sufficiently large job groups.
- Cellular contacts converted at **14.9%**, compared with **4.1%** where the
  contact channel was unknown.
- A successful previous campaign outcome was the strongest historical signal,
  with **64.7%** conversion in that segment.

These are descriptive historical associations and should be validated through
controlled campaigns before operational use.

## Limitations and responsible use

- Generated customer IDs represent campaign rows because the source data has no
  persistent customer identifier.
- Historical associations are not proof of causation.
- The model is a prioritization demonstration, not an automated eligibility or
  credit decision system.
- Real deployment would require consent, governance, fairness review, drift
  monitoring, and validation using current local data.

## Attribution

Moro, S., Rita, P., and Cortez, P. (2014). Bank Marketing. UCI Machine Learning
Repository. https://doi.org/10.24432/C5K306
