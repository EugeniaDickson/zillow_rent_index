
import pandas as pd
import numpy as np

# SF Metro
sf_counties = ['Alameda County', 'Contra Costa County', 'Marin County', 'Napa County', 'San Mateo County', 
               'Santa Clara County', 'Solano County', 'Sonoma County', 'San Francisco County']
# NY Metro:
ny_counties = ['New York County', 'Bronx County', 'Queens County', 'Kings County', 'Richmond County']
# Greater Austin Metro:
tx_counties = ['Travis County']
# Miami Metro:
mia_counties = ['Miami-Dade County', 'Broward County', 'Palm Beach County']

counties_dict = {'CA':sf_counties,'NY':ny_counties,'TX':tx_counties,'FL':mia_counties}

all_counties = []
for state,counties in counties_dict.items():
    for county in counties:
        all_counties.append('%s-%s' % (state,county))

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
    
    dataframe['State-County'] = dataframe['State'] + '-' + dataframe['County']
    dataframe = dataframe[dataframe['State-County'].isin(all_counties)]
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
    
    
    dataframe['County'] = dataframe['County'] + ' County'
    state_map = {'Florida':'FL','California':'CA','New York':'NY','Texas':'TX'}
    dataframe['State'] = dataframe['State'].apply(lambda x: state_map[x] if x in state_map else x)
    dataframe['State-County'] = dataframe['State'] + '-' + dataframe['County']
    dataframe = dataframe[dataframe['State-County'].isin(all_counties)]
    
    nyc_avg = dataframe[dataframe.City=='New York'].groupby('Date').mean().reset_index()
    nyc_avg['State'] = 'NY'
    nyc_avg['City'] = 'New York'
    nyc_aq = pd.concat((nyc_avg,nyc_avg,nyc_avg))
    counties = ['New York County']*129+['Kings County']*129+['Richmond County']*129
    nyc_aq['County']= counties
    nyc_aq = nyc_aq[['State','County','City','AQIMean','Date']]
    dataframe = pd.concat((dataframe,nyc_aq)).groupby(['Date','State','County']).mean().reset_index()
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
    
    inclvl_moderate = dataframe[dataframe.income_level_group == 'Moderate'][['Date','Vol']]
    inclvl_moderate = inclvl_moderate.rename(columns={'Vol':'Vol_moderate_income'})
    inclvl_low = dataframe[dataframe.income_level_group == 'Low'][['Date','Vol']]
    inclvl_low = inclvl_low.rename(columns={'Vol':'Vol_low_income'})
    dataframe = pd.merge(inclvl_moderate,inclvl_low,on='Date')

    return(dataframe)


def transform_census(path):
    '''
    Args: path to the data file, str

    Merge By: 
        time: Year
        location: Zipcode

    Feature Name: plethora of features
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
    dataframe['do_date'] = pd.to_datetime(dataframe['do_date'])

    dataframe = dataframe[['do_date','total_pop','households','median_age','median_income','income_per_capita',
                  'pop_determined_poverty_status', 'poverty','gini_index','housing_units',
                  'different_house_year_ago_different_city','different_house_year_ago_same_city',
                  'pop_in_labor_force','aggregate_travel_time_to_work','bachelors_degree','employed_pop',
                  'unemployed_pop', 'employed_arts_entertainment_recreation_accommodation_food','Zipcode']]

    # pct poverty
    dataframe['pct_poverty'] = dataframe['poverty']/dataframe['pop_determined_poverty_status']
    dataframe.drop(['poverty','pop_determined_poverty_status'],axis=1,inplace=True)
    # estimated number of homes for each household (scarse? or many available?)
    dataframe['housing_availability'] = dataframe['housing_units']/dataframe['households']
    # estimated number of people per household
    dataframe['home_density'] = dataframe['total_pop']/dataframe['households']
    dataframe['pct_employed'] = dataframe['employed_pop']/dataframe['pop_in_labor_force']
    dataframe['pct_jobs_nightlife'] = dataframe['employed_arts_entertainment_recreation_accommodation_food']/dataframe['employed_pop']
    dataframe['pct_unemployed'] = dataframe['unemployed_pop']/dataframe['pop_in_labor_force']
    # have moved from somewhere else in the same city
    dataframe['move_within_city'] = dataframe['different_house_year_ago_same_city']/dataframe['total_pop']
    # have moved to this city from a new city
    dataframe['move_new_city'] = dataframe['different_house_year_ago_different_city']/dataframe['total_pop']
    dataframe['avg_commute_time'] = dataframe['aggregate_travel_time_to_work'] / dataframe['employed_pop']
    dataframe.drop(['pop_in_labor_force','housing_units','employed_pop','employed_arts_entertainment_recreation_accommodation_food','unemployed_pop',
              'different_house_year_ago_same_city','different_house_year_ago_different_city','aggregate_travel_time_to_work'],axis=1,inplace=True)
    # percent of population w/ bachelors degree
    dataframe['pct_college'] = dataframe['bachelors_degree'] / dataframe['total_pop']
    dataframe.drop('bachelors_degree',axis=1,inplace=True)

    return(dataframe)

def join_dfs(zillow_df,air_df=None,persinc_df=None,inclvl_df=None,census_df=None):
    if air_df is not None:
        pass
        
    if persinc_df is not None:
        zillow_df=pd.merge(zillow_df,persinc_df,on=['Year','State'],how='left')
        
    if inclvl_df is not None:
        zillow_df=pd.merge(zillow_df,inclvl_df,on=['Date'],how='left')
        
    if census_df is not None:
        zillow_df=pd.merge(zillow_df,census_df,on=['Zipcode'],how='left')
    return zillow_df