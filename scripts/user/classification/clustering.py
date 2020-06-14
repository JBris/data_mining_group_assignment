import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sc
import statistics
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import TimeSeriesSplit, train_test_split, GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, f1_score, roc_auc_score, balanced_accuracy_score
from sklearn.cluster import AgglomerativeClustering

np.random.seed(10)

def pivot(df):
  channel_df = pd.pivot_table(
    df,
    values = ['usage', 'anomaly'],
    index = 'date_time',
    columns = 'channel_id'
  )
  channel_df.fillna(-1, inplace=True)
  return channel_df

def load_data():
  df = pd.read_csv(
        '../data/labelled_final_processed.csv',
         parse_dates = ['date_time'],
         dayfirst = True,
      )
        
  #Handle site 20 here
  df_20 = df.loc[df.site == 20] 
  df = df.loc[df.site != 20] 
  return df, df_20

def model_hours(df, i):
    df_model = df.loc[df.site == i]
    df_model.set_index('date_time', inplace=True)
    
    # visualization
    fig, axes = plt.subplots(3, 2)
    fig.subplots_adjust(hspace=0.5)
    fig.suptitle('Estimated Operating Hours')

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days = df_model.weekday.drop_duplicates().sort_values().values
    for ax, day in zip(axes.flatten(), days):      
        df_model_day = df_model.loc[df_model.weekday == day]
        X = df_model_day.usage.values 
        X = X.reshape(X.shape[0], 1)
        #distance_threshold=...
        clf = AgglomerativeClustering(n_clusters=2, affinity='manhattan', linkage='average')
        pred = clf.fit_predict(X)

        df_model_day["cluster"] = pred
        df_model_day.index = df_model_day.index.time
        a = df_model_day.loc[df_model_day['cluster'] == 0, ['usage', 'hour']] 
        b = df_model_day.loc[df_model_day['cluster'] == 1, ['usage', 'hour']] 
        print(df_model_day)
        ax.set_title(weekdays[day])
        ax.scatter(a.hour, a.usage, color='blue', s=5)
        ax.scatter(b.hour, b.usage, color='red', s=5)

    plt.gcf().autofmt_xdate()
    handles, labels = ax.get_legend_handles_labels()
    plt.figlegend(handles, labels, bbox_to_anchor=(0.5, 0.5, 0.5, 0.5), loc='center right')
    plt.show();  
  
df, df_20 = load_data()
df['weekday'] = df.date_time.dt.weekday

# df.groupby(['site', 'weekday']).apply(
#     lambda x: print(x.site.iloc[0] , x.weekday.iloc[0]  , max(x.usage) - min(x.usage) )
# ) 


#sites = [5, 6, 7, 8, 12]
site = 5
model_hours(df, site)
