import pandas as pd
import numpy as np
import os
from glob import glob


## ADD IN COMPILATION CODE TO JOIN ALL THE SUB-MODELS INTO A SINGLE FILE FOR PROCESSING

SEARCH_FOLDER = '/home/bryant/Documents/an_metcoal_modelcoding/phasefilegenerator/Comet Reserves/'

INPUT_SHEET = 'PhaseCalculator_V1_MetCoal_2021-06-03.xlsx'

## METCOAL RESERVE SETS REQUIRE AN ASSOCIATED FILTER - SELECT THE RESERVE SET REQUIRED

BLOCKMODEL = 'MetCoal'

RESERVESET = 'ALL'

########################################################################################
##
# Find relevant columns to subset the model.

inputs = pd.ExcelFile(INPUT_SHEET)
field_order_import = inputs.parse('FieldOrder')
field_order = field_order_import
weighted_fields = inputs.parse('WeightedFields')
sum_fields = inputs.parse('SumFields')
FieldSearchList = field_order['Field'].tolist()

########################################################################################
##
# IMPORT CASHFLOW MODELS

print("Loading Reserve Models")

df1 = pd.concat(map(pd.read_csv, glob(SEARCH_FOLDER + "*.csv")))

# df1.to_csv("debug_export.csv")

########################################################################################
##
## REPLACE -99 VALUES WITH NANS AND UPDATE OTHER KEY FIELDS

print("Cleaning Reserve Models")

df1.replace(-99, np.nan)

df1.columns = df1.columns.str.replace(" ", "_")

query = df1['Mining_Method'] == 'OC'
df1.loc[query, 'ROM_Dev_Tonnes'] = 0
df1.loc[query, 'ROM_LW_Tonnes'] = 0
df1.loc[query, 'ROM_Mains_Tonnes'] = 0

query = df1['Mining_Method'] == 'UG'
df1.loc[query, 'Waste_Volume'] = 0
df1.loc[query, 'DL_Total_Waste_Volume'] = 0
df1.loc[query, 'TS_Total_Waste_Volume'] = 0

df1['CELL']= df1['CELL'].map(str)

########################################################################################
##
## FILTER THOSE DATA FOR THE RELEVANT RESERVE SET

print("Filtering Reserve Models")

df1["RESERVEFILTER"] = False

if RESERVESET == 'BASE':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.8 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.85 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.05 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.05 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.85 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.90 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.90 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'GC') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'AQ') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True


elif RESERVESET == 'SUBSET1':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '5') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'GC') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'AQ') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'HRZ') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'WTF') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'RMN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'RNW') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'TRS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'TRE') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'BSN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'BSS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'OMG') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'SXE') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'SXS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True


elif RESERVESET == 'SUBSET2':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '5') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'GC') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'AQ') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET3':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.8 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.85 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.05 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.05 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.85 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.9 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 0.9 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'B') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'BL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'C') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'DU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'D') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'E') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'GC') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'AQ') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'DYU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'HCL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET4':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'B') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'BL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'C') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'DU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'D') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'E') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '5') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'GC') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'AQ') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'DYU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'HCL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'HRZ') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'WTF') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'RMN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'RNW') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'TRS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'TRE') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'BSN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'BSS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'OMG') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'SXE') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'SXS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET5':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'B') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'BL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'C') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'DU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'D') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'E') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET6':
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.0 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'COC') & (df1['CELL'] == '5') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'GC') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Capcoal') & (df1['PIT'] == 'GTAQ') & (df1['CELL'] == 'AQ') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET7':
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'DYU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'HCL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET8':
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'HRZ') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'WTF') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'RMN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'RNW') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'TRS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'TRE') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'BSN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'BSS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'OMG') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'SXE') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'PRC') & (df1['PIT'] == 'SXS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.5 ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET9':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'B') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'BL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'C') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'DU') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'D') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'E') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET10':
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DN') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP15') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP612') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['HORIZON_Number'] <=1720) & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP1319') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DP2024') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'DS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['PIT'] == 'Theo') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'B') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'BL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'C') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'DU') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'D') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'Dawson') & (df1['CELL'] == 'E') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.2 ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET11':
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.3 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.3 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.3 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.3 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'DYU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.3 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'HCL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.3 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.3 ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET12':
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.4 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.4 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.4 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.4 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'DYU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.4 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'HCL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.4 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.4 ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET13':
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '1') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '2') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '3') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == '4') & (df1['Mining_Method'] == 'OC') & (df1['RF_Shell_No'] >= 0.5) & (df1['RF_Shell_No'] <= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'DYU') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MN') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'GRV') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG'   ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'HCL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GL') & (df1['Mining_Method'] == 'UG' ) & (df1['RF_Shell_No'] >= 1.1 ) 
    df1.loc[query, 'RESERVEFILTER'] = True

elif RESERVESET == 'SUBSET14':
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG')
    df1.loc[query, 'RESERVEFILTER'] = True    
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 1.5) & (df1['LW_PANEL'] == 201)  
    df1.loc[query, 'RESERVEFILTER'] = False
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 1.5) & (df1['LW_PANEL'] == 202)  
    df1.loc[query, 'RESERVEFILTER'] = False 
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 1.5) & (df1['LW_PANEL'] == 203)  
    df1.loc[query, 'RESERVEFILTER'] = False
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 2.0) & (df1['LW_PANEL'] == 204)  
    df1.loc[query, 'RESERVEFILTER'] = False
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 2.0) & (df1['LW_PANEL'] == 205)  
    df1.loc[query, 'RESERVEFILTER'] = False
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 2.0) & (df1['LW_PANEL'] == 206)  
    df1.loc[query, 'RESERVEFILTER'] = False
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 2.0) & (df1['LW_PANEL'] == 207)  
    df1.loc[query, 'RESERVEFILTER'] = False 
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 2.0) & (df1['LW_PANEL'] == 208)  
    df1.loc[query, 'RESERVEFILTER'] = False
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 2.0) & (df1['LW_PANEL'] == 209)  
    df1.loc[query, 'RESERVEFILTER'] = False
    query =  (df1['MINE'] == 'MG') & (df1['PIT'] == 'MS') & (df1['CELL'] == 'GM') & (df1['Mining_Method'] == 'UG') & (df1['RF_Shell_No'] >= 1.35) & (df1['RF_Shell_No'] <= 2.0) & (df1['LW_PANEL'] == 210)  
    df1.loc[query, 'RESERVEFILTER'] = False

elif RESERVESET == 'ALL':
    df1['RESERVEFILTER'] = True   

df1 = df1.query("RESERVEFILTER == True").copy()


########################################################################################
##
## CREATE FILELD FOR A CLEANED PHASE NAME

print("Running Calculations on Reserve Models")

df1['PHASENAME'] = 'NO_PHASE'

df1['PHASENAMECALC'] = df1['MINE'] + "_" + df1['PIT'] + "_" + df1['CELL'] + "_" + df1['Mining_Method']
query = (df1['Mining_Method'] == 'OC')
df1.loc[query, 'PHASENAME'] = df1.loc[query, 'PHASENAMECALC']

df1['PHASENAMECALC'] = df1['MINE'] + "_" + 'Daw' + "_" + df1['CELL'] + "_" + df1['Mining_Method']
query = (df1['Mining_Method'] == 'UG') & (df1['MINE'] == 'Dawson')
df1.loc[query, 'PHASENAME'] = df1.loc[query, 'PHASENAMECALC']

df1['PHASENAMECALC'] = df1['MINE'] + "_" + df1['PIT'] + "_" + df1['CELL'] + "_" + df1['Mining_Method']
query = (df1['Mining_Method'] == 'UG')
df1.loc[query, 'PHASENAME'] = df1.loc[query, 'PHASENAMECALC']



########################################################################################
##
## CREATE DIMENSION FIELDS AND RELEVANT WEIGHTING FIELDS 


## CREATING PROCESSING HOUR FIELD FIRST SO IT CAN BE USED FOR FURTHER CALCULATIONS

df1['ProcessingHours'] = 0
query = (df1['PIT'] == 'COC') & (df1['HORIZON_Group'] == 'Girrah') 
df1.loc[query, 'ProcessingHours'] =  925
query = (df1['PIT'] == 'COC') & (df1['HORIZON_Group'] == 'Middlemount') 
df1.loc[query, 'ProcessingHours'] =  925
query = (df1['PIT'] == 'COC') & (df1['HORIZON_Group'] == 'Pisces') 
df1.loc[query, 'ProcessingHours'] =  925
query = (df1['PIT'] == 'COC') & (df1['HORIZON_Group'] == 'Roper') 
df1.loc[query, 'ProcessingHours'] =  925
query = (df1['PIT'] == 'COC') & (df1['HORIZON_Group'] == 'Tralee') 
df1.loc[query, 'ProcessingHours'] =  925

query = (df1['PIT'] == 'DN') & (df1['HORIZON_Group'] == 'B') 
df1.loc[query, 'ProcessingHours'] =  1675
query = (df1['PIT'] == 'DN') & (df1['HORIZON_Group'] == 'C') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DN') & (df1['HORIZON_Group'] == 'D') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'DN') & (df1['HORIZON_Group'] == 'E') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'A') 
df1.loc[query, 'ProcessingHours'] =  1500
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'AL') 
df1.loc[query, 'ProcessingHours'] =  1400
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'AU') 
df1.loc[query, 'ProcessingHours'] =  1100
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'B') 
df1.loc[query, 'ProcessingHours'] =  1100
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'BL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'C') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'D') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'DL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'DU') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP1319') & (df1['HORIZON_Group'] == 'E') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'DP15') & (df1['HORIZON_Group'] == 'A') 
df1.loc[query, 'ProcessingHours'] =  1475
query = (df1['PIT'] == 'DP15') & (df1['HORIZON_Group'] == 'AU') 
df1.loc[query, 'ProcessingHours'] =  1475
query = (df1['PIT'] == 'DP15') & (df1['HORIZON_Group'] == 'B') 
df1.loc[query, 'ProcessingHours'] =  1675
query = (df1['PIT'] == 'DP15') & (df1['HORIZON_Group'] == 'C') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP15') & (df1['HORIZON_Group'] == 'D') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'DP15') & (df1['HORIZON_Group'] == 'DL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP15') & (df1['HORIZON_Group'] == 'E') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'A') 
df1.loc[query, 'ProcessingHours'] =  1500
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'AL') 
df1.loc[query, 'ProcessingHours'] =  1400
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'AU') 
df1.loc[query, 'ProcessingHours'] =  1100

query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'BL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'C') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'D') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'DL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'DU') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'E') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'A') 
df1.loc[query, 'ProcessingHours'] =  1600
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'AU') 
df1.loc[query, 'ProcessingHours'] =  1600
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'B') 
df1.loc[query, 'ProcessingHours'] =  1400
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'BL') 
df1.loc[query, 'ProcessingHours'] =  1200
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'C') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'D') 
df1.loc[query, 'ProcessingHours'] =  1750
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'DU') 
df1.loc[query, 'ProcessingHours'] =  1850
query = (df1['PIT'] == 'DP612') & (df1['HORIZON_Group'] == 'E') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'A') 
df1.loc[query, 'ProcessingHours'] =  1500
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'A2') 
df1.loc[query, 'ProcessingHours'] =  1400
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'AL') 
df1.loc[query, 'ProcessingHours'] =  1400
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'AU') 
df1.loc[query, 'ProcessingHours'] =  1100
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'B') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'BL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'C') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'D') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'DL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'DU') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DS') & (df1['HORIZON_Group'] == 'E') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'DYR') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'DYU') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'GL') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'GM') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'Goonyella Rider') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'Goonyella Upper') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'HCL') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'Grv') & (df1['HORIZON_Group'] == 'P Lower') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'GTAQ') & (df1['HORIZON_Group'] == 'Aquila') 
df1.loc[query, 'ProcessingHours'] =  1600
query = (df1['PIT'] == 'GTAQ') & (df1['HORIZON_Group'] == 'Corvus') 
df1.loc[query, 'ProcessingHours'] =  1600
query = (df1['PIT'] == 'GTAQ') & (df1['HORIZON_Group'] == 'German Creek') 
df1.loc[query, 'ProcessingHours'] =  1600
query = (df1['PIT'] == 'GTAQ') & (df1['HORIZON_Group'] == 'Pleiades') 
df1.loc[query, 'ProcessingHours'] =  1600
query = (df1['PIT'] == 'GTAQ') & (df1['HORIZON_Group'] == 'Tieri') 
df1.loc[query, 'ProcessingHours'] =  1600
query = (df1['PIT'] == 'MN') & (df1['HORIZON_Group'] == 'DYR') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MN') & (df1['HORIZON_Group'] == 'DYU') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MN') & (df1['HORIZON_Group'] == 'GL') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MN') & (df1['HORIZON_Group'] == 'GM') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MN') & (df1['HORIZON_Group'] == 'HCL') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MS') & (df1['HORIZON_Group'] == 'DYR') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MS') & (df1['HORIZON_Group'] == 'DYU') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MS') & (df1['HORIZON_Group'] == 'GL') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MS') & (df1['HORIZON_Group'] == 'GM') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MS') & (df1['HORIZON_Group'] == 'HCL') 
df1.loc[query, 'ProcessingHours'] =  2250
query = (df1['PIT'] == 'MS') & (df1['HORIZON_Group'] == 'P Lower') 
df1.loc[query, 'ProcessingHours'] =  2250

query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'B') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'C') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'D') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'DL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'DU') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'E') 
df1.loc[query, 'ProcessingHours'] =  1700
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'A') 
df1.loc[query, 'ProcessingHours'] =  1500
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'AL') 
df1.loc[query, 'ProcessingHours'] =  1400
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'AU') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'BL') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'Theo') & (df1['HORIZON_Group'] == 'F') 
df1.loc[query, 'ProcessingHours'] =  1800
query = (df1['PIT'] == 'DN') & (df1['HORIZON_Group'] == 'A') 
df1.loc[query, 'ProcessingHours'] =  1475
query = (df1['PIT'] == 'DP2024') & (df1['HORIZON_Group'] == 'B') 
df1.loc[query, 'ProcessingHours'] =  1800

query = (df1['PIT'] == 'BSN') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'BSS') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'HRZ') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'OMG') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'RMN') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'RNW') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'SXE') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'SXS') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'TRE') 
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'TRS')
df1.loc[query, 'ProcessingHours'] =  850
query = (df1['PIT'] == 'WTF') 
df1.loc[query, 'ProcessingHours'] =  850


## COMPLETE REMAINING CALCUATED RANKINGS


df1['ValuePerTonne'] = 0
df1['ValuePerTonneCALC'] = df1['Max_Value']/df1['ROM_Tonnes']
query = (df1['Max_Value'] > 0)  & (df1['ROM_Tonnes'] > 0) 
df1.loc[query, 'ValuePerTonne'] =  df1.loc[query, 'ValuePerTonneCALC']

df1['d1_Ranking'] = df1['ValuePerTonne'] * df1['ProcessingHours']


df1['d2_CSRRanking'] = 0
query = df1['CSR'].notna()
df1.loc[query, 'd2_CSRRanking'] = df1.loc[query, 'CSR']


df1['d3_CVRanking'] = np.nan
query = (df1['CV_-_Clean_Coking_Volatile_Matter'].isna()) & (df1['TV_-_Clean_Thermal_Volatile_Matter'].isna()) & (df1['RV_-_Raw_Volatile_Matter'].notna())
df1.loc[query, 'd3_CVRanking'] = df1.loc[query, 'RV_-_Raw_Volatile_Matter']
query = (df1['CV_-_Clean_Coking_Volatile_Matter'].isna()) & (df1['TV_-_Clean_Thermal_Volatile_Matter'].notna())
df1.loc[query, 'd3_CVRanking'] = df1.loc[query, 'TV_-_Clean_Thermal_Volatile_Matter']
query = (df1['CV_-_Clean_Coking_Volatile_Matter'].notna()) 
df1.loc[query, 'd3_CVRanking'] = df1.loc[query, 'CV_-_Clean_Coking_Volatile_Matter']


df1['d4_CASHRanking'] = -1*df1['1_Stage_Prim_Wash_Ash']
df1['d4_CASHRankingCALC'] = -1*df1['2_Stage_Prim_Wash_Ash']
query = df1['Best_Product_Sec_Tonnes'] > 0
df1.loc[query, 'd4_CASHRanking'] = df1.loc[query, 'd4_CASHRankingCALC']


df1['d5_C1Ranking'] = df1['C1_-_Clean_Coking_ROMAX_(maximum_reflectance)']
df1['d6_C2Ranking'] = df1['C2_-_Clean_Coking_Crucible_Swell_Number']
df1['d7_CSRanking'] = df1['CS_-_Clean_Coking_Total_Sulphur']
df1['d8_CPRanking'] = df1['CP_-_Clean_Coking_Phosphorous_(P)']



########################################################################################
##
## ADD CALCULATED SEQUENCE FIELD

df1['QS_SEQ'] = np.NaN


df1['Mining_MethodCALC'] = 1000-df1['LW_PANEL']
query = (df1['Mining_Method'] == 'UG') & (df1['ROM_Dev_Tonnes'] > 0)
df1.loc[query, 'QS_SEQ'] = df1.loc[query, 'Mining_MethodCALC']

query = (df1['Mining_Method'] == 'UG') & (df1['ROM_Mains_Tonnes'] > 0)
df1.loc[query, 'QS_SEQ'] = df1.loc[query, 'Mining_MethodCALC']

df1['Mining_MethodCALC'] = 1000-(df1['LW_PANEL']+1)
query = (df1['Mining_Method'] == 'UG') & (df1['ROM_LW_Tonnes'] > 0)
df1.loc[query, 'QS_SEQ'] = df1.loc[query, 'Mining_MethodCALC']


df1['Mining_MethodCALC'] = 10000-(df1['HORIZON_Number']) + 1000000-(df1['STRIP']*10000) + 250000000-(df1['RF_Shell_No']*100000000)
query = (df1['Mining_Method'] == 'OC') & (df1['MINE'] == 'PRC')
df1.loc[query, 'QS_SEQ'] = df1.loc[query, 'Mining_MethodCALC']

df1['Mining_MethodCALC'] = 10000-(df1['HORIZON_Number']) + 2500000-(df1['RF_Shell_No']*1000000) + 1000000000-(df1['STRIP']*10000000)
query = (df1['Mining_Method'] == 'OC') & (df1['MINE'] != 'PRC')
df1.loc[query, 'QS_SEQ'] = df1.loc[query, 'Mining_MethodCALC']

## ADDED A BENCH COPY TO MAKE THE PHASE PROCESS SIMPLER

df1['BENCH'] = df1['QS_SEQ']

########################################################################################
##
## ADD REQUIRED CALCULATED FIELDS


df1['Best_Product_Value'] = df1['Max_Value'] 

df1['QS_Reblock'] = df1['ROM_Tonnes']+(df1['Waste_Volume']/10) 

df1['Total_Dev_Tonnes'] = df1['ROM_Mains_Tonnes']+df1['ROM_Dev_Tonnes'] 

df1['CombinedProductTonnes'] = 0

df1['MASS'] = df1['ROM_Tonnes']+(df1['Waste_Volume']*2.2)

df1['Best_Product_Total_Tonnes'] = df1['Best_Product_Prim_Tonnes']+df1['Best_Product_Sec_Tonnes']

df1['BestProductThermalCALC'] = df1['Best_Product_Sec_Tonnes']
query = (df1['Best_Product_Name'] == 'Thermal')
df1.loc[query, 'BestProductThermalCALC'] = df1.loc[query, 'Best_Product_Prim_Tonnes']


df1['MaxSpecificEnergyCALC'] = df1['TE_-_Clean_Thermal_Specific_Energy_(MJ/kg)']
query = (df1['CE_-_Clean_Coking_Specific_Energy_(MJ/kg)'] > df1['TE_-_Clean_Thermal_Specific_Energy_(MJ/kg)'])
df1.loc[query, 'MaxSpecificEnergyCALC'] = df1.loc[query, 'CE_-_Clean_Coking_Specific_Energy_(MJ/kg)']
query = (df1['MaxSpecificEnergyCALC'] >= 30.25)
df1.loc[query, 'MaxSpecificEnergyCALC'] = 30.25


df1['MaxSpecificEnergyCALC_WGT'] = df1['Best_Product_Sec_Tonnes']
query = (df1['Best_Product_Name'] == 'Thermal')
df1.loc[query, 'MaxSpecificEnergyCALC_WGT'] = df1.loc[query, 'Best_Product_Prim_Tonnes']
query = (df1['CE_-_Clean_Coking_Specific_Energy_(MJ/kg)'] > df1['TE_-_Clean_Thermal_Specific_Energy_(MJ/kg)'])
df1.loc[query, 'MaxSpecificEnergyCALC_WGT'] = df1.loc[query, 'Best_Product_Prim_Tonnes']


df1['VMCALC'] = np.NaN
query = (df1['TV_-_Clean_Thermal_Volatile_Matter'] >0)
df1.loc[query, 'VMCALC'] = df1.loc[query, 'TV_-_Clean_Thermal_Volatile_Matter']
query = (df1['CV_-_Clean_Coking_Volatile_Matter'] >0)
df1.loc[query, 'VMCALC'] = df1.loc[query, 'CV_-_Clean_Coking_Volatile_Matter']


df1['VMCALC_WGT'] = np.NaN
query = (df1['TV_-_Clean_Thermal_Volatile_Matter'] > 0)
df1.loc[query, 'VMCALC_WGT'] = df1.loc[query, 'Best_Product_Sec_Tonnes']
query = (df1['Best_Product_Name'] == 'Thermal') & (df1['TV_-_Clean_Thermal_Volatile_Matter'] > 0)
df1.loc[query, 'VMCALC_WGT'] = df1.loc[query, 'Best_Product_Prim_Tonnes']
query = (df1['CV_-_Clean_Coking_Volatile_Matter'] >0)
df1.loc[query, 'VMCALC_WGT'] = df1.loc[query, 'Best_Product_Prim_Tonnes']


df1['QS_PrimAsh'] = np.NaN
query = (df1['PIT'] == 'DN') | (df1['PIT'] == 'DP15') | (df1['PIT'] == 'DP612') | (df1['PIT'] == 'DP1319') | (df1['PIT'] == 'DP2024') | (df1['PIT'] == 'COC') 
df1.loc[query, 'QS_PrimAsh'] = df1.loc[query, '2_Stage_Prim_Wash_Ash']
query = (df1['PIT'] == 'DS') | (df1['PIT'] == 'Theo') | (df1['PIT'] == 'GTAQ') | (df1['PIT'] == 'Grv') | (df1['PIT'] == 'MN') | (df1['PIT'] == 'MS') | (df1['PIT'] == 'BSN') | (df1['PIT'] == 'BSS') | (df1['PIT'] == 'HRZ') | (df1['PIT'] == 'OMG') | (df1['PIT'] == 'RMN') | (df1['PIT'] == 'RNW') | (df1['PIT'] == 'SXE') | (df1['PIT'] == 'SXS') | (df1['PIT'] == 'TRE') | (df1['PIT'] == 'TRS') | (df1['PIT'] == 'WTF') 
df1.loc[query, 'QS_PrimAsh'] = df1.loc[query, '1_Stage_Prim_Wash_Ash']


df1['QS_SecAsh'] = np.NaN
query = (df1['PIT'] == 'DN') | (df1['PIT'] == 'DP15') | (df1['PIT'] == 'DP612') | (df1['PIT'] == 'DP1319') | (df1['PIT'] == 'DP2024') | (df1['PIT'] == 'COC') 
df1.loc[query, 'QS_SecAsh'] = df1.loc[query, '2_Stage_Sec_Wash_Ash']
query = (df1['PIT'] == 'DS') | (df1['PIT'] == 'Theo') | (df1['PIT'] == 'GTAQ') | (df1['PIT'] == 'Grv') | (df1['PIT'] == 'MN') | (df1['PIT'] == 'MS') | (df1['PIT'] == 'BSN') | (df1['PIT'] == 'BSS') | (df1['PIT'] == 'HRZ') | (df1['PIT'] == 'OMG') | (df1['PIT'] == 'RMN') | (df1['PIT'] == 'RNW') | (df1['PIT'] == 'SXE') | (df1['PIT'] == 'SXS') | (df1['PIT'] == 'TRE') | (df1['PIT'] == 'TRS') | (df1['PIT'] == 'WTF') 
df1.loc[query, 'QS_SecAsh'] = 0


df1['QS_Value'] = df1['d1_Ranking']
df1['QS_CSR'] = df1['d2_CSRRanking']
df1['QS_CV'] = df1['d3_CVRanking']
df1['QS_CASH'] = df1['d4_CASHRanking']
df1['QS_CASH_POS'] = df1['d4_CASHRanking']*-1


df1['CHPP_HRS'] = 0
df1['CHPP_HRSCALC'] = df1['ROM_Tonnes']/df1['ProcessingHours']
query = (df1['ProcessingHours'] > 0)
df1.loc[query, 'CHPP_HRS'] = df1.loc[query, 'CHPP_HRSCALC']


########################################################################################
##
## DROP OUT CLOSED LOOP VALIDATION DATASET

# dfcol = pd.Series(list(df1.columns))
# dfcol.to_csv(BLOCKMODEL + '_' + RESERVESET + '_COLUMNS.csv', index=False)




# data_validation  = df1.copy()

# for i, weightedfield in weighted_fields.iterrows():
#     field = weightedfield['Field']
#     weighting = weightedfield['Weighting']
#     print(field + "_" + weighting)
#     data_validation[field + '_TOTAL'] = data_validation[field] * data_validation[weighting]





# validationwtfields = weighted_fields['Field'] + '_TOTAL'
# validationwtfields = validationwtfields.tolist()
# #print(validationwtfields)

# validationsumfields = sum_fields['Field']
# validationsumfields = validationsumfields.tolist()
# #print(validationsumfields)


# data_validation[["PHASENAME"] + validationwtfields + validationsumfields].groupby("PHASENAME").sum().to_csv(BLOCKMODEL + '_' + RESERVESET + '_VALIDATION.csv')
# del data_validation # Validation dump completed



########################################################################################
##
## EXPORT FINAL PREPARED DATASET

df1.to_csv(BLOCKMODEL + '_' + RESERVESET + '_PHASEPREP.csv')
