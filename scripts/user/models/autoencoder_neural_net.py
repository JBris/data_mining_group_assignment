import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings  
import tensorflow  
from keras import regularizers, Input
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
  X_train, X_test = train_test_split(X, train_size=0.7, random_state=1234, shuffle=True)
  X_train = scaler.fit_transform(X_train)
  X_test = scaler.transform(X_test)
  return X_train, X_test

def create_model(X_train, X_test):
  seed(1234)
  tensorflow.random.set_seed(1234)
  act_func = 'relu'
  model = Sequential()
  input_shape = (4 * 60 * 24, 1)
  input_layer = Input(shape=input_shape)
  
  model.add(Bidirectional(
    LSTM(
      128,
      activation=act_func,
      input_shape=input_shape,
      return_sequences=False,
    )
  ))
  
  model.add(Dropout(0.2))
  model.add(RepeatVector(n=X_train.shape[1]))
  model.add(Bidirectional(
    LSTM(
      128,
      activation=act_func,
      input_shape=input_shape,
      return_sequences=False,
    )
  ))
  model.add(Dropout(0.2))

  model.add(Dense(
    units=15 * 24, 
    activation=act_func,
    input_shape=input_shape,
    kernel_initializer='glorot_uniform',
    kernel_regularizer=regularizers.l2(0.0)
  ))
  
  model.add(Dense(
    units=1, 
    activation='softmax',
    kernel_initializer='glorot_uniform',
  ))
  
  model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['mse'])
  NUM_EPOCHS=50
  BATCH_SIZE=10
  return model
  
def view_anomalies(X_train, X_test, model):
  X_pred = model.predict(X_train)
  X_train = X_train.reshape(len(X_train), 1)
  X_pred = pd.DataFrame(X_pred, columns=["usage"])

  scored = pd.DataFrame()
  scored['Loss_mae'] = np.mean(np.abs(X_pred - X_train), axis = 1)
  plt.figure()
  sns.distplot(scored['Loss_mae'],
              bins = 10, 
              kde= True,
              color = 'blue');
  plt.xlim([0.0,.5])

  X_pred = model.predict(X_test)
  X_test = X_test.reshape(len(X_test), 1)
  X_pred = pd.DataFrame(X_pred, 
                        columns=["usage"])

  scored = pd.DataFrame()
  scored['Loss_mae'] = np.mean(np.abs(X_pred-X_test), axis = 1)
  scored['Threshold'] = 0.3
  scored['Anomaly'] = scored['Loss_mae'] > scored['Threshold']
  print(scored.head())

  X_train = X_train.reshape(len(X_train), 1, 1)
  X_pred_train = model.predict(np.array(X_train))
  X_train = X_train.reshape(len(X_train), 1)
  X_pred_train = pd.DataFrame(X_pred_train, 
                        columns=["usage"])

  scored_train = pd.DataFrame()
  scored_train['Loss_mae'] = np.mean(np.abs(X_pred_train - X_train), axis = 1)
  scored_train['Threshold'] = 0.3
  scored_train['Anomaly'] = scored_train['Loss_mae'] > scored_train['Threshold']
  scored = pd.concat([scored_train, scored])

  scored.plot(logy=True,  figsize = (10,6), ylim = [1e-2,1e2], color = ['blue','red'])
  plt.show()

channel_id = 20  
df, df_20 = load_data()
X_train, X_test = preprocess_data(df, channel_id)
X_train = X_train.reshape(len(X_train), 1, 1)
X_test = X_test.reshape(len(X_test), 1, 1)
model = create_model(X_train, X_test)
view_anomalies(X_train, X_test, model)
