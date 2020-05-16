import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings  
import tensorflow
from keras import regularizers
from keras.layers import LSTM, Bidirectional, Dropout, RepeatVector
from keras.layers.core import Dense
from keras.models import Model, Sequential, load_model
from numpy.random import seed
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split	
	
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

def preprocess_data(df, channel_id):
  X = df.iloc[:, channel_id : channel_id + 1]
  scaler = MinMaxScaler(feature_range=(-1, 1)) 
  X_train, X_test = train_test_split(X, train_size=0.5, random_state=1234, shuffle=False)
  X_train = scaler.fit_transform(X_train)
  X_test = scaler.transform(X_test)
  return X_train, X_test

def create_model(X_train, X_test):
  seed(1234)
  tensorflow.random.set_seed(1234)
  act_func = 'elu'
  model = Sequential()
  
  model.add(Bidirectional(
    LSTM(64, return_sequences=False), 
    input_shape=(X_train.shape[1], X_train.shape[2]),
  ))

  model.add(Dropout(0.2))
  model.add(Dense(1))

  model.add(RepeatVector(n=X_train.shape[1]))
  model.add(Bidirectional(
    LSTM(32, return_sequences=True), 
    input_shape=(X_train.shape[1], X_train.shape[2]),
  ))
  model.add(Dropout(0.2))
  model.add(Dense(1))

  model.compile(loss='mse',optimizer='adam', metrics=['mse'])
  NUM_EPOCHS=50
  BATCH_SIZE=10
  model.fit(X_train, X_train, epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, verbose=2, shuffle=True)
  return model
  
def view_anomalies(X_train, X_test, model, threshold):
  #X_pred = model.predict(X_train)
  #X_train = X_train.reshape(X_train.shape[1], 1)
  #X_pred = X_pred.reshape(X_pred.shape[1], 1)
  #X_pred = pd.DataFrame(X_pred, columns=["usage"])
  #scored = pd.DataFrame()
  #scored['Loss_mae'] = np.mean(np.abs(X_pred - X_train), axis = 1)
  #plt.figure()
  #sns.distplot(scored['Loss_mae'],
  #            bins = 10, 
  #            kde= True,
  #            color = 'blue');
  #plt.xlim([0.0,.5])
  
  X_pred = model.predict(X_test)
  X_pred = X_pred.reshape(X_pred.shape[1], 1)
  X_test = X_test.reshape(X_test.shape[1], 1)
  X_pred = pd.DataFrame(X_pred, columns=["usage"])
  scored = pd.DataFrame()
  scored['Loss_mae'] = np.mean(np.abs(X_pred-X_test), axis = 1)

  X_pred_train = model.predict(X_train)
  X_pred_train = X_pred_train.reshape(X_pred_train.shape[1], 1)
  X_train = X_train.reshape(X_train.shape[1], 1)
  X_pred_train = pd.DataFrame(X_pred_train, columns=["usage"])
  scored_train = pd.DataFrame()
  scored_train['Loss_mae'] = np.mean(np.abs(X_pred_train - X_train), axis = 1)
  scored = pd.concat([scored_train, scored])

  scored['Anomaly'] = scored['Loss_mae'] > threshold
  scored['Threshold'] = threshold
  return scored

def fit_model(df):
  # visualization
  fig, axes = plt.subplots(3, 3)
  fig.subplots_adjust(hspace=0.5)
  fig.suptitle('Outlier Threshold')

  for ax, i in zip(axes.flatten(), range(9, 18)):
    X_train, X_test = preprocess_data(df, i)
    X_train = X_train.reshape(1, X_train.shape[0], 1)
    X_test = X_test.reshape(1, X_test.shape[0], 1)

    thresholds = {
      9: 0.75, 10 : 0.95, 11 : 1, 12 : 1, 13 : 0.8, 14 : 0.8, 15 : 1, 
      16 : 1, 17 : 0.8
    }

    model = create_model(X_train, X_test)
    scored = view_anomalies(X_train, X_test, model, thresholds[i])
    scored.set_index(df.index, drop=True, inplace=True)
    print(scored['Anomaly'].value_counts())
    ax.set(title=f"Channel {i + 1}")
    a = scored.loc[scored['Anomaly'] == True] 
    ax.plot(scored.index, scored["Loss_mae"], color = 'blue', label = 'Normal')
    ax.plot(scored.index, scored["Threshold"], color = 'red', label = 'Threshold')
    ax.scatter(a.index, a['Loss_mae'], color='red', label = 'Anomaly')

  fig.text(0.04, 0.5, 'Mean Standard Error', va='center', rotation='vertical')
  plt.gcf().autofmt_xdate()
  handles, labels = ax.get_legend_handles_labels()
  plt.figlegend(handles, labels, bbox_to_anchor=(0.5, 0.5, 0.5, 0.5), loc='center right')
  plt.show();

df, df_20 = load_data()
fit_model(df)
