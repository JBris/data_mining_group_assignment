import numpy as np
import pandas as pd

df = pd.read_csv(
      '~/data/processed_dataset.csv',
       usecols=[
         'channel_id', 
         'date_time',
         'site',
         'usage',
       ], 
       parse_dates = ['date_time'],
       infer_datetime_format = True,
       dayfirst = True,
    ).assign(
      missing=False
    )

print(df)

def pad_datetime(df):
  date_range = pd.date_range(
    start = df.date_time.min(),
    end = df.date_time.max(),
    freq = "15min"
  )
  
  new_df = pd.DataFrame({
      'date_time': date_range,
      'missing': True,
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

missing = padded_df.loc[padded_df['missing'] == True]
print(missing)
missing_observation_count = missing.groupby(['channel_id']).apply(
  lambda x: x.date_time.nunique()
)
print(missing_observation_count)

padded_df.to_csv('~/data/dupes_and_missing_processed.csv', index=False)
