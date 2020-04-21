import pandas as pd

df = pd.read_csv(
      '~/data/processed_dataset.csv',
       usecols=[
         'channel_id', 
         'date_time'
       ], 
    )

def n_dupes_across_channels(df, keep):
  dupes_across_channels = df.groupby(['channel_id']).apply(
    lambda x: x.date_time.duplicated(keep=keep)
  ).sum() 
  print("Duplicates across channels:", dupes_across_channels) 
  
n_dupes_across_channels(df, False)
n_dupes_across_channels(df, "first")

def n_dupes_within_channels(df, keep):
  dupes_within_channels = df.groupby(['channel_id']).apply(
    lambda x: x.date_time.duplicated(keep=keep).sum()
  ) 
  print("Duplicates within channels:", dupes_within_channels) 

n_dupes_within_channels(df, False)
n_dupes_within_channels(df, "first")

summary = df.groupby(['channel_id']).apply(
    lambda x: pd.Series({
      "length": x.date_time.size, 
      "unique": x.date_time.nunique(),
      "duplicates": x.date_time.size -x.date_time.nunique()      
    })
)
print(summary)

mapped_df = df.groupby(['channel_id']).apply(
    lambda x: pd.DataFrame(
      data=x
    ).assign(
      duplicate = lambda x: x.date_time.duplicated(keep=False)
    ) 
) 

duplicates = mapped_df.loc[mapped_df['duplicate'] == True]
print(duplicates)
print(duplicates.duplicate.size)
