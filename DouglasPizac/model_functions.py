'''
Rent model functions 

Created by Douglas Pizac, Jane Dickson, Ethan Zien, and Casey Hoffman
'''
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

feature_cols = ['Rent','State-County','State','Year',
                             'City','Metro','County','Zipcode','SizeRank']

def forest_regressor(df, datestr):
    '''Returns a fit Random Forest model, the testing features, and the testing targets

        Args:
        df: pd.DataFrame, Dataframe containing features and target to evaluate with Random Forest
        datestr: str, date by which to split the train/test data (train < datestr, test >= datestr)

    '''
    
    
    X = df.copy()
    for feature in feature_cols:
        try:
            X.drop(feature, axis = 1, inplace = True)
        except:
            continue
    y = np.log(df['Rent'])
    rfc = RandomForestRegressor(n_estimators = 600)
    Xtrain = X.loc[X.index <datestr]
    train_index = Xtrain.shape[0]
    Xtest = X[train_index:]
    ytrain = y[:train_index]
    ytest = y[train_index:]
    rfc.fit(Xtrain,ytrain)
    
    return rfc, Xtest,ytest

def abs_relative_error(ytest,ypred,df):
    '''returns a plot of the metro area rent errors relative to the rent price
    
    Args:
    
    ytest: pd.DataFrame, Actual rent values
    ypred: np.array, predicted rent values
    df: pd.DataFrame'''
    abs_pct_rent_error = pd.Series(np.abs((np.exp(ytest)-np.exp(ypred))/np.exp(ytest)))

    test_metros = df['Metro'].loc[df.index >=ytest.index[0]].copy()

    test_predictions = pd.concat([abs_pct_rent_error,test_metros],axis = 1)
    test_predictions.reset_index(inplace = True)
    data_error_max = test_predictions.groupby(['Date','Metro'],as_index = False)['Rent'].mean()

    fig = plt.figure(figsize =(15,10))
    sns.lineplot(data = data_error_max, x = 'Date', y = 'Rent',hue = 'Metro')
    plt.title('Mean absolute error as percentage of rent')
    plt.xlabel('Date')
    plt.ylabel('Error in percent of actual rent')
    plt.legend(loc = 'upper left')
    

def forest_clusters(df,datestr):
    '''
    returns a dictionary containing Random Forest results for each cluster

    args:

    df: pd.DataFrame, DataFrame containing features, target, and a column 'Clusters' to slice by
    datestr: str, date by which to split the train/test data (train < datestr, test >= datestr)

    '''

    try:
        isinstance(datestr,str)
    except:
        raise TypeError('Index must be dates formattted as a str and (YYYY-mm-dd)')
    cluster_res = dict()

    for cluster in range(len(df['Clusters'].unique())):
    
        X = df.loc[df['Clusters'] == cluster].copy()
        y = np.log(X.Rent)
        X = X.drop(feature_cols, axis = 1)
        
        Xtrain = X.loc[X.index <datestr]
        train_index = Xtrain.shape[0]
        Xtest = X[train_index:]
        ytrain = y[:train_index]
        ytest = y[train_index:]
        rfc_cluster = RandomForestRegressor(n_estimators=600)
        rfc_cluster.fit(Xtrain,ytrain)
        cluster_res[f'cluster{cluster}_train_score'] = rfc_cluster.score(Xtrain,ytrain)
        cluster_res[f'cluster{cluster}_test_score'] = rfc_cluster.score(Xtest,ytest)
        cluster_res[f'cluster{cluster}_test_set'] = np.array(ytest)
        cluster_res[f'cluster{cluster}_predictions'] = rfc_cluster.predict(Xtest)
        cluster_res[f'cluster{cluster}_RMSE'] = mean_squared_error(np.exp(ytest),
                                                 np.exp(cluster_res[f'cluster{cluster}_predictions'])
                                                 ,squared = False)
    return cluster_res
        