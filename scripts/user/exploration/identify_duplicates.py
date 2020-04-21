import pandas as pd

df = pd.read_csv(
      '~/data/processed_dataset.csv',
       usecols=[
         'channel_id', 
         'date_time'
       ], 
    )

def n_dupes_across_channels(df, keep):
  dupes_across_channels= df.groupby(['channel_id']).apply(
    lambda date_time: date_time.duplicated(keep=keep)
  ).sum() 
  print("Duplicates across channels:", dupes_across_channels) 
  
n_dupes_across_channels(df, False)
n_dupes_across_channels(df, "first")

def n_dupes_within_channels(df, keep):
  dupes_within_channels = df.groupby(['channel_id']).apply(
    lambda date_time: date_time.duplicated(keep=keep).sum()
  ) 
  print("Duplicates within channels:", dupes_within_channels) 

n_dupes_within_channels(df, False)
n_dupes_within_channels(df, "first")
