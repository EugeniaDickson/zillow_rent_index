import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.decomposition import PCA
#zillow = pd.read_csv('../../data/zillow_full_imputed.csv')

#%run ../Jane/extract_data.py

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def preProc(zillow_df, ytype='log'):
    '''
    Input a dataframe of features + target rent.
    Will return X (with label encoding for non-numeric features)
    'y_type' argument allows you to specify how the feature should be treated;
    'y_type' = 'log' will return a log-transformed rent pd.Series
    'y_type' = 'normal' will return the original rent pd.Series
    '''
    LE = LabelEncoder() 
    features = zillow_df.copy()
    features = features.drop('Rent',axis=1).copy()
    cat_cols = features.select_dtypes(include = object).copy()
    num_cols = features.select_dtypes(exclude = object).copy()
    for col in cat_cols.columns:
        cat_cols[col] = LE.fit_transform(cat_cols[col])
    
    X = pd.concat([cat_cols,num_cols],axis=1)
    
    if ytype == 'log':
        y = np.log(zillow_df['Rent'])
    elif ytype == 'normal':
        y = zillow_df['Rent']
    return X,y

def train_test(X,y):
    '''
    Input the output of the preProc function. Make sure 'Date' is the index of X dataframe.
    '''
    Xtrain = X.loc[X.index <'2019-01-01']
    train_index = Xtrain.shape[0]
    Xtest = X[train_index:]
    ytrain = y[:train_index]
    ytest = y[train_index:]
    return Xtrain,Xtest,ytrain,ytest

def screePlot(df, df_name='features'):
    '''
    Input a dataframe of features; outputs a screeplot for PCA.
    If you specify a df_name, it will output to the plot's title.
    Ex. df_name='features' ->
    plot title -> "Scree Plot of features"
    '''
    pca = PCA(n_components=df.shape[1]) 
    pca.fit(df)
    titl = "Scree Plot of {}".format(df_name)
    print(pca.explained_variance_ratio_)
    plt.plot((np.arange(pca.n_components_)+1), pca.explained_variance_ratio_, 'ro-', linewidth=2)
    plt.title(titl)
    plt.xlabel('# Principal Components')
    plt.ylabel('% of Variance Explained')
    plt.show()

def featurePlotPCA(df, figure_size = (8,5), df_name='features'):
    '''
    Input a data frame of JUST the feature columns.
    This will output a heatmap of feature importances in each principal component.

    If you specify a df_name, it will output to the plot's title.
        Ex. df_name='features' ->
        plot title -> "Scree Plot of features"
    Make sure the df:
        - has no NA's
        - has no non-numeric features
        - is scaled/normalized
    '''
    pca = PCA(n_components=df.shape[1]) 
    components = pca.fit_transform(df)
    idx = df.columns.to_list() # indices of original col names
    cols = ['PC'+str(i) for i in range(1,len(idx)+1)]
    dot_matrix = pd.DataFrame(np.dot(df.T,components),
                         index = idx, columns = cols)
    df_abs = dot_matrix.copy().abs() # absolute value
    
    plt.figure(figsize=figure_size)
    heatmap = sns.heatmap(df_abs, cmap="GnBu", vmin=0, vmax=1, linewidths=.5)
    titl = "|Z-Normalized| Feature Importances for {} PCA".format(df_name)
    heatmap.set_title(titl)
    plt.show()

def randForest(model,Xtrain,Xtest,ytrain,ytest):
    '''
    Input a -tuned- model, train/test for feature/target.
    Will output the test and training R2, test RMSE.
    '''
    model.fit(Xtrain,ytrain)
    print(f'training R2: {model.score(Xtrain,ytrain)}')
    print(f'test R2: {model.score(Xtest,ytest)}')
    
    ypred = model.predict(Xtest)
    RMSE = mean_squared_error(np.exp(ytest),np.exp(ypred),squared=False)
#     RMSE = mean_squared_error(ytest,ypred, squared = False)
    print(f'RMSE: {RMSE}')
    
    feature_imps = pd.DataFrame({'Columns':Xtrain.columns,'Feature_importances':model.feature_importances_})
    return feature_imps.sort_values('Feature_importances',ascending=False)