# Data dictionary

File: `macao_tourism_2015_2025.csv`.

Each row is one calendar month in Macao. Coverage: January 2015–December 2025, **132 rows**, sorted by month, without duplicates or missing values.

| Column | Type | Unit / format | Meaning | DSEC indicator |
| --- | --- | --- | --- | --- |
| `Month` | Monthly date | `YYYY-MM` | Reference month shared by the two series | API `Year` and `PeriodID` |
| `Visitor_Arrivals` | Integer | Number of arrivals | Total monthly visitor arrivals, including overnight and same-day visitors; not the number of unique people or hotel guests | 14023, total by mode of transport, `VAL` |
| `Hotel_Occupancy_Rate_Percent` | Decimal | Percent, 0–100 | Average monthly occupancy rate of guest rooms for hotel establishments in DSEC's total series; not hotel guests divided by all visitor arrivals | 13005, total average occupancy rate, `VAL` |

The values were downloaded directly from [DSEC's official Time Series Database](https://www.dsec.gov.mo/ts/) on **13 October 2026**. No imputation, interpolation, scaling, or synthetic observations were used. The two series were merged on the month with a one-to-one match. The full original response is retained in `raw/dsec_2015_2025.json`, including units, reference periods, source update timestamps, and remark fields.

`fetch_data.py` documents the API request and can refresh the data. `analysis.py` compares every CSV value against the retained response and checks month coverage and plausible ranges. Historical revisions can change a later download; review such differences rather than silently replacing published findings. Earlier provisional releases should not be mixed with this snapshot.

Source attribution and DSEC's reproduction permission are documented in the root README. The dataset contains aggregate public statistics and no personal visitor records.
