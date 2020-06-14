import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datawig import SimpleImputer
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import TimeSeriesSplit, train_test_split, GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, f1_score, roc_auc_score, balanced_accuracy_score

np.random.seed(10)

def pivot(df):
  channel_df = pd.pivot_table(
    df,
    values = ['usage', 'anomaly'],
    index = 'date_time',
    columns = 'channel_id'
  )
  return channel_df

def load_data():
  df = pd.read_csv(
        'data/labelled_final_processed.csv',
         parse_dates = ['date_time'],
         infer_datetime_format = True,
         dayfirst = True,
      )
      
  df.loc[df['missing'] == 1, 'usage'] = np.nan
  print( 'Missing: %d' % sum(np.isnan(df.usage)) )
  
  #Handle site 20 here
  df_20 = df.loc[df.site == 20] 
  df = df.loc[df.site != 20] 
  return df, df_20

def impute_values(df, i):
    df_model = df.loc[df.site == i]
    #Produce anomaly labels
    df_model.loc[df_model['anomaly'] == 1, 'anomaly'] = -1
    df_model.loc[df_model['anomaly']== 0, 'anomaly'] = 1
    df_model = pivot(df_model)
    scaler = StandardScaler()
    scaler.fit_transform(df_model.usage)
    df_model.loc[df_model.anomaly.isin([-1]).any(axis=1), 'anomaly'] = -1
    labels = df_model.iloc[:,0]
    print(labels)
    
    X_train, X_test, Y_train, Y_test = train_test_split(
      df_model.usage.values,
      labels.values,
      train_size=0.75,
      shuffle=False
    )
    names = df_model.usage.columns.values
    df_train = pd.DataFrame(
      data=X_train,
      columns = names,
    )
    df_train["anomaly"] = Y_train
    df_train.columns = df_train.columns.astype(str)
    df_test = pd.DataFrame(
      data=X_test,
      columns = names,
    )
    df_test["anomaly"] = Y_test
    df_test.columns = df_test.columns.astype(str)
    
    names = df_train.columns.values.tolist()
    names.remove("anomaly")
    imputer_1 = SimpleImputer(
        input_columns= names,
        output_column= names[0],
        output_path='data/imputer_model_1'
    )
    imputer_2 = SimpleImputer(
        input_columns= names,
        output_column= names[1],
        output_path='data/imputer_model_2'
    )
    print(imputer_1.__class__.__name__)
    EPOCHS=20
    imputer_1.fit(
      train_df=df_train,
      learning_rate=1e-4,
      num_epochs=EPOCHS,
    )
    imputer_2.fit(
      train_df=df_train,
      learning_rate=1e-4,
      num_epochs=EPOCHS,
    )
    clf = IsolationForest()
    clf.fit(X_train, Y_train)
    def make_prediction(title, X_test):
      print(title)
      Y_hat = clf.predict(X_test)
      pred_results = {
        'mse' : mean_squared_error(Y_test, Y_hat),
        'f1' : f1_score(Y_test, Y_hat),
        'balanced_accuracy' : balanced_accuracy_score(Y_test, Y_hat),
      }
      print(pred_results)
      
    make_prediction("Full data", X_test)
    X_test_missing = X_test
    p = 0.2
    indices = np.random.choice(np.arange(X_test_missing.size), replace=False,
                               size=int(X_test_missing.size * p))
    X_test_missing[np.unravel_index(indices, X_test_missing.shape)] = -1
    make_prediction("Missing data", X_test_missing)
    predictions_1 = imputer_1.predict(df_test)
    predictions_2 = imputer_2.predict(df_test)
    X_test_imputed = np.concatenate((predictions_1.iloc[:, 0].values.reshape(-1,1), predictions_2.iloc[:, 1].values.reshape(-1,1)), axis=1)
    make_prediction("Imputed data", X_test_imputed)

df, df_20 = load_data()
site = 5
impute_values(df, site)
