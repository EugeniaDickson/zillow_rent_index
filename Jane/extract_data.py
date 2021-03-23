from transformers import *

zillow_path = '../../data/zillow/Zip_Zri_MultiFamilyResidenceRental.csv'
airqual_path = '../../data/airqual/' #path to folder
persinc_path = '../../data/real_personal_income.csv'
inclvl_path = '../../data/volume_data_Income_Level_CRC.csv'
census_path = '../../data/census-query.csv'

zillow_data = transform_zillow(zillow_path)
airqual_data = transform_air_qual(airqual_path)
persinc_data = transform_pers_income(persinc_path)
inclvl_data = transform_income_level(inclvl_path)
census_data = transform_census(census_path)