#### **Objective:**
##### **Problem to solve:**
Predict Zillow Home/Rent values using data models.
Utilize a variety of publicly available data sources to develop new indices / feature engineer to aid in this prediction.
##### **Questions to answer:**
- What factors most strongly account for the pricing of homes/rent?
- How do past prices impact future prices?
- What constitutes a good metric -- is it 1) useful for prediction, 2) easily interpretable for the sake of real-world applicability?
- How will we measure success from a business/user perspective?
- Are the predictions accurate? (Can our models predict the future sale/ rent price within a very slim margin of error).
- Do our predictors provide new insights / unique value? We want to ensure we don’t “reinvent the wheel” (i.e, fail to provide a model with substantial value)

##### **Scope:**
**Population:** process and model will be used to predict Zillow home/rent values for multi-family homes in the United States. 
**Timeframe:** Zillow’s latest dataset has 7 years of rental indices for the United States, but it does not include the full history. Therefore, we will use data from rentals spanning between September 2010 and January 2020.
**Target variable:** Home value index (in US dollars).
**Questions to answer with business and risk:**
- What’s the default definition of the index?
- Which features from the American Community Survey (ACS) should be considered?
- How do we forecast prices 1,2,5 years from now given this data does not account for the COVID-19 pandemic?

##### **Data:**
**Zillow Historical ZRI Data Multi Family Homes:**
Description: historical ZRI data from 1/2014 - 1/2021
**Zillow Historical ZORI Data Multi Family Homes:**
Description: most recent ZORI data
Source: https://www.zillow.com/research/data/
**ACS Data:**
Description: Data from ACS surveys
Source: https://console.cloud.google.com/marketplace/product/united-states-census-bureau/acs?project=rf-etl

##### **Team:**
[Casey Hoffman](https://github.com/caseyahoffman): Academic research
[Douglas Pizac](https://github.com/pizacd): Academic research
[Ethan Zien](https://github.com/ejzien): Advertising
[Eugenia Dickson](https://github.com/EugeniaDickson): Building design & BIM
