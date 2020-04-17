import os
import pandas as pd

def load_data():
    return pd.read_csv('~/data/initial_dataset.csv')
    
def struct(df):
  print(df.head())
  print()
  print(df.describe())
  print()
  print(df.columns)
  
df = load_data()
struct(df)
