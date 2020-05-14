import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import warnings  
import hdbscan
from sklearn.preprocessing import StandardScaler

def pivot(df):
  channel_df = pd.pivot_table(
    df,
    values = 'usage',
    index = 'date_time',
    columns ='channel_id'
  )
  channel_df.fillna(0, inplace=True)
  print(channel_df)
  return channel_df

def load_data():
  df = pd.read_csv(
        '~/data/final_processed.csv',
         parse_dates = ['date_time'],
         infer_datetime_format = True,
         dayfirst = True,
      )
      
  print(df)
  
  #Handle site 20 here
  df_20 = df.loc[df.site == 20] 
  df = df.loc[df.site != 20] 
  return pivot(df), pivot(df_20)

def fit_model(df):
  channel = 20
  model = hdbscan.HDBSCAN(
    algorithm='best', 
    #alpha=1.0, 
    approx_min_span_tree=True,
    gen_min_span_tree=False, 
    leaf_size = 50, 
    #memory=Memory(cachedir=None),
    metric='euclidean', 
    min_cluster_size= 4 * 24 * 14, 
    min_samples= 4 * 24, 
    #p=None,
    core_dist_n_jobs = -1,
    cluster_selection_method = "leaf",
    cluster_selection_epsilon = 0.15,
  )
  
  def model_channel(i):
    model.fit(df.iloc[:,i:i+1].values)
    pred = model.fit_predict(df.iloc[:,i:i+1].values)
      
    test_df = pd.DataFrame()
    test_df['date_time'] = df.index
    test_df = test_df.sort_values(by='date_time')
  
    test_df['score']=model.outlier_scores_
    test_df.score.fillna(0, inplace=True)
    test_df['usage']=df.iloc[:,i:i+1].values
    test_df['anomaly'] = pred
    test_df.loc[test_df.anomaly >= 0, 'anomaly'] = 1
    #outliers=test_df.loc[test_df['anomaly'] == -1]
    #outlier_index=list(outliers.index)
      
    channel_id = df.columns[i]
    test_df['channel_id'] = channel_id
    test_df['shift'] = test_df['usage'].shift(-1)
    test_df['percentage_change'] = ((test_df['usage'] - test_df['shift']) / test_df['usage']) * 100
    test_df = test_df.drop('shift', 1)
      
    test_df.to_csv(f"~/data/hdbscan_channel_{channel_id}.csv", index=False)
    return test_df
    
  test_df = model_channel(channel)
  print(test_df['anomaly'].value_counts())
  print(test_df)
  
  # visualization
  channel_id = test_df.channel_id.values[0]
  fig, ax = plt.subplots(figsize=(10, 6))
  fig.suptitle(f"Anomalies for Channel {channel_id}")
  a = test_df.loc[test_df['anomaly'] == -1, ['date_time', 'usage']] #anomaly
  ax.plot(test_df['date_time'], test_df['usage'], color='blue', label = 'Normal')
  ax.scatter(a['date_time'],a['usage'], color='red', label = 'Anomaly')
  plt.legend()
  plt.show();
  
df, df_20 = load_data()
fit_model(df)
