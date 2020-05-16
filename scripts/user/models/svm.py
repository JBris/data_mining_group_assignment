import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings  
from sklearn.svm import OneClassSVM
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
        '../data/final_processed.csv',
         parse_dates = ['date_time'],
         infer_datetime_format = True,
         dayfirst = True,
      )
      
  print(df)
  
  #Handle site 20 here
  df_20 = df.loc[df.site == 20] 
  #df = df.loc[df.site != 20] 
  return pivot(df), pivot(df_20)

def fit_model(df):
  model = OneClassSVM(
    nu=0.05, 
    kernel="rbf", 
    gamma='scale',
    cache_size = 500
  )
  
  def model_channel(i):
    model.fit(df.iloc[:,i:i+1].values)
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
      
    test_df.to_csv(f"../data/svm_channel_{channel_id}.csv", index=False)
    return test_df
    
  # visualization
  fig, axes = plt.subplots(3, 3)
  fig.subplots_adjust(hspace=0.5)
  fig.suptitle('Outliers by Channel')
  for ax, i in zip(axes.flatten(), range(18, 27)):
    test_df = model_channel(i)
    print(test_df['anomaly'].value_counts())
    ax.set(title=f"Channel {i + 1}")
    #X_train, X_test = train_test_split(test_df, train_size=(2/3), random_state=1234, shuffle=False)
    a = test_df.loc[test_df['anomaly'] == -1, ['date_time', 'usage']] #anomaly
    ax.plot(test_df['date_time'], test_df['usage'], color='blue', label = 'Normal')
    ax.scatter(a['date_time'],a['usage'], color='red', label = 'Anomaly')
    
  plt.gcf().autofmt_xdate()
  handles, labels = ax.get_legend_handles_labels()
  plt.figlegend(handles, labels, bbox_to_anchor=(0.5, 0.5, 0.5, 0.5), loc='center right')
  plt.show();

df, df_20 = load_data()
fit_model(df)
