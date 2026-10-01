# Power BI build guide

## Import

Import these files from `data/powerbi/`:

- `dim_customer.csv`
- `dim_month.csv`
- `dim_channel.csv`
- `fact_campaign.csv`
- `model_scores.csv`

## Relationships

Create the following relationships:

| One side | Many side | Cardinality |
| --- | --- | --- |
| `dim_customer[customer_id]` | `fact_campaign[customer_id]` | One-to-many |
| `dim_month[month_number]` | `fact_campaign[month_number]` | One-to-many |
| `dim_channel[channel_id]` | `fact_campaign[channel_id]` | One-to-many |
| `model_scores[contact_id]` | `fact_campaign[contact_id]` | One-to-one |

Sort `dim_month[month_name]` by `dim_month[month_number]`.

## Measures

```DAX
Campaign Contacts =
COUNTROWS(fact_campaign)

Subscriptions =
SUM(fact_campaign[subscribed])

Conversion Rate =
DIVIDE([Subscriptions], [Campaign Contacts])

Average Contact Attempts =
AVERAGE(fact_campaign[campaign])

High Priority Prospects =
CALCULATE(
    COUNTROWS(model_scores),
    model_scores[priority_segment] = "High priority"
)

Average Propensity =
AVERAGE(model_scores[propensity_score])
```

## Suggested pages

### Executive overview

- KPI cards: contacts, subscriptions, conversion, average contact attempts.
- Monthly conversion line chart.
- Contact-channel conversion bar chart.
- Previous-campaign outcome matrix.

### Customer segments

- Job conversion ranking.
- Age-band conversion.
- Education and loan-status breakdown.
- Balance band and subscription matrix.

### Campaign efficiency

- Conversion by number of contact attempts.
- Channel and month comparison.
- Previous contact and previous campaign outcome.
- Tooltip with contact volume to prevent over-interpreting small segments.

### Priority list

- Priority-segment KPI cards.
- Propensity score distribution.
- Customer-level table with score, segment, job, age band, channel, and month.
- CSV export from the underlying table.

