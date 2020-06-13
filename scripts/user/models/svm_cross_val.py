import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings  
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, f1_score, roc_auc_score, balanced_accuracy_score
from sklearn.model_selection import GridSearchCV, train_test_split, TimeSeriesSplit

def pivot(df):
  channel_df = pd.pivot_table(
    df,
    values = ['usage', 'anomaly'],
    index = 'date_time',
    columns = 'channel_id'
  )
  channel_df.fillna(0, inplace=True)
  print(channel_df)
  return channel_df

def load_data():
  df = pd.read_csv(
        'data/labelled_final_processed.csv',
         parse_dates = ['date_time'],
         infer_datetime_format = True,
         dayfirst = True,
      )
      
  print(df)
  
  #Handle site 20 here
  df_20 = df.loc[df.site == 20] 
  df = df.loc[df.site != 20] 
  return df, df_20


def fit_model(df):
  def model_channel(i):
    df_model = df.loc[df.site == i]
    
    #Produce anomaly labels
    df_model.loc[df_model['anomaly'] == 1, 'anomaly'] = -1
    df_model.loc[df_model['anomaly']== 0, 'anomaly'] = 1
    df_model = pivot(df_model)
    scaler = StandardScaler()
    scaler.fit_transform(df_model.usage)
    print(df_model)
    df_model.loc[df_model.anomaly.isin([-1]).any(axis=1), 'anomaly'] = -1
    labels = df_model.iloc[:,0]
    print(labels)
    
    #params
    param_grid = {
      'kernel':['linear', 'poly', 'rbf', 'sigmoid'],
      'gamma':['scale'],
      'nu':[.5, .75, .9],
      'max_iter':[-1],
    }
    
    X_train, X_test, Y_train, Y_test = train_test_split(
      df_model.usage.values, 
      labels.values, 
      train_size=0.75, 
      shuffle=False
    )
    cv = TimeSeriesSplit(n_splits=3)
    clf = GridSearchCV(
      estimator=OneClassSVM(),
      param_grid=param_grid,
      cv=cv,
      scoring=['neg_mean_squared_error', 'f1'],
      refit='neg_mean_squared_error'
    )
    clf.fit(X_train, Y_train)
    
    scoring_params = ["mean_fit_time", "mean_score_time", "mean_test_f1", "rank_test_f1", "mean_test_neg_mean_squared_error", 
      "rank_test_neg_mean_squared_error"]
    scoring_params_df = [ pd.DataFrame(clf.cv_results_["params"]) ]
    for param in scoring_params: 
      scoring_params_df.append( pd.DataFrame(clf.cv_results_[param], columns=[param]) )
    tuning_results = pd.concat(scoring_params_df, axis = 1)
    print(tuning_results)
    tuning_results.to_csv(f"~/data/svm_tuning_results.csv", index=False)
    Y_hat = clf.predict(X_test)
    pred_results = {
      'mse' : mean_squared_error(Y_test, Y_hat),
      'f1' : f1_score(Y_test, Y_hat),
      'roc_auc': roc_auc_score(Y_test, clf.decision_function(X_test)),
      'balanced_accuracy' : balanced_accuracy_score(Y_test, Y_hat),
    }
    print(pred_results)
    
  site = 14
  model_channel(site)

df, df_20 = load_data()
fit_model(df)
