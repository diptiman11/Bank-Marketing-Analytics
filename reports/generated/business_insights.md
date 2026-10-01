# Business insight summary

## Executive summary

- The dataset contains **45,211** historical campaign contacts.
- Overall term-deposit subscription rate: **11.7%**.
- Selected pre-contact model: **random_forest** (PR-AUC 0.4511, ROC-AUC 0.7967).
- Call duration is excluded from prediction because it is unavailable before contact and would leak post-call information.

## Strong observed segments

- Job: **student** — 28.7% conversion across 938 contacts.
- Job: **retired** — 22.8% conversion across 2,264 contacts.
- Job: **unemployed** — 15.5% conversion across 1,303 contacts.
- Month: **Sep** — 46.5% conversion across 579 contacts.
- Month: **Oct** — 43.8% conversion across 738 contacts.
- Month: **Apr** — 19.7% conversion across 2,932 contacts.

## Channel performance

- **cellular** — 14.9% conversion across 29,285 contacts.
- **telephone** — 13.4% conversion across 2,906 contacts.
- **unknown** — 4.1% conversion across 13,020 contacts.

## Previous campaign signal

- Previous outcome **success** — 64.7% conversion across 1,511 contacts.
- Previous outcome **other** — 16.7% conversion across 1,840 contacts.
- Previous outcome **failure** — 12.6% conversion across 4,901 contacts.
- Previous outcome **unknown** — 9.2% conversion across 36,959 contacts.

## Recommended actions

1. Use propensity scores to prioritize the top 10% of prospects, then compare conversion and contact cost against the current broad-contact strategy.
2. Treat the model as a prioritization aid rather than an automatic approval or exclusion rule.
3. Test channel and timing recommendations through a controlled campaign before operational rollout.
4. Monitor conversion, false-negative rate, segment fairness, and model drift after each campaign cycle.

## Limitations

- This is a public historical dataset from a Portuguese bank, not current Australian customer data.
- No persistent customer identifier is supplied; generated customer IDs represent campaign rows, not verified unique individuals.
- The analysis demonstrates a portfolio workflow and should not be used for real customer decisions without governance and validation.
