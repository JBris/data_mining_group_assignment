import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings  
from pyemma import msm
from sklearn.preprocessing import StandardScaler

def pivot(df):
  channel_df = pd.pivot_table(
    df,
    values = 'usage',
    index = 'date_time',
    columns ='channel_id'
  )
  #channel_df.fillna(0, inplace=True)
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

def get_transition_matrix(series):
  series = np.array(series)
  model = msm.estimate_markov_model(series, 1)
  return model.transition_matrix
  
def success_probability_metric(state1, state2, transition_matrix):
  proba = 0
  for k in range(0, len(transition_matrix)):
    if (k != (state2 - 1)):
      proba += transition_matrix[state1-1][k]
  return 1 - proba

def success_score(sequence, transition_matrix):
  proba = 0
  for i in range(1, len(sequence)):
    if(i == 1):
      proba = success_probability_metric(sequence[i-1], sequence[i], transition_matrix)
    else:
      proba = proba * success_probability_metric(sequence[i-1], sequence[i], transition_matrix)
  return proba

def anomaly_element(sequence, threshold, transition_matrix):
  if (success_score(sequence, transition_matrix) > threshold):
    return 0
  else: 
    return -1

def markov_anomaly(series, windows_size, threshold):
  transition_matrix = get_transition_matrix(series)
  real_threshold = threshold**windows_size
  df_anomaly = []
  
  for j in range(0, len(series)):
    if (j < windows_size):
      df_anomaly.append(0)
    else:
      start_index = j - windows_size
      sequence = series[start_index:j]
      sequence.reset_index(inplace=True, drop=True)
      df_anomaly.append(anomaly_element(sequence, real_threshold, transition_matrix))
  return df_anomaly
  
def fit_model(df):

  def model_channel(i):
    X = df.iloc[:,i:i+1]
    quintiles = np.percentile( X, [20, 40, 60, 80] )   
    x1 = (X <= quintiles[0]) 
    x2= ((X > quintiles[0]) & (X <= quintiles[1])) 
    x3 = ((X > quintiles[1]) & (X <= quintiles[2])) 
    x4 = ((X > quintiles[2]) & (X <= quintiles[3])) 
    x5 = (X > quintiles[3]) 
    df_mm = x1 + 2 * x2 + 3 * x3 + 4 * x4 + 5 * x5
    df_mm.rename(columns={ i :'usage'}, inplace=True)
    df_mm.reset_index(inplace=True)
    pred = markov_anomaly(df_mm.usage, 4, 0.2)
    pred = pd.Series(pred)
    
    test_df = pd.DataFrame()
    test_df['date_time'] = df.index
    test_df = test_df.sort_values(by='date_time')
  
    test_df['usage']= X.values
    test_df['anomaly'] = pred
    #outliers=test_df.loc[test_df['anomaly'] == -1]
    #outlier_index=list(outliers.index)
    channel_id = df.columns[i]
    test_df['channel_id'] = channel_id
    test_df.to_csv(f"~/data/markov_chain_channel_{channel_id}.csv", index=False)
    return test_df
    
  channel_id = 20
  test_df = model_channel(channel_id)
  print(test_df['anomaly'].value_counts())
  print(test_df)
  
  # visualization
  fig, ax = plt.subplots(figsize=(10, 6))
  fig.suptitle(f"Anomalies for Channel {channel_id}")
  a = test_df.loc[test_df['anomaly'] == -1, ['date_time', 'usage']] #anomaly
  ax.plot(test_df['date_time'], test_df['usage'], color='blue', label = 'Normal')
  ax.scatter(a['date_time'],a['usage'], color='red', label = 'Anomaly')
  plt.legend()
  plt.show();

df, df_20 = load_data()
fit_model(df)
