"""Reproduce Macao tourism analysis from a frozen DSEC snapshot."""
import os
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache' / 'matplotlib'))
import matplotlib
matplotlib.use('Agg')
for folder in ('figures', 'results'):
    (ROOT / folder).mkdir(exist_ok=True)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

plt.style.use('seaborn-v0_8-whitegrid')
pd.set_option('display.max_columns', None)

# Load the verified merged dataset using a relative path.
data_path = ROOT / 'data' / 'macao_tourism_2015_2025.csv'
df = pd.read_csv(data_path, parse_dates=['Month'])
df.head()

# Verify structure, date coverage, duplicate months, and missing values.
print('Shape:', df.shape)
print('Date range:', df['Month'].min().strftime('%Y-%m'), 'to', df['Month'].max().strftime('%Y-%m'))
print('Duplicate months:', df['Month'].duplicated().sum())
print('Missing values:')
print(df.isna().sum())

assert len(df) == 132, 'Expected 132 monthly observations.'
assert df['Month'].is_unique, 'Each month should appear exactly once.'
assert not df.isna().any().any(), 'The study dataset should not contain missing values.'

# Descriptive statistics for the two variables.
df[['Visitor_Arrivals', 'Hotel_Occupancy_Rate_Percent']].describe().round(2)

# Figure 1: aligned time-series panels.
fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
fig.subplots_adjust(left=0.11, right=0.98, top=0.90, bottom=0.15, hspace=0.08)

for ax in axes:
    ax.axvspan(pd.Timestamp('2020-01-01'), pd.Timestamp('2022-12-31'),
               color='lightgray', alpha=0.55, label='COVID-19 period (2020–2022)')

axes[0].plot(df['Month'], df['Visitor_Arrivals'], color='#1769aa', linewidth=2)
axes[0].set_title('Monthly Visitor Arrivals and Hotel Occupancy in Macao, 2015–2025',
                  fontsize=16, fontweight='bold')
axes[0].set_ylabel('Visitor arrivals')
axes[0].legend(loc='lower left')
axes[0].ticklabel_format(axis='y', style='plain')

axes[1].plot(df['Month'], df['Hotel_Occupancy_Rate_Percent'],
             color='#e4572e', linewidth=2)
axes[1].set_ylabel('Hotel occupancy rate (%)')
axes[1].set_xlabel('Month')
axes[1].set_ylim(0, 100)
axes[1].set_xlim(pd.Timestamp('2015-01-01'), pd.Timestamp('2025-12-01'))
axes[1].xaxis.set_major_locator(mdates.YearLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.setp(axes[1].get_xticklabels(), rotation=45, ha='right')

fig.text(0.01, 0.02,
         'Source: Macao Statistics and Census Service (DSEC), monthly time series; API snapshot retrieved 13 Oct 2026.',
         fontsize=9, color='#555555')
fig.savefig(ROOT / 'figures' / '01_monthly_trends.png', dpi=160)
plt.close(fig)

# Calculate Pearson correlation and prepare the fitted line.
correlation = df['Visitor_Arrivals'].corr(df['Hotel_Occupancy_Rate_Percent'])
slope, intercept = np.polyfit(df['Visitor_Arrivals'],
                              df['Hotel_Occupancy_Rate_Percent'], 1)
x_line = np.linspace(df['Visitor_Arrivals'].min(), df['Visitor_Arrivals'].max(), 200)
y_line = slope * x_line + intercept
print(f'Pearson correlation for all 132 months: r = {correlation:.3f}')

# Figure 2: scatter plot with the COVID-19 period distinguished.
covid_period = df['Month'].dt.year.between(2020, 2022)

fig, ax = plt.subplots(figsize=(11, 7.5))
fig.subplots_adjust(left=0.12, right=0.98, top=0.89, bottom=0.17)
ax.scatter(df.loc[~covid_period, 'Visitor_Arrivals'],
           df.loc[~covid_period, 'Hotel_Occupancy_Rate_Percent'],
           s=55, color='#1769aa', alpha=0.75,
           label='2015–2019 and 2023–2025')
ax.scatter(df.loc[covid_period, 'Visitor_Arrivals'],
           df.loc[covid_period, 'Hotel_Occupancy_Rate_Percent'],
           s=60, color='#e4572e', alpha=0.85,
           label='COVID-19 period (2020–2022)')
ax.plot(x_line, y_line, color='#333333', linewidth=2, label='Fitted linear trend')

ax.set_title('Visitor Arrivals and Hotel Occupancy in Macao, 2015–2025',
             fontsize=16, fontweight='bold')
ax.set_xlabel('Monthly visitor arrivals')
ax.set_ylabel('Hotel occupancy rate (%)')
ax.set_ylim(0, 100)
ax.legend(loc='lower right')
ax.text(0.02, 0.96, f'Pearson correlation: r = {correlation:.2f}',
        transform=ax.transAxes, va='top',
        bbox=dict(facecolor='white', alpha=0.9, edgecolor='#aaaaaa'))
fig.text(0.01, 0.025,
         'Source: Macao Statistics and Census Service (DSEC), monthly time series; API snapshot retrieved 13 Oct 2026.',
         fontsize=9, color='#555555')
fig.savefig(ROOT / 'figures' / '02_arrivals_vs_occupancy.png', dpi=160)
plt.close(fig)

# Check the local CSV against the complete retained official response.
raw = json.loads((ROOT / 'data/raw/dsec_2015_2025.json').read_text())
assert raw['Status'] == 'OK'
for series in raw['Value']:
    column = 'Visitor_Arrivals' if series['indicatorId'] == 14023 else 'Hotel_Occupancy_Rate_Percent'
    values = pd.DataFrame(series['dsecIndicatorData'])
    values['Month'] = pd.to_datetime(dict(year=values.Year, month=values.PeriodID, day=1))
    joined = df.merge(values[['Month', 'IndicatorValue']], on='Month', validate='one_to_one')
    assert len(joined) == 132
    assert np.allclose(joined[column], joined.IndicatorValue, rtol=0, atol=0)
assert df.Month.sort_values().tolist() == pd.date_range('2015-01-01', '2025-12-01', freq='MS').tolist()
assert (df.Visitor_Arrivals >= 0).all()
assert df.Hotel_Occupancy_Rate_Percent.between(0, 100).all()

periods = [('All months: 2015–2025', 2015, 2025), ('2015–2019', 2015, 2019),
           ('2020–2022', 2020, 2022), ('2023–2025', 2023, 2025)]
rows = []
for label, start, end in periods:
    part = df[df.Month.dt.year.between(start, end)]
    rows.append({'period': label, 'months': len(part),
                 'pearson_r': part.Visitor_Arrivals.corr(part.Hotel_Occupancy_Rate_Percent)})
summary = pd.DataFrame(rows)
summary.to_csv(ROOT / 'results/correlations.csv', index=False)
df[['Visitor_Arrivals', 'Hotel_Occupancy_Rate_Percent']].describe().to_csv(ROOT / 'results/descriptive_statistics.csv')
fig, ax = plt.subplots(figsize=(10, 5.5))
colors = ['#1769aa', '#56a0cf', '#e4572e', '#2a9d8f']
bars = ax.bar(summary.period, summary.pearson_r, color=colors, width=0.62)
ax.set_ylim(0, 1.05)
ax.set_ylabel('Pearson correlation (r)')
ax.set_title('Association varies across periods', fontsize=16, fontweight='bold')
for bar, row in zip(bars, rows):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.025,
            f"{row['pearson_r']:.3f} (n={row['months']})", ha='center', fontsize=10)
fig.text(0.02, 0.025, 'Source: DSEC official monthly series, retrieved 13 Oct 2026. Correlation does not establish causation.', fontsize=9)
fig.tight_layout(rect=[0, 0.06, 1, 1])
fig.savefig(ROOT / 'figures/03_period_correlations.png', dpi=160)
plt.close(fig)
(ROOT / 'results/metrics.json').write_text(json.dumps({'observations': len(df), 'start': '2015-01', 'end': '2025-12', 'period_correlations': rows}, indent=2))
print(summary.to_string(index=False))
print('All data checks passed. Three figures and result tables saved.')
