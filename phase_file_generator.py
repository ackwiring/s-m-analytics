import pandas as pd
import numpy as np
from datetime import datetime
import os
import os.path
from pandas import read_hdf
import time
from pandas import HDFStore
import multiprocessing
import seaborn as sns
import matplotlib.pyplot as plt
import re


CASHFLOW_BLOCKMODEL = 'MetCoal_ALL_PHASEPREP.csv'

INPUT_SHEET = 'PhaseCalculator_V3_MetCoal_2021-06-03.xlsx'

# Any Phase Preparations should be done prior to this script and fed in via the model above
# DZ = 15
# def phase_prep():
#     # AA TODO: Filter dataset. Add Calculated fields, etc
#     df = pd.read_csv(CASHFLOW_BLOCKMODEL)
#     df['BENCH'] = df['ELEV'] - (DZ/2)
#     df['Volume'] = df['BlockTonnes'] / df['DENTY']
#     return df


def dcog(df_model, cog_bins):
    # regex, assumed fromat is PERC_[0-9]
    regex = re.compile("PERC_*")
    df1 = df_model
    field_names = cog_bins['FIELDNAME'].unique()

    for name in field_names:
        df = cog_bins.query(f"FIELDNAME == '{name}'")

        # get range
        if not df.query("COG_TOP == 'MAX'").empty:
            base_max = df1[f"{name}"].max()
            df.at[df.query("COG_TOP == 'MAX'").index.values[0],"COG_TOP"] = base_max + 10
        base_max = df["COG_TOP"].replace(to_replace = regex, value = np.nan, regex = True).dropna().max()

        if not df.query("COG_CUTOFF == 'MIN'").empty:
            base_min = df1[f"{name}"].min()
            df.at[df.query("COG_CUTOFF == 'MIN'").index.values[0],"COG_CUTOFF"] = base_min - 10
        base_min = df["COG_CUTOFF"].replace(to_replace = regex, value = np.nan, regex = True).dropna().max()

        dcogq = f"{name} > {base_min} & {name} <= {base_max}"
        dcogtemp = pd.DataFrame(df1[f'{name}']).query(dcogq).copy()

        # creat string lists
        top_string_interval = df["COG_TOP"].tolist()
        cutoff_string_interval = df["COG_CUTOFF"].tolist()

        # Convert string value to actual percentile
        count = df.index.values.min()
        for top in top_string_interval:
            if type(top) is str:
                df.at[count,"COG_TOP"] = np.percentile(dcogtemp,int(top.strip(str(regex))))
            count+=1

        count = df.index.values.min()
        for cutoff in cutoff_string_interval:
            if type(cutoff) is str:
                df.at[count,"COG_CUTOFF"] = np.percentile(dcogtemp,int(cutoff.strip(str(regex))))
            count+=1

        # replace cog_bins
        for index in df.index.values:
            cog_bins.at[index,"COG_TOP"] = df.at[index,"COG_TOP"]
            cog_bins.at[index,"COG_CUTOFF"] = df.at[index,"COG_CUTOFF"]

    return cog_bins

def bin_data(df_model, cog_bins):
    """
    Bin data by cog_bins inputs
    """
    # First bin each block by each dimension individually

    max_bins = cog_bins.groupby('FIELDNAME')['INTERVAL'].max()

    dimension_fields = cog_bins['FIELDNAME'].unique()
    for field in dimension_fields:
        intervals = cog_bins.query(f'FIELDNAME == "{field}"')
        for i, interval in intervals.iterrows():
            query = (df_model[field] >= interval['COG_CUTOFF']) & (df_model[field] < interval['COG_TOP'])
            df_model.loc[query, field + '_bin'] = interval['INTERVAL']
            #df_model.loc[query, field + '_binmax'] = max_bins[field]

    # Now combine bins into one unique bin identifier

    # Eg.
    #df_model['BIN'] = 1 + (df_model['d5_P']-1)*1
        #+ (df_model['d4_Al203']-1)*2
        #+ (df_model['d3_Si02']-1)*4
        #+ (df_model['d2_Fe']-1)*4
        #+ (df_model['d1_Ranking']-1)*16

    df_model['BIN'] = 1
    multiplier = 1
    # Important: np.flip() to reverse the order
    for field in np.flip(dimension_fields):
        df_model['BIN'] = df_model['BIN'] + ((df_model[field+'_bin']-1) * multiplier)
        multiplier = multiplier * max_bins[field]
    # AA TODO: This should actually be a cog_bins.groupby() (need to transpose first)

    return df_model

def grouped_weighted_average(self, values, weights, *groupby_args, **groupby_kwargs):
	"""
	:param values: column(s) to take the average of
	:param weights_col: column to weight on
	:param group_args: args to pass into groupby (e.g. the level you want to group on)
	:param group_kwargs: kwargs to pass into groupby
	:return: pandas.Series or pandas.DataFrame

    Created on Thu Mar 16 23:05:37 2017

    @author: slewis
	"""

	if isinstance(values, str):
	    values = [values]

	ss = []
	for value_col in values:
	    df = self.copy()
	    prod_name = 'prod_{v}_{w}'.format(v=value_col, w=weights)
	    weights_name = 'weights_{w}'.format(w=weights)

	    df[prod_name] = df[value_col] * df[weights]
	    df[weights_name] = df[weights].where(~df[prod_name].isnull())
	    df = df.groupby(*groupby_args, **groupby_kwargs).sum()
	    s = df[prod_name] / df[weights_name]
	    s.name = value_col
	    ss.append(s)
	df = pd.concat(ss, axis=1) if len(ss) > 1 else ss[0]
	return df

def group_data(df_model, weighted_fields, group_by_fields):
    """
    Group and weight data by each unique 'Weighting' field in weighted_fields.
    Returns a list of dataframes to be combined with concat later.
    """

    dataframes = []
    for field in weighted_fields['Weighting'].unique():
        cols = weighted_fields.query(f'Weighting == "{field}"')['Field'].unique()
        df = grouped_weighted_average(df_model, cols, field, group_by_fields)
        print('AA DEBUG', field, df.shape)
        dataframes.append(df)

    return dataframes

def calc_phase_files(df_model, cog_bins, weighted_fields, sum_fields, field_order, group_by_fields, output_file_prefix=''):

    #if output_file_prefix != '':
        #output_file_prefix = output_file_prefix + '_'
    if output_file_prefix != '':
        os.makedirs(output_file_prefix, exist_ok=True)

    bin_dimensions = len(cog_bins['FIELDNAME'].unique())

    print(cog_bins)

    df_model = bin_data(df_model, cog_bins)

    grouped_dfs = group_data(df_model, weighted_fields, group_by_fields)

    sum_cols = sum_fields['Field'].unique()
    df_model_summed = df_model.groupby(group_by_fields)[sum_cols].sum()

    # Concat everything together
    #df_model_binned = pd.concat([df_model_summed] + grouped_dfs, axis=1)
    df_model_binned = pd.concat(grouped_dfs + [df_model_summed], axis=1)
    # super important that the benches in the phase file are sorted in descending order.  Otherwise Comet mines upside down. 0 for ascending = False = descending.
    df_model_binned.sort_values(['PHASENAME','BENCH','BIN'], ascending=[1, 0, 1], inplace=True)
    df_model_binned.reset_index(inplace=True)

    # df_model_binned is now ready to write to phase files

    # order phase file columns and remove unneccessary fields
    #fieldslist = field_order['Field'].tolist()
    fieldslist = field_order['Alias'].tolist()
    # We could be dynamic here but Comet does NO checking and would silently continue with erroneous data.
    missing_cols = set(fieldslist) - set(df_model_binned.columns)
    # print('AA DEBUG: missing_cols:', missing_cols)
    # fieldslist = [f for f in fieldslist if f not in missing_cols]

    data_export = df_model_binned[['PHASENAME'] + fieldslist].copy()
    remove_cols=['PHASENAME', 'block_count']
    export_cols = [c for c in data_export.columns if c not in remove_cols]

    data_export.to_csv(output_file_prefix + CASHFLOW_BLOCKMODEL + '_PhaseFile_Data.csv')
    attributes = pd.Series(list(data_export.columns))
    attributes.to_csv(output_file_prefix + CASHFLOW_BLOCKMODEL + '_Attributes.csv', index=False)

    # Dump out a validation dataset to make validation easier
    data_validation = data_export.copy()
    # data_validation = df_model.copy()
    for i, weightedfield in weighted_fields.iterrows():
        field = weightedfield['Field']
        weighting = weightedfield['Weighting']
        print(field + '_' + weighting)
        data_validation[field + '_TOTAL'] = data_validation[field] * data_validation[weighting]


    validationwtfields = weighted_fields['Field'] + '_TOTAL'
    validationwtfields = validationwtfields.tolist()
    #print(validationwtfields)

    validationsumfields = sum_fields['Field']
    validationsumfields = validationsumfields.tolist()
    #print(validationsumfields)

    data_validation[['PHASENAME'] + validationwtfields + validationsumfields].groupby('PHASENAME').sum().to_csv(output_file_prefix + CASHFLOW_BLOCKMODEL + '_Validation.csv')

    #data_validation.groupby('PHASE').sum().to_csv(output_file_prefix + CASHFLOW_BLOCKMODEL + '_Validation.csv')
    del data_validation # Validation dump completed



    ## COMET cannot have NULL's in these data -- Setting all NULL Values to 0 prior to exporting into phase file - MADE DYNAMIC TO ALLOW ADDITION OF -99
    # data_export.fillna(0, inplace = True)
    # AA 20210621 unique NullValue for each field
    for _, r in field_order.iterrows():
        print('fillna():', r['Alias'],r['NullValue'])
        data_export[r['Alias']].fillna(r['NullValue'], inplace=True)




    unique_phase_list = list(data_export['PHASENAME'].unique())
    #for phase_numeric in unique_phase_list: # used when PHASE was an integer
    for phase_string in unique_phase_list:

        # Phase file Header
        #phase = str(int(phase_numeric)).zfill(2) # used when PHASE was an integer
        phase = str(phase_string).zfill(2)
        # phasefile = CASHFLOW_BLOCKMODEL + '_' + phase + '.txt'
        phasefile = output_file_prefix + CASHFLOW_BLOCKMODEL + '_' + phase + '.txt'
        lines = [
              'SOS COMET n-D Phase File Created in Python (phase_file_generator.py) - Phase:' + phase + ' created at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # date/time stamp for header
            , 'File :' + os.path.join(os.getcwd(), phasefile)
            , ''
            , 'NumDims\tNumAtts'
            , str(bin_dimensions) + '\t' + str(data_export.shape[1]-1)

            # , DIM1_Field + '\t' + str(len(bin_list)) + '\t' + bin_list_tab
            # , DIM2_Field + '\t' + str(len(mat_list)) + '\t' + mat_list_tab
            # , ''
        ]

        # Loop through dimensions and create summary lines
        for field in cog_bins['FIELDNAME'].unique():
            dim_bins = cog_bins[ cog_bins['FIELDNAME'] == field ]
            bins = dim_bins['COG_CUTOFF'].astype(str).tolist()
            n_bins = len(bins)
            lines = lines + ['\t'.join([field, str(n_bins)] + bins)]

        lines = lines + ['']
        lines = [l + '\n' for l in lines]

        header = open(phasefile, "w")
        header.writelines(lines)
        header.close()

        # mask = data_export.pit == phase  # mask the file with the pit
        #mask = data_export['PHASE'] == phase_numeric  # mask the file with the pit # used when PHASE was an integer
        mask = data_export['PHASENAME'] == phase_string  # mask the file with the pit
        # df = data_export_no_pit[mask].copy()  # write out the no pit file with the pit mask
        df = data_export[mask].copy()  # write out the no pit file with the pit mask
        with open(phasefile, 'a', newline='') as phasefile:
            df[export_cols].to_csv(phasefile, sep='\t', header=True, index=False)
            phasefile.close()

    ##########################################################################
    ##########################################################################
    #
    ### Create Dimension Plots for Review

    # First bin each block by each dimension individually
    #max_bins = cog_bins.groupby('FIELDNAME').max()['INTERVAL']

    dimension_fields = cog_bins['FIELDNAME'].unique()
    for field in dimension_fields:
        intervals = cog_bins.query(f'FIELDNAME == "{field}"')
        for i, interval in intervals.iterrows():
            query = (df_model[field] >= interval['COG_CUTOFF']) & (df_model[field] < interval['COG_TOP'])
            df_model.loc[query, field + '_bin'] = interval['INTERVAL']
            #df_model.loc[query, field + '_binlabel'] = interval['INTERVAL'] #(interval['COG_TOP']+interval['COG_CUTOFF'])/2

            #df_model.loc[query, field + '_binmax'] = max_bins[field]

        a4_dims = (11.7, 8.27)
        fig, ax = plt.subplots(figsize=a4_dims)
        plt.ticklabel_format(style='plain', axis='y')

        df_model_plot = df_model[['MASS',f'{field}_bin']].groupby(f'{field}_bin',as_index=False).sum()

        df_model_plot.to_csv(output_file_prefix + CASHFLOW_BLOCKMODEL + f'M_{field}_bintonnes.csv')

        sns.barplot(ax=ax, data=df_model_plot, x=f'{field}_bin', y='MASS') #  bins=cogofinterest['COG_CUTOFF'])

        plt.savefig(output_file_prefix + CASHFLOW_BLOCKMODEL + f'M_{field}.jpg', format='jpeg', dpi=70)

    return data_export



def main():
    inputs = pd.ExcelFile(INPUT_SHEET)
    cog_bins = inputs.parse('COG_Bins')
    weighted_fields = inputs.parse('WeightedFields')
    sum_fields = inputs.parse('SumFields')
    field_order = inputs.parse('FieldOrder')

    group_by_fields = ['PHASENAME','BENCH','BIN']

    # df_model = phase_prep()
    df_model = pd.read_csv(CASHFLOW_BLOCKMODEL)


    # If DCOG is required, calculate the cog_bins accordingly # THIS NEEDS TO BE CHANGED TO INCORP MAX AND MIN - BBDEBUG
    # if cog_bins['COG_TOP'].astype(str).str.contains('PERC').any():
    cog_bins = dcog(df_model,cog_bins)
    cog_bins.to_csv(CASHFLOW_BLOCKMODEL + '_DCOG_Bins.csv')

    # Standard Phase Files
    starttime = datetime.now()
    standard_phase_data = calc_phase_files(df_model, cog_bins, weighted_fields, sum_fields, field_order, group_by_fields, output_file_prefix='Standard_PhaseFiles' + os.path.sep)
    endtime = datetime.now()
    print('Standard Phase Files: calc_phase_files(df_model, ...) completed in: ', endtime - starttime)

    standard_cog_bins = cog_bins.copy()
    standard_weighted_fields = weighted_fields.copy()
    standard_field_order = field_order.copy()
    standard_sum_fields = sum_fields.copy()

    # AA 20210630 Extract mtype logic into function
    standard_mtype_phase_data = mtype_calc_phase_files(standard_phase_data.copy(), cog_bins, weighted_fields, sum_fields, field_order, group_by_fields)

    ##########################################################################
    ##########################################################################
    #
    ### Create S Type Phase FIles

    stype_flexorder = inputs.parse('STYPE_FlexOrder')
    stype_options = inputs.parse('STYPE_Options')

    stype_sets = stype_options.loc[stype_options['STYPE Parameter'] == 'STYPE Sets', 'Value']
    stype_aggregation_field = stype_options.loc[stype_options['STYPE Parameter'] == 'STYPE Aggregation Field', 'Value'].iloc[0]
    stype_aggregation_type = stype_options.loc[stype_options['STYPE Parameter'] == 'STYPE Aggregation Type', 'Value'].iloc[0]

    # Eg. [20,40,60,80]
    percentiles = list(range(0,100, int(100/stype_sets)))[1:]
    for percentile in percentiles:
        # stype_reduction(percentile, stype_aggregation_field, stype_aggregation_type, stype_flexorder, standard_phase_data, standard_cog_bins, standard_weighted_fields, sum_fields, standard_field_order, group_by_fields)
        stype_reduction(percentile, stype_aggregation_field, stype_aggregation_type, stype_flexorder, standard_phase_data.copy(), standard_cog_bins, standard_weighted_fields, standard_sum_fields, standard_field_order, group_by_fields)
        
def mtype_calc_phase_files(df_model, cog_bins, weighted_fields, sum_fields, field_order, group_by_fields, output_file_prefix='MTYPE_PhaseFiles' + os.path.sep):
    ##########################################################################
    ##########################################################################
    #
    ### Create M Type Phase FIles

    # Copy standard binning into a new dimension field so BIN can be overwritten

    df_model['STANDARD_BIN'] = df_model['BIN'] # Keep original bins in the model
    df_model['dQS'] = df_model['BIN']
    df_model['dQS_Weighting'] = 1

    # data_export['STANDARD_BIN'] = data_export['BIN'] # Keep original bins in the model
    # data_export['dQS'] = data_export['BIN']

    # Build lookup and associated binning for the M type based on the primary binned dataset
    df_mtypebins = pd.DataFrame(df_model['BIN'].unique())
    df_mtypebins.dropna(inplace=True) # in case these pop up - BB TODO - TRACK DOWN SOURCE OF THESE RECORDS
    df_mtypebins.sort_values(0, inplace=True)

    df_mtypebins['FIELDNAME'] = 'dQS'
    df_mtypebins['INTERVAL'] = 0
    df_mtypebins['COG_CUTOFF'] = df_mtypebins[0]-0.5
    df_mtypebins['COG_TOP'] = df_mtypebins[0].max()+0.5

    n = df_mtypebins[0].count()
    rowid = range(1,n+1)
    df_mtypebins['INTERVAL'] = rowid
    df_mtypebins['INTERVAL_INDEX'] = df_mtypebins['INTERVAL']
    df_mtypebins.set_index('INTERVAL_INDEX', inplace=True)


    for i in range(1, len(df_mtypebins)):
        df_mtypebins.loc[i, 'COG_TOP'] = df_mtypebins.loc[i+1, 'COG_CUTOFF']

    print(df_mtypebins)
    df_mtypebins[['FIELDNAME','INTERVAL','COG_CUTOFF','COG_TOP']].to_csv(output_file_prefix.replace(os.path.sep, '') + '_df_mtypebins.csv')


    # Adapt the field list for the final model export to remove the original dimensions, and slot in dQS

    # Get dimension list from the original COG imported data
    bin_dimension_list = cog_bins['FIELDNAME'].unique().tolist()

    # Modify this dataframe to be the new M-Type Data
    cog_bins = df_mtypebins[['FIELDNAME','INTERVAL','COG_CUTOFF','COG_TOP']]

    # Use the following to build ignore and replacement lists based off that information
    primary_bin_dimension = bin_dimension_list[0]
    bin_dimension_list.remove(primary_bin_dimension)

    # Check for and remove the dimension fields from SUM # BB NOTES wouldnt be done, ignoring for now.

    # Check for and remove the dimension fields from weighted fields and field order table except primary
    weighted_fields = weighted_fields.loc[~weighted_fields['Field'].isin(bin_dimension_list)]

    #field_order = field_order.loc[~field_order['Field'].isin(bin_dimension_list)]
    field_order = field_order.loc[~field_order['Alias'].isin(bin_dimension_list)]

    # Add in dQS into weighting and final field order
    weighted_fields = weighted_fields.replace([primary_bin_dimension],'dQS')
    weighted_fields.loc[weighted_fields['Field']=='dQS', 'Weighting'] = 'dQS_Weighting'
    field_order = field_order.replace([primary_bin_dimension], 'dQS')
    sum_fields = sum_fields.append(pd.DataFrame({'Field': ['dQS_Weighting']}))
    field_order = field_order.append(pd.DataFrame({'Field': ['dQS_Weighting'], 'Alias':['dQS_Weighting'], 'NullValue': [0]}))

    # M-Type Dimension Reduction Phase Files
    starttime = datetime.now()
    data_export = calc_phase_files(df_model, cog_bins, weighted_fields, sum_fields, field_order, group_by_fields, output_file_prefix)
    endtime = datetime.now()
    print('M-Type completed in: ', endtime - starttime)

    # # AA 20210203 Can we M-Type the pre-aggregated phase file data?
    # starttime = datetime.now()
    # data_export = calc_phase_files(data_export, cog_bins, weighted_fields, sum_fields, field_order, group_by_fields, output_file_prefix='MTYPE_PreAggregate_PhaseFiles' + os.path.sep)
    # endtime = datetime.now()
    # print('M-Type from Aggregated model: calc_phase_files(data_export, ...) completed in: ', endtime - starttime)
    
    return data_export

def stype_reduction(percentile, stype_aggregation_field, stype_aggregation_type, stype_flexorder, df_model, cog_bins, weighted_fields, sum_fields, field_order, group_by_fields):
    # SType starts from source input sheet data (per MType)
    # input: standard_phase_data (phase file data, aggregated into bins)
    # input: SType percentile (eg 10)
    # Step 1: Identify bins to be Removed
    # - 'Stype Aggregation Field' - calculate percentile of the agg field
    # - Flag all bins that are lte to the percentile value
    # Step 2: new_bin_seek(oldbins) => (oldbins, newbins)
    # Step 3: re-aggregate phase file data (obey sum_fields, weighted_fields)

    full_cog_bins = calc_bin_table(cog_bins)

    if stype_aggregation_type == 'QUANTITY':
        percentile_value = np.percentile(df_model[stype_aggregation_field], percentile)
        # 'STYPE_Remove' is a boolean True for bins that need to be SType
        # removed.
        df_model['STYPE_Remove'] = df_model[stype_aggregation_field] <= percentile_value
        df_model.to_csv('df_model_STYPE.csv')

        # AA TODO:
        raise Exception("STYPE Aggregation Type: QUANTITY - NOT YET IMPLEMENTED")


    elif stype_aggregation_type == 'GRADE':
        # raise Exception("STYPE Aggregation Type GRADE - NOT YET IMPLEMENTED")

        # Look up weighting field for stype_aggregation_field
        weightingfield = weighted_fields.loc[weighted_fields['Field'] == stype_aggregation_field, 'Weighting'].iloc[0]
        df_model['STYPE_Aggregation'] = df_model[stype_aggregation_field] * df_model[weightingfield]
        df_model_stypeagg = df_model.groupby('BIN').sum().reset_index()
        df_model_stypeagg.to_csv(f'df_model_stypeagg.csv')
        binned_stype_aggregation = df_model_stypeagg['STYPE_Aggregation']

        percentile_value = np.percentile(binned_stype_aggregation, percentile)
        # 'STYPE_Remove' is a boolean True for bins that need to be SType removed.
        df_model_stypeagg['STYPE_Remove'] = df_model_stypeagg['STYPE_Aggregation'] <= percentile_value
        df_model_stypeagg.to_csv('df_model_stypeagg.csv')
        
        # AA 20210623 full_cog_bins can contain bins that don't exist in the dataset, delete those here
        existing_bins = df_model_stypeagg['BIN'].unique()
        for binid in full_cog_bins['BIN_ID'].unique():
            if binid not in existing_bins:
                full_cog_bins = full_cog_bins[ full_cog_bins['BIN_ID'] != binid ]

        bins_to_collapse = df_model_stypeagg[df_model_stypeagg['STYPE_Remove'] == True]['BIN'].unique()
        stype_cog_bins = stype_bin_search(full_cog_bins, bins_to_collapse, stype_flexorder)
        stype_cog_bins.to_csv(f'STYPE_{percentile}_full_cog_bins.csv')

        # Collapse the stype_cog_bins back into the settings sheet cog_bins format
        # stype_cog_bins_min = stype_cog_bins.groupby('STYPE_BIN_ID').min()
        # stype_cog_bins_max = stype_cog_bins.groupby('STYPE_BIN_ID').max()
        stype_cog_bins = stype_cog_bins[stype_cog_bins['BIN_ID'] == stype_cog_bins['STYPE_BIN_ID']] # Remaining bins
        new_cog_bins = collapse_stype_cog_bins(stype_cog_bins, cog_bins)
        new_cog_bins.to_csv(f'STYPE_{percentile}_cog_bins.csv')


        # AA 20210629 Produce Stype N-dimensional and Stype 1-dimensional (MType) phase files
        starttime = datetime.now()
        stype_df_model = calc_phase_files(df_model, new_cog_bins, weighted_fields, sum_fields, field_order, group_by_fields, output_file_prefix=f'STYPE_{percentile}_PhaseFiles' + os.path.sep)
        endtime = datetime.now()
        print(f'S-Type_{percentile} completed in: ', endtime - starttime)
        

        ### AA 20210701
        # - recode df_model['BIN'] to be the matching stype_cog_bins['STYPE_BIN_ID']
        ###
        for _, bin in full_cog_bins.iterrows():
            if bin['BIN_ID'] != bin['STYPE_BIN_ID']:
                df_model['BIN'] = df_model['BIN'].replace(bin['BIN_ID'], bin['STYPE_BIN_ID'])
        
        ###
        ### AA 20210629 Produce Stype 1-dimensional (MType) phase files
        ###
        mtype_calc_phase_files(df_model, new_cog_bins, weighted_fields, sum_fields, field_order, group_by_fields, output_file_prefix=f'STYPE_{percentile}_PhaseFiles_MTYPE' + os.path.sep)

    else:
        raise Exception("STYPE Aggregation Type invalid")
    
def collapse_stype_cog_bins(stype_full_cog_bins, cog_bins):
    """
    Takes stype_full_cog_bins and the original cog_bins dataframes and collapses the stype_full_cog_bins back into the cog_bins shape
    with the INTERVAL, COG_CUTOFF and COG_TOP fields renumbered and expanded to fill the removed stype bins.
    """

    cutoff_cols = [c for c in stype_full_cog_bins.columns if c.endswith('CUTOFF')]
    top_cols = [c for c in stype_full_cog_bins.columns if c.endswith('TOP')]
    fieldname_cols = [c for c in stype_full_cog_bins.columns if c.endswith('FIELDNAME')]
    interval_cols = [c for c in stype_full_cog_bins.columns if c.endswith('INTERVAL')]

    # ###
    # # AA 20210624 sort unique remaining intervals per dimension, and then just expand the cutoffs to match
    # ###
    new_cog_bins = pd.DataFrame(columns=cog_bins.columns)
    new_cog_bins.set_index(['FIELDNAME','INTERVAL'], inplace=True)
    cog_bins.set_index(['FIELDNAME','INTERVAL'], inplace=True)
    intervaltuples = []
    for i in range(0, len(fieldname_cols)):
        fcol = fieldname_cols[i]
        icol = interval_cols[i]
        new_cog_bins = new_cog_bins.append(cog_bins.loc[stype_full_cog_bins.groupby([fcol, icol]).min().index.values])
    cog_bins.reset_index(inplace=True)
    new_cog_bins.reset_index(inplace=True)

    # new_cog_bins.to_csv(f'STYPE_{percentile}_cog_bins_PRE_CUTOFFS.csv')
    
    # AA 20210624 Fix up the cutoffs and renumber the intervals
    dimensions = new_cog_bins['FIELDNAME'].unique()
    for dimension in dimensions:
        query = new_cog_bins['FIELDNAME'] == dimension
        new_cog_bins_subset = new_cog_bins[query].copy()
        next_cog_cutoffs = new_cog_bins_subset['COG_CUTOFF'].shift(-1)
        cog_top = new_cog_bins_subset['COG_TOP']
        diffs = next_cog_cutoffs - cog_top
        cog_top.loc[diffs>0] = next_cog_cutoffs

        new_cog_bins.loc[query, 'COG_TOP'] = cog_top

    # AA 20210625 Do the loop above again but for FLEX UP not FLEX DOWN SType fields
    for dimension in dimensions:
        query = new_cog_bins['FIELDNAME'] == dimension
        new_cog_bins_subset = new_cog_bins[query].copy()
        next_cog_cutoffs = new_cog_bins_subset['COG_CUTOFF'].shift(1)
        cog_top = new_cog_bins_subset['COG_TOP']
        diffs = next_cog_cutoffs - cog_top
        cog_top.loc[diffs>0] = next_cog_cutoffs

        new_cog_bins.loc[query, 'COG_TOP'] = cog_top

    
    return new_cog_bins

def stype_bin_search(full_cog_bins, bins_to_collapse, stype_flexorder): # AA DEBUG: This function may be broken
    """
    full_cog_bins = the expanded and flattened cog_bins table with the BIN_ID column and all dimension field info
    bins_to_collapse = a list of BIN_IDs to remove (if possible) Eg. [22, 6, 8, 9]

    Returns full_cog_bins with a new column 'STYPE_BIN_ID' that is the target BIN_ID to collapse into
    """

    dimfields_flexlist = stype_flexorder[stype_flexorder['Flex Order'] > 0].sort_values(by=['Flex Order'])['FIELDNAME'].values

    dimfieldnames = [c for c in full_cog_bins.columns if 'FIELDNAME' in c]
    dimfieldlevels = []
    # eg dimfieldlevels = ['d2_FIELDNAME', 'd1_FIELDNAME', 'd3_FIELDNAME']
    for dimfield in dimfields_flexlist:
        for f in dimfieldnames:
            if full_cog_bins[full_cog_bins[f] == dimfield].shape[0] > 0:
                dimfieldlevels.append(f)
                break

    full_cog_bins['STYPE_BIN_ID'] = full_cog_bins['BIN_ID'] # Set all bins to exactly the same to start with

    # Now update the bins that need to change where possible
    for binid in bins_to_collapse:
        current_bin = full_cog_bins[full_cog_bins['BIN_ID'] == binid].iloc[0]

        # - Sort remaining_cog_bins by 'Flex Order' fields ascending/descending by each fields 'STYPE OPTION'
        # - Filter remaining_cog_bins by 'STYPE OPTION'  gt 'FLEX UP' and lt 'FLEX DOWN'
        # - First result (if any) is the new bin.  If no results then no change possible.

        # eg sortfields = ['d2_INTERVAL', 'INTERVAL', 'd3_INTERVAL']
        sortfields = [f.replace('FIELDNAME', 'INTERVAL') for f in dimfieldnames if current_bin[f] != 'STATIC']
        sortorders = [True if current_bin[f.replace('INTERVAL', 'STYPE OPTION')] == 'FLEX UP' else False for f in sortfields]

        remaining_cog_bins = full_cog_bins.query(f'BIN_ID not in {list(bins_to_collapse)}')
        remaining_cog_bins.sort_values(by=sortfields, ascending=sortorders, inplace=True)

        filter_strings = []
        for f in sortfields:
            stype_option = current_bin[f.replace('INTERVAL', 'STYPE OPTION')] 
            if stype_option == 'FLEX UP':
                filter_string = f'({f} >= {current_bin[f]})'
                filter_strings.append(filter_string)
            elif stype_option == 'FLEX DOWN':
                filter_string = f'({f} <= {current_bin[f]})'
                filter_strings.append(filter_string)
            elif stype_option == 'STATIC':
                filter_string = f'({f} == {current_bin[f]})'
                filter_strings.append(filter_string)
            else:
                raise Exception(f'STYPE OPTION invalid: {stype_option}')
        
        remaining_cog_bins = remaining_cog_bins.query(' & '.join(filter_strings))
        remaining_cog_bins.sort_values(by=sortfields, ascending=sortorders, inplace=True)
        if remaining_cog_bins.shape[0] > 0:
            # First result (if any) is the new bin.  
            new_binid = remaining_cog_bins.iloc[0]['BIN_ID']
            full_cog_bins.loc[full_cog_bins['BIN_ID'] == binid, 'STYPE_BIN_ID'] = new_binid
        else:
            # If no results then no change possible.
            full_cog_bins.loc[full_cog_bins['BIN_ID'] == binid, 'STYPE_BIN_ID'] = binid

    return full_cog_bins

def calc_bin_table(cog_bins):
    """
    Calculate the full bin table with all dimension fields multiplied out by
    each other.
    """
    dimension_fields = cog_bins['FIELDNAME'].unique()
    d1 = dimension_fields[0]
    bin_table = cog_bins[cog_bins['FIELDNAME'] == d1]

    for i in range(1, len(dimension_fields)):
        di = dimension_fields[i]
        di_cog_bins = cog_bins[cog_bins['FIELDNAME'] == di]
        for _, row in di_cog_bins.iterrows():
            bin_table_temp = bin_table.copy()
            for col in row.index:
                bin_table_temp[f'd{i+1}_' + col] = row[col]
            new_cols = set(bin_table_temp) - set(bin_table.columns)
            for col in new_cols:
                bin_table[col] = np.nan
            bin_table = bin_table.append(bin_table_temp)

    # bin_table now contains all the valid bins along with some invalid partial
    # sections with 'd2_FIELDNAME'==nan, 'd3_FIELDNAME'==nan etc
    # Select only the valid bins
    fieldcols = [c for c in bin_table.columns if 'FIELDNAME' in c]
    for f in fieldcols:
        bin_table = bin_table[bin_table[f].notna()]

    bin_table.drop_duplicates(inplace=True)
    bin_table.reset_index(inplace=True)
    bin_table['BIN_ID'] = bin_table.index + 1

    return bin_table


if __name__=="__main__":
    starttime = datetime.now()
    main()

    endtime = datetime.now()
    print('phase_file_generator.py completed in:', endtime - starttime)
