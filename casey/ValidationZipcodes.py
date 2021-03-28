import numpy as np
import pandas as pd

def GetZipcodes(ZRI):
    '''
    Import the original ZRI Multifamily df. This will output a list of all zipcodes (from our counties)
    that have NO missing rent values, starting in 2015.
    Load in ZRI using the following:
    pd.read_csv('../../data/zillow/Zip_Zri_MultiFamilyResidenceRental.csv',dtype = {'RegionName':str})
    '''
    ZRI = ZRI.rename(columns = {'RegionName':'Zipcode'})
    ZRI.drop(['2010-09','2010-10','2010-11','2010-12','2011-01','2011-02','2011-03','2011-04','2011-05','2011-06',
             '2011-07','2011-08','2011-09','2011-10','2011-11','2011-12','2012-01','2012-02','2012-03','2012-04',
             '2012-05','2012-06','2012-07','2012-08','2012-09','2012-10','2012-11','2012-12','2013-01','2013-02',
             '2013-03','2013-04','2013-05','2013-06','2013-07','2013-08','2013-09','2013-10','2013-11','2013-12',
             '2014-01','2014-02','2014-03','2014-04','2014-05','2014-06','2014-07','2014-08','2014-09','2014-10',
             '2014-11','2014-12'],axis=1,inplace=True)
    
    # from transformers.py
    sf_counties = ['Alameda County', 'Contra Costa County', 'Marin County', 'Napa County', 'San Mateo County',
    'Santa Clara County', 'Solano County', 'Sonoma County', 'San Francisco County']
    ny_counties = ['New York County', 'Bronx County', 'Queens County', 'Kings County', 'Richmond County']
    tx_counties = ['Travis County']
    mia_counties = ['Miami-Dade County', 'Broward County', 'Palm Beach County']
    counties_dict = {'CA':sf_counties,'NY':ny_counties,'TX':tx_counties,'FL':mia_counties}
    
    all_counties = []
    for state,counties in counties_dict.items():
        for county in counties:
            all_counties.append('%s-%s' % (state,county))

    ZRI['State-County'] = ZRI['State'] + '-' + ZRI['CountyName']
    # filter by the above counties to our group's target counties
    ZRI = ZRI[ZRI['State-County'].isin(all_counties)].copy()
    # remove all other cols (could potentially have an NA)
    ZRI.drop(['RegionID','City','State','Metro','CountyName','SizeRank','State-County'],axis=1,inplace=True)
    ZRI.set_index('Zipcode',inplace=True)
    zipcodes = ZRI.isnull().sum(axis=1).reset_index().rename(columns = {0:'n_missing'})
    test_zips = zipcodes[zipcodes['n_missing']==0].Zipcode.to_list()

    return test_zips