#### **Objective:**<br/>
##### **Problem to solve:**<br/>
 - Predict Zillow Home/Rent values using data models.<br/>
 - Utilize a variety of publicly available data sources to develop new indices / feature engineer to aid in this prediction.<br/>
##### **Questions to answer:**<br/>
- What factors most strongly account for the pricing of homes/rent?<br/>
- How do past prices impact future prices?<br/>
- What constitutes a good metric -- is it 1) useful for prediction, 2) easily interpretable for the sake of real-world applicability?<br/>
- How will we measure success from a business/user perspective?<br/>
- Are the predictions accurate? (Can our models predict the future sale/ rent price within a very slim margin of error).<br/>
- Do our predictors provide new insights / unique value? We want to ensure we don’t “reinvent the wheel” (i.e, fail to provide a model with substantial value)<br/>

##### **Scope:**<br/>
**Population:** process and model will be used to predict Zillow home/rent values for multi-family homes in the United States. <br/>
**Timeframe:** Zillow’s latest dataset has 7 years of rental indices for the United States, but it does not include the full history. Therefore, we will use data from rentals spanning between September 2010 and January 2020.<br/>
**Target variable:** Home value index (in US dollars).<br/>
**Questions to answer with business and risk:**<br/>
- What’s the default definition of the index?<br/>
- Which features from the American Community Survey (ACS) should be considered?<br/>
- How do we forecast prices 1,2,5 years from now given this data does not account for the COVID-19 pandemic?<br/>

##### **Data:**<br/>
**Zillow Historical ZRI Data Multi Family Homes:**<br/>
Description: historical ZRI data from 1/2014 - 1/2021<br/>
**Zillow Historical ZORI Data Multi Family Homes:**<br/>
Description: most recent ZORI data<br/>
Source: https://www.zillow.com/research/data/<br/>
**ACS Data:**<br/>
Description: Data from ACS surveys<br/>
Source: https://console.cloud.google.com/marketplace/product/united-states-census-bureau/acs?project=rf-etl<br/>

##### **Team:**<br/>
[Casey Hoffman](https://github.com/caseyahoffman): Academic research<br/>
[Douglas Pizac](https://github.com/pizacd): Academic research<br/>
[Ethan Zien](https://github.com/ejzien): Advertising<br/>
[Eugenia Dickson](https://github.com/EugeniaDickson): Building design & BIM
