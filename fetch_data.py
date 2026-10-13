"""Download the two public DSEC series and merge them by month.

Optional refresh: python fetch_data.py
The normal analysis uses the included frozen data and does not need network access.
"""
import json
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
URL = 'https://www.dsec.gov.mo/TimeSeriesApi/App/IndicatorValue/LatestSameEndPeriodv3'
PAYLOAD = {'indicator_ids': [14023, 13005], 'language': 'en-US',
           'types': ['VAL', 'VAL'], 'dataPeriods': ['Monthly'],
           'fromYear': 2015, 'toYear': 2025}

request = urllib.request.Request(URL, data=json.dumps(PAYLOAD).encode(),
                                 headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(request, timeout=60) as response:
    raw = json.load(response)
if raw.get('Status') != 'OK':
    raise RuntimeError('DSEC did not return a successful data response.')
frames = []
for series in raw['Value']:
    indicator = series['indicatorId']
    if indicator not in (14023, 13005):
        raise ValueError(f'Unexpected indicator: {indicator}')
    df = pd.DataFrame(series['dsecIndicatorData'])
    df['Month'] = pd.to_datetime(dict(year=df.Year, month=df.PeriodID, day=1))
    column = 'Visitor_Arrivals' if indicator == 14023 else 'Hotel_Occupancy_Rate_Percent'
    frames.append(df[['Month', 'IndicatorValue']].rename(columns={'IndicatorValue': column}))
if len(frames) != 2:
    raise ValueError('Expected two series.')
merged = frames[0].merge(frames[1], on='Month', validate='one_to_one').sort_values('Month')
expected = pd.date_range('2015-01-01', '2025-12-01', freq='MS')
if merged.Month.tolist() != expected.tolist() or merged.isna().any().any():
    raise ValueError('Unexpected missing values or date coverage.')
merged['Visitor_Arrivals'] = merged.Visitor_Arrivals.astype('int64')
(ROOT / 'data/raw').mkdir(parents=True, exist_ok=True)
(ROOT / 'data/raw/dsec_2015_2025.json').write_text(json.dumps(raw, ensure_ascii=False, indent=2))
merged.to_csv(ROOT / 'data/macao_tourism_2015_2025.csv', index=False, date_format='%Y-%m')
print('Saved 132 matched months. DSEC may revise historical data; review changes before committing.')
