import pandas as pd

def load_data():
    return pd.read_csv(
      '~/data/initial_dataset.csv',
      dtype={
        "Load Main Incomer": "object",
      }
    )
    
def rename_columns(df):
  #Rename columns. Remove spaces and make all lowercase.
  df.columns = df.columns.str.replace(' ', '_')
  df.columns = df.columns.str.lower()
  print(df.columns)
  return df
  
def convert_load_main_incomer(df):
  # Replace Load Main Incomer strings with 1 or 0
  print(df.load_main_incomer)
  df.loc[df.load_main_incomer == "TRUE", 'load_main_incomer'] = 1
  df.loc[df.load_main_incomer == "FALSE", 'load_main_incomer'] = 0
  return df

def drop_columns(df):
  #Drop unneeded columns
  cols = [
    'channel_unit', 
    'channel_interval_frequency', 
    'load_utility', 
    'load_main_incomer', 
    #'channel_key'
  ]
  df = df.drop(cols, 1)
  print(df.columns)
  return df
  
def site_to_factor(df):
  #Convert the site column to a factor.
  def to_factor(ele):
    ele = ele.lower()
    ele = ele.replace('site', '')
    ele = ele.strip()
    return ele
  def chan_to_factor(ele):
    ele = ele.lower()
    ele = ele.replace('activeenergy', '')
    ele = ele.strip()
    return ele
    
  df.site = df.site.apply(to_factor)
  df.channel_key = df.channel_key.apply(chan_to_factor)
  
  print(df.site)
  return df

def factorize_channel_columns(df):
  cols = ['channel_id']
  df[cols] = df[cols].apply(lambda x: pd.factorize(x)[0])
  return df

def create_channel_tuple_factor(df):
  channel_tupple = list(zip(df.channel_id, df.channel_key))
  df['channel_pair'] = pd.Series(channel_tupple).factorize()[0]
  return df
  
df = load_data()
df = rename_columns(df)
df = drop_columns(df)
df = site_to_factor(df)
df = factorize_channel_columns(df)
df.to_csv('~/data/processed_dataset.csv', index=False)
