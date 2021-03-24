
import pandas as pd
import numpy as np

def transform_zillow(path):
    '''
    Transforms the Zillow ZRI data file:
        - imputes missing rents by interpolation and backfilling
        - transforms date/rent columns into rows

    Args:
    path: path to the data file, str

    Merge By: 
        time: Date (01 of every month), Year
        location: State, City, Metro, County, Zipcode

    '''
    dataframe = pd.read_csv(path, dtype = {'RegionName':str})
    dataframe.rename(columns = {'RegionName':'Zipcode',
                                'CountyName': 'County'}, inplace = True)
    dataframe['Zipcode'] = dataframe['Zipcode'].str.zfill(5)

    dataframe = pd.melt(dataframe, id_vars =dataframe.columns[:7],
                         value_vars = dataframe.columns[7:],
                         var_name = 'Date', 
                         value_name = 'Rent')
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])

    fill_rents = dataframe[['Zipcode', 'Rent', 'Date']].copy()

    # imputing missing Rent values
    fill_rents = fill_rents.reset_index().pivot(index = 'Date',columns = 'Zipcode')['Rent'].reset_index()
    fill_rents.fillna(method = 'ffill',inplace = True)
    fill_rents = pd.melt(fill_rents, id_vars='Date', 
                                      value_vars = fill_rents.columns[1:],
                                      var_name='Zipcode',value_name = 'Rent')
    dataframe.drop('Rent', axis = 1, inplace = True)
    dataframe = pd.merge(dataframe, fill_rents, on = ['Date','Zipcode'])

    #parsing year separately for merging with annual features
    dataframe['Year'] = dataframe['Date'].dt.year
    
    date_cut = '2015-01-01'
    dataframe = dataframe[dataframe['Date']>=date_cut]

    nulls_df = dataframe[dataframe['Rent'].isnull()]
    bad_zips = nulls_df['Zipcode'].unique().tolist()
    dataframe = dataframe[dataframe['Zipcode'].isin(bad_zips)==False]
    
    return(dataframe)


def transform_air_qual(path):
    '''
    Args: path to **folder** containing the data files, str

    Merge By: 
        time: Date (01 of every month)
        location: State, City, County

    Feature Name: 'AQIMean'

    '''
    file_list = [(f'{path}/daily_42602_{year}.csv') for year in range(2010, 2021)]
    cols = ['Date Local', 'Arithmetic Mean', 'State Name', 'County Name', 'City Name']

    dataframe = pd.read_csv(file_list[0], usecols = cols)

    for file in file_list[1:]:
        new_df = pd.read_csv(file, usecols = cols)
        dataframe = pd.concat([dataframe, new_df], axis=0)

    dataframe['Date Local'] = pd.to_datetime(dataframe['Date Local'])
    dataframe['Month'] = dataframe['Date Local'].dt.month
    dataframe['Year'] = dataframe['Date Local'].dt.year
    dataframe = dataframe.groupby(['State Name', 'County Name', 'City Name', 'Year', 'Month'])[['Arithmetic Mean']].agg('mean').reset_index()
    dataframe.Month = dataframe.Month.astype(str)
    dataframe.Month = dataframe.Month.str.zfill(2)
    dataframe['Date'] = '01/'+dataframe.Month.astype(str)+'/'+dataframe.Year.astype(str)
    dataframe['Date'] = pd.to_datetime(dataframe['Date'], format="%d/%m/%Y")
    dataframe.drop(['Month', 'Year'],axis=1,inplace=True)

    dataframe.rename(columns={'State Name': 'State', 
                                'County Name': 'County', 
                                'City Name':'City',
                                'Arithmetic Mean':'AQIMean'}, inplace=True)

    return(dataframe)


def transform_pers_income(path):
    '''
    Args: path to the data file, str

    Merge By: 
        time: Year
        location: City

    Feature Name: 'PersonalIncome'

    '''
    dataframe = pd.read_csv(path)

    dataframe = dataframe[dataframe.LineCode == 2]
    dataframe.drop(['GeoFips','LineCode'],axis=1,inplace=True)

    dataframe = dataframe.melt(id_vars = ['MetroArea','Description'],
                                var_name='Year', 
                                value_name='PersonalIncome').\
                                drop('Description',axis=1)

    dataframe['Year'] = pd.to_datetime(dataframe['Year']).dt.year

    dataframe.rename(columns={'MetroArea':'State'}, inplace=True)
    state_map = {'Austin':'TX','Miami':'FL','New York':'NY','San Francisco':'CA'}
    dataframe['State'] = dataframe['State'].apply(lambda x: state_map[x])

    return(dataframe)

def transform_income_level(path):
    '''
    Args: path to the data file, str

    Merge By: 
        time: Year
        location: City

    Feature Name: 'Vol',  'VolUnadjusted',  'IncomeLevelGroup'

    '''
    dataframe = pd.read_csv(path)

    dataframe.drop('month', axis=1, inplace=True)
    dataframe = dataframe[(dataframe['income_level_group'] != "High") & 
                            (dataframe['income_level_group'] != "Middle")]

    dataframe['date'] = pd.to_datetime(dataframe['date']+'-01', format="%Y-%m-%d")

    dataframe.rename(columns={'date':'Date',
                                'vol':'Vol',
                                'vol_unadj':'VolUnadjusted',
                                '   income_level_group':'IncomeLevelGroup'}, inplace=True)

    return(dataframe)


def transform_census(path):
    '''
    Args: path to the data file, str

    Merge By: 
        time: Year
        location: Zipcode

    Feature Name: 'Vol',  'VolUnadjusted',  'IncomeLevelGroup'
    ----------------------------------------------------------
    SQL Query to retrieve the data from BigQuery:

        SQL query for retrival: WITH acs_2018 AS (
          SELECT *
          FROMbigquery-public-data.census_bureau_acs.zip_codes_2018_5yr` ),

        acs_zip AS ( SELECT zip_code FROM bigquery-public-data.geo_us_boundaries.zip_codes ),

        acs_zipcode AS ( SELECT * FROM acs_2018 a18 JOIN acs_zip geo ON a18.geo_id = geo.zip_code )

        SELECT * FROM acs_zipcode`

    '''
    dataframe = pd.read_csv(path, dtype={'zip_code':str})
    dataframe['zip_code'] = dataframe['zip_code'].str.zfill(5)
    dataframe.rename(columns={'zip_code':'Zipcode'}, inplace=True)

    return(dataframe)