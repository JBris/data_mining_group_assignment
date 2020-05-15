import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings  
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, train_test_split, TimeSeriesSplit

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

def fit_model(df):
  def model_channel(i, model):
    #scoring
    tuned = {
      'store_precision':[True], 
      'assume_centered':[False],
      'support_fraction':[None],
      'contamination':[0.05],
      'random_state':[1234],
    }
    
    X_train, X_test = train_test_split(df.iloc[:,i:i+1].values, train_size=0.5, random_state=1234, shuffle=True)
    tss = TimeSeriesSplit(n_splits=10)
    model = GridSearchCV(
      estimator=model, 
      param_grid=tuned, 
      cv=tss,
      scoring=('r2', 'neg_mean_squared_error'),
      refit='neg_mean_squared_error',
    )
    
    model.fit(X_train, X_test)
    print("GridCV", model.cv_results_)
    pred = model.predict(df.iloc[:,i:i+1].values)
      
    test_df = pd.DataFrame()
    test_df['date_time'] = df.index
    test_df = test_df.sort_values(by='date_time')
  
    test_df['score']=model.decision_function(df.iloc[:,i:i+1].values)
    test_df['usage']=df.iloc[:,i:i+1].values
    test_df['anomaly'] = pred
    #outliers=test_df.loc[test_df['anomaly'] == -1]
    #outlier_index=list(outliers.index)
      
    channel_id = df.columns[i]
    test_df['channel_id'] = channel_id
    test_df['shift'] = test_df['usage'].shift(-1)
    test_df['percentage_change'] = ((test_df['usage'] - test_df['shift']) / test_df['usage']) * 100
    test_df = test_df.drop('shift', 1)
      
    test_df.to_csv(f"~/data/elliptic_envelope_channel_{channel_id}.csv", index=False)
    return test_df
  
  channel_id = 20
  model = EllipticEnvelope(
    store_precision = True,
    assume_centered = False,
    support_fraction = None,
    contamination = 0.005,
    random_state = 1234,
  )
  test_df = model_channel(channel_id, model)
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
