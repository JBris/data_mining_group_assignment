import datetime
import numpy as np
import pandas as pd
from datetime import datetime

df = pd.read_csv(
      '~/data/processed_dataset.csv',
       usecols=[
         'channel_id', 
         'date_time',
         'site',
         'usage',
       ], 
       parse_dates = ['date_time'], 
       date_parser = lambda s: datetime.strptime(s,'%d/%m/%Y %H:%M'),
       dayfirst = True,
    )

df["missing"] = pd.isna(df.usage).astype(int)
print(df)

#Daylight savings
#Start: 2019-04-07 02:00:00
#End: 2019-09-29 02:45:00
df.loc[ (df['date_time'] >= '2019-04-07 03:00:00') & (df['date_time'] <= '2019-09-29 01:45:00'), 'date_time' ] =  df['date_time'] + pd.to_timedelta(1, unit='h')

def shift_dupes(df): 
  df.loc[df.date_time.duplicated(keep='first'), 'date_time'] = df['date_time'] + pd.to_timedelta(1, unit='h')
  return df
  
df = df.groupby('channel_id').apply(shift_dupes)

def pad_datetime(df):
  date_range = pd.date_range(
    start = df.date_time.min(),
    end = df.date_time.max(),
    freq = "15min"
  )
  
  new_df = pd.DataFrame({
      'date_time': date_range,
      'missing': 1,
      'site': df.site.iloc[0],
      'channel_id': df.channel_id.iloc[0],
    },
    index=date_range
  )
  
  return df.merge(
    new_df,
    on=["date_time", "missing", "site", "channel_id"],
    how="outer",
  ).drop_duplicates(["date_time"])
  
padded_df = df.sort_values([
  'channel_id',
  'date_time'
]).groupby(
  'channel_id'
).apply(pad_datetime).reset_index(
  drop=True
)

print(padded_df)

summary = padded_df.groupby(['site', 'channel_id']).apply(
    lambda x: pd.Series({
      "length": x.date_time.size, 
      "unique": x.date_time.nunique(),
      "duplicates": x.date_time.size -x.date_time.nunique()      
    })
)
print(summary)

missing = padded_df.loc[padded_df['missing'] == 1]
print(missing)
missing_observation_count = missing.groupby(['channel_id']).apply(
  lambda x: x.date_time.nunique()
)
print(missing_observation_count)

padded_df['month'] = padded_df.date_time.dt.month
padded_df['day'] = padded_df.date_time.dt.day
padded_df['hour'] = padded_df.date_time.dt.hour
padded_df['minute'] = padded_df.date_time.dt.minute

padded_df.to_csv('~/data/final_processed.csv', index=False)
