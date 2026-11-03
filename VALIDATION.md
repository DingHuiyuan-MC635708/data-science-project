# Reproduction and data checks

Verified on **13 October 2026**.

- Downloaded DSEC's two official monthly series, indicators 14023 and 13005, for 2015–2025.
- All 264 values agree with the original project CSV.
- 132 unique and consecutive months; no missing values; visitor counts are nonnegative; occupancy rates are between 0% and 100%.
- Executed `analysis.py` in the available analysis environment.
- Created a separate clean virtual environment with Python **3.14.6**, installed only the pinned dependencies in `requirements.txt`, copied the project to another directory, and reran the script successfully.
- Full-sample and three subperiod correlations reproduce within an absolute tolerance of **1e-12**. The largest observed difference was approximately **8.9e-16**, from numerical rounding across environments.
- Generated three plots and visually inspected their titles, axes, legends, source notes, and labels.

These checks validate the included analysis against its retained official snapshot. They do not independently validate the government data collection or establish a causal relationship.

Deployment, public links, and the classmate-feedback requirement are checked separately in the Practice 09 submission checklist.

## Follow-up verification — 3 November 2026

A new isolated environment used Python 3.14.7 with the pinned requirements. `analysis.py` ran successfully: 132 months, zero duplicates or missing values, exact retained-snapshot comparisons passed, and all three figures and result tables were regenerated. Correlations reproduced as 0.946615, 0.807682, 0.769815, and 0.913474. This rerun does not refresh or independently authenticate the government dataset.

The scatter chart now reports arrivals in millions and correlation to three decimal places. The website receives the same regenerated figures.
