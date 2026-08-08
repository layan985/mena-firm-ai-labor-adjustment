# Core data dictionary

| Variable | Level | Definition | Treatment status |
|---|---|---|---|
| `firm_id` | firm | stable internal identifier | key |
| `year` | firm-year | fiscal year | time |
| `country` | firm | ISO3 country | FE / heterogeneity |
| `sector` | firm-year | harmonized ISIC/ICB sector | controls |
| `employee_count` | firm-year | permanent/full-time headcount where possible | outcome |
| `personnel_expense` | firm-year | annual staff/personnel cost in local currency | outcome |
| `temporary_workers` | firm-year | temporary/seasonal headcount where available | outcome |
| `female_employment_share` | firm-year | female workers / total workers | outcome / heterogeneity |
| `training_any` | firm-year | firm reports formal employee training | outcome |
| `ai_score` | firm-year | 0–3 substantiveness score | treatment measurement |
| `ai_category` | firm-year | functional AI use | heterogeneity |
| `first_ai_year` | firm | first validated year with `ai_score >= 2` | event time |
| `pre_ai_exposure` | firm | predetermined exposure measure built using pre-2022 info | treatment intensity |
| `report_sha256` | document | hash of source report | provenance |
| `evidence_hash` | observation | hash of evidence passage | provenance |
