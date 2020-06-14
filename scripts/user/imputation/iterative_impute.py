import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer
from sklearn.model_selection import TimeSeriesSplit, train_test_split, GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, f1_score, roc_auc_score, balanced_accuracy_score
from scipy.stats import bernoulli as bn

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
        '../data/labelled_final_processed.csv',
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
    print(df_model)
    df_model.loc[df_model.anomaly.isin([-1]).any(axis=1), 'anomaly'] = -1
    
    labels = df_model.iloc[:,0]
    print(labels)
    
    #params
    param_grid = {}
    
    X_train, X_test, Y_train, Y_test = train_test_split(
      df_model.usage.values, 
      labels.values, 
      train_size=0.75, 
      shuffle=False
    )
    cv = TimeSeriesSplit(n_splits=3)
    imputer = IterativeImputer()

    print(imputer.__class__.__name__)
    pipeline = Pipeline(steps=[('i', imputer), ('m', IsolationForest())])
    param_grid = {
      'i__n_nearest_features': [None, 1],
      'i__initial_strategy': ['mean', 'median', 'most_frequent'],
      'i__imputation_order': ['ascending', 'descending', 'random']
    }

    clf = GridSearchCV(
      estimator=pipeline,
      param_grid=param_grid,
      cv=cv,
      scoring=['neg_mean_squared_error', 'f1', 'balanced_accuracy'],
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
    tuning_results.to_csv(f"../data/{imputer.__class__.__name__}_tuning_results.csv", index=False)

    def make_prediction(title, X_test, Y_test): 
      print(title)
      Y_hat = clf.predict(X_test)
      pred_results = {
        'mse' : mean_squared_error(Y_test, Y_hat),
        'f1' : f1_score(Y_test, Y_hat),
        'balanced_accuracy' : balanced_accuracy_score(Y_test, Y_hat),
      }
      print(pred_results)

    make_prediction("Full data", X_test, Y_test)
    X_test_missing = X_test
    p = 0.2
    indices = np.random.choice(np.arange(X_test_missing.size), replace=False,
                              size=int(X_test_missing.size * p))
    X_test_missing[np.unravel_index(indices, X_test_missing.shape)] = np.nan
    make_prediction("Missing data", X_test_missing, Y_test)

df, df_20 = load_data()
site = 5
impute_values(df, site)
