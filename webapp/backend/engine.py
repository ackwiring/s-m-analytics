import os, io, re, zipfile
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

class PhaseEngine:
    def __init__(self, excel_path_or_bytes=None, blockmodel_path_or_bytes=None):
        self.excel_source = excel_path_or_bytes
        self.bm_source = blockmodel_path_or_bytes
        self.config = {}
        self.df_model = None
        self.standard_phase_data = None
        self.standard_cog_bins = None
        self.standard_mtype_bins = None
        self.mtype_baseline_result = None
        self.stype_results_cache = {}
        
        if excel_path_or_bytes is not None:
            self.load_config(excel_path_or_bytes)
        if blockmodel_path_or_bytes is not None:
            self.load_blockmodel(blockmodel_path_or_bytes)

    def load_config(self, excel_source):
        if isinstance(excel_source, bytes):
            excel_file = pd.ExcelFile(io.BytesIO(excel_source))
        else:
            excel_file = pd.ExcelFile(excel_source)
            
        cog_bins = excel_file.parse('COG_Bins')
        weighted_fields = excel_file.parse('WeightedFields')
        sum_fields = excel_file.parse('SumFields')
        field_order = excel_file.parse('FieldOrder')
        
        stype_flexorder = excel_file.parse('STYPE_FlexOrder') if 'STYPE_FlexOrder' in excel_file.sheet_names else pd.DataFrame(columns=['FIELDNAME', 'Flex Order'])
        stype_options = excel_file.parse('STYPE_Options') if 'STYPE_Options' in excel_file.sheet_names else pd.DataFrame(columns=['STYPE Parameter', 'Value'])
        
        cog_bins.dropna(subset=['FIELDNAME'], inplace=True)
        weighted_fields.dropna(subset=['Field', 'Weighting'], inplace=True)
        sum_fields.dropna(subset=['Field'], inplace=True)
        field_order.dropna(subset=['Field', 'Alias'], inplace=True)

        stype_sets = 5
        stype_agg_field = 'd1_Ranking'
        stype_agg_type = 'GRADE'
        
        if not stype_options.empty:
            sets_match = stype_options.loc[stype_options['STYPE Parameter'] == 'STYPE Sets', 'Value']
            if not sets_match.empty and pd.notna(sets_match.values[0]):
                try:
                    stype_sets = int(sets_match.values[0])
                except:
                    stype_sets = 5
            
            agg_match = stype_options.loc[stype_options['STYPE Parameter'] == 'STYPE Aggregation Field', 'Value']
            if not agg_match.empty and pd.notna(agg_match.values[0]):
                stype_agg_field = str(agg_match.values[0]).strip()
                
            type_match = stype_options.loc[stype_options['STYPE Parameter'] == 'STYPE Aggregation Type', 'Value']
            if not type_match.empty and pd.notna(type_match.values[0]):
                stype_agg_type = str(type_match.values[0]).strip().upper()

        self.config = {
            'cog_bins': cog_bins,
            'weighted_fields': weighted_fields,
            'sum_fields': sum_fields,
            'field_order': field_order,
            'stype_flexorder': stype_flexorder,
            'stype_sets': stype_sets,
            'stype_agg_field': stype_agg_field,
            'stype_agg_type': stype_agg_type
        }
        return self.config

    def load_blockmodel(self, bm_source):
        if isinstance(bm_source, pd.DataFrame):
            self.df_model = bm_source.copy()
        elif isinstance(bm_source, bytes):
            # Attempt multi-encoding and multi-format parsing
            loaded = False
            last_err = None
            for enc in ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig', 'iso-8859-1']:
                try:
                    self.df_model = pd.read_csv(io.BytesIO(bm_source), encoding=enc)
                    loaded = True
                    break
                except Exception as e:
                    last_err = e
            
            if not loaded:
                try:
                    self.df_model = pd.read_parquet(io.BytesIO(bm_source))
                    loaded = True
                except Exception:
                    pass

            if not loaded:
                try:
                    self.df_model = pd.read_excel(io.BytesIO(bm_source))
                    loaded = True
                except Exception:
                    pass

            if not loaded:
                raise ValueError(f"Could not parse uploaded dataset. Error: {last_err}")
        else:
            loaded = False
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    self.df_model = pd.read_csv(bm_source, encoding=enc)
                    loaded = True
                    break
                except Exception:
                    pass
            if not loaded:
                self.df_model = pd.read_parquet(bm_source)
        
        self.df_model.columns = [str(c).strip().replace(' ', '_') for c in self.df_model.columns]
        self.df_model.replace(-99, np.nan, inplace=True)
        self.df_model.replace('-99', np.nan, inplace=True)
        return self.df_model



    def dcog(self, df_model, cog_bins):
        df1 = df_model
        field_names = cog_bins['FIELDNAME'].unique()
        cog_bins_res = cog_bins.copy()

        for name in field_names:
            if name not in df1.columns:
                continue
            df_sub = cog_bins_res.query(f"FIELDNAME == '{name}'").copy()
            if df_sub.empty:
                continue

            if not df_sub.query("COG_TOP == 'MAX'").empty:
                base_max = df1[name].max()
                cog_bins_res.loc[(cog_bins_res['FIELDNAME'] == name) & (cog_bins_res['COG_TOP'] == 'MAX'), 'COG_TOP'] = base_max + 10

            if not df_sub.query("COG_CUTOFF == 'MIN'").empty:
                base_min = df1[name].min()
                cog_bins_res.loc[(cog_bins_res['FIELDNAME'] == name) & (cog_bins_res['COG_CUTOFF'] == 'MIN'), 'COG_CUTOFF'] = base_min - 10

        return cog_bins_res

    def bin_data(self, df_model, cog_bins):
        df = df_model.copy()
        max_bins = cog_bins.groupby('FIELDNAME')['INTERVAL'].max()
        dimension_fields = cog_bins['FIELDNAME'].unique()
        
        for field in dimension_fields:
            if field not in df.columns:
                df[field] = 0.0
            intervals = cog_bins.query(f'FIELDNAME == "{field}"')
            df[field + '_bin'] = 1
            for _, interval in intervals.iterrows():
                cutoff = float(interval['COG_CUTOFF']) if str(interval['COG_CUTOFF']).strip() != 'MIN' else -np.inf
                top = float(interval['COG_TOP']) if str(interval['COG_TOP']).strip() != 'MAX' else np.inf
                query = (df[field] >= cutoff) & (df[field] < top)
                df.loc[query, field + '_bin'] = interval['INTERVAL']

        df['BIN'] = 1
        multiplier = 1
        for field in np.flip(dimension_fields):
            m_val = max_bins[field] if field in max_bins and max_bins[field] is not None else 1
            df['BIN'] = df['BIN'] + ((df[field + '_bin'] - 1) * multiplier)
            multiplier = multiplier * int(m_val)

        return df

    def calc_bin_table(self, cog_bins):
        dimension_fields = cog_bins['FIELDNAME'].unique()
        if len(dimension_fields) == 0:
            return pd.DataFrame()
            
        d1 = dimension_fields[0]
        bin_table = cog_bins[cog_bins['FIELDNAME'] == d1].copy()

        for i in range(1, len(dimension_fields)):
            di = dimension_fields[i]
            di_cog_bins = cog_bins[cog_bins['FIELDNAME'] == di]
            temp_list = []
            for _, row in di_cog_bins.iterrows():
                bt_temp = bin_table.copy()
                for col in row.index:
                    bt_temp[f'd{i+1}_{col}'] = row[col]
                temp_list.append(bt_temp)
            if temp_list:
                bin_table = pd.concat(temp_list, ignore_index=True)

        fieldcols = [c for c in bin_table.columns if 'FIELDNAME' in c]
        for f in fieldcols:
            bin_table = bin_table[bin_table[f].notna()]

        bin_table.drop_duplicates(inplace=True)
        bin_table.reset_index(drop=True, inplace=True)
        bin_table['BIN_ID'] = bin_table.index + 1
        return bin_table

    def run_mtype_baseline(self):
        if self.df_model is None:
            raise ValueError("No Block Model loaded.")
        if not self.config:
            raise ValueError("No Configuration loaded.")

        cog_bins = self.dcog(self.df_model, self.config['cog_bins'])
        self.standard_cog_bins = cog_bins.copy()

        if 'PHASENAME' not in self.df_model.columns:
            self.df_model['PHASENAME'] = 'Phase01'
        if 'BENCH' not in self.df_model.columns:
            self.df_model['BENCH'] = 100.0

        df_binned = self.bin_data(self.df_model, cog_bins)
        self.standard_phase_data = df_binned.copy()

        df_mtypebins = pd.DataFrame(df_binned['BIN'].dropna().unique(), columns=[0])
        df_mtypebins.sort_values(0, inplace=True)
        df_mtypebins['FIELDNAME'] = 'dQS'
        df_mtypebins['INTERVAL'] = range(1, len(df_mtypebins) + 1)
        df_mtypebins['COG_CUTOFF'] = df_mtypebins[0] - 0.5
        df_mtypebins['COG_TOP'] = df_mtypebins[0].max() + 0.5
        df_mtypebins.set_index('INTERVAL', drop=False, inplace=True)
        
        for i in range(1, len(df_mtypebins)):
            if (i+1) in df_mtypebins.index:
                df_mtypebins.loc[i, 'COG_TOP'] = df_mtypebins.loc[i+1, 'COG_CUTOFF']
                
        self.standard_mtype_bins = df_mtypebins

        total_mass = float(df_binned['MASS'].sum()) if 'MASS' in df_binned.columns else float(len(df_binned))
        bin_counts = df_binned.groupby('BIN', as_index=False).agg({'MASS': 'sum'}) if 'MASS' in df_binned.columns else df_binned.groupby('BIN', as_index=False).size().rename(columns={'size': 'MASS'})
        
        bin_distribution = []
        for _, row in bin_counts.iterrows():
            b_id = int(row['BIN'])
            mass = float(row['MASS'])
            pct = round((mass / total_mass * 100.0) if total_mass > 0 else 0.0, 2)
            bin_distribution.append({
                'bin_id': b_id,
                'mass': round(mass, 1),
                'percentage': pct
            })

        weighted_summary = {}
        if 'weighted_fields' in self.config:
            for _, r in self.config['weighted_fields'].iterrows():
                f = r['Field']
                w = r['Weighting']
                if f in df_binned.columns and w in df_binned.columns and df_binned[w].sum() > 0:
                    weighted_val = float((df_binned[f] * df_binned[w]).sum() / df_binned[w].sum())
                    weighted_summary[f] = round(weighted_val, 3)

        self.mtype_baseline_result = {
            'total_mass': round(total_mass, 1),
            'total_bins': int(len(bin_counts)),
            'dimension_count': len(cog_bins['FIELDNAME'].unique()),
            'phases': [str(p) for p in df_binned['PHASENAME'].unique()],
            'benches': [float(b) for b in sorted(df_binned['BENCH'].unique())],
            'bin_distribution': bin_distribution,
            'weighted_summary': weighted_summary
        }
        return self.mtype_baseline_result

    def stype_bin_search(self, full_cog_bins, bins_to_collapse, stype_flexorder):
        if stype_flexorder.empty or full_cog_bins.empty:
            full_cog_bins['STYPE_BIN_ID'] = full_cog_bins['BIN_ID']
            return full_cog_bins

        dimfields_flexlist = stype_flexorder[stype_flexorder['Flex Order'] > 0].sort_values(by=['Flex Order'])['FIELDNAME'].values
        dimfieldnames = [c for c in full_cog_bins.columns if 'FIELDNAME' in c]
        
        full_cog_bins['STYPE_BIN_ID'] = full_cog_bins['BIN_ID']
        
        for binid in bins_to_collapse:
            match_rows = full_cog_bins[full_cog_bins['BIN_ID'] == binid]
            if match_rows.empty:
                continue
            current_bin = match_rows.iloc[0]

            sortfields = [f.replace('FIELDNAME', 'INTERVAL') for f in dimfieldnames if f.replace('FIELDNAME', 'INTERVAL') in full_cog_bins.columns and current_bin[f] != 'STATIC']
            sortorders = [True if f.replace('INTERVAL', 'STYPE OPTION') in current_bin and current_bin[f.replace('INTERVAL', 'STYPE OPTION')] == 'FLEX UP' else False for f in sortfields]

            collapse_set = set(int(b) for b in bins_to_collapse if pd.notna(b))
            remaining = full_cog_bins[~full_cog_bins['BIN_ID'].isin(collapse_set)].copy()
            if remaining.empty:
                continue
                
            mask = pd.Series(True, index=remaining.index)
            for f in sortfields:
                opt_col = f.replace('INTERVAL', 'STYPE OPTION')
                stype_option = current_bin[opt_col] if opt_col in current_bin else 'FLEX DOWN'
                val = current_bin[f]
                if stype_option == 'FLEX UP':
                    mask = mask & (remaining[f] >= val)
                elif stype_option == 'FLEX DOWN':
                    mask = mask & (remaining[f] <= val)
                elif stype_option == 'STATIC':
                    mask = mask & (remaining[f] == val)

            remaining = remaining[mask]
                
            if not remaining.empty and sortfields:
                remaining.sort_values(by=sortfields, ascending=sortorders, inplace=True)
                new_binid = remaining.iloc[0]['BIN_ID']
                full_cog_bins.loc[full_cog_bins['BIN_ID'] == binid, 'STYPE_BIN_ID'] = new_binid

        return full_cog_bins

    def run_stype_reduction(self, percentiles: List[float], agg_field: str = 'd1_Ranking', agg_type: str = 'GRADE', flex_rules: Optional[List[Dict]] = None):
        if self.standard_phase_data is None:
            self.run_mtype_baseline()

        df_model = self.standard_phase_data.copy()
        cog_bins = self.standard_cog_bins.copy()
        weighted_fields = self.config['weighted_fields']

        if flex_rules:
            stype_flexorder = pd.DataFrame(flex_rules)
            if 'fieldname' in stype_flexorder.columns:
                stype_flexorder.rename(columns={'fieldname': 'FIELDNAME', 'flex_order': 'Flex Order'}, inplace=True)
        else:
            stype_flexorder = self.config.get('stype_flexorder', pd.DataFrame())

        full_cog_bins = self.calc_bin_table(cog_bins)

        results = []
        original_bin_count = len(df_model['BIN'].unique())
        total_mass = float(df_model['MASS'].sum()) if 'MASS' in df_model.columns else 1.0

        for percentile in percentiles:
            df_stype = df_model.copy()
            
            if agg_type == 'GRADE':
                weighting_match = weighted_fields.loc[weighted_fields['Field'] == agg_field, 'Weighting']
                weighting_col = weighting_match.iloc[0] if not weighting_match.empty and weighting_match.iloc[0] in df_stype.columns else 'ROM_Tonnes'
                if weighting_col not in df_stype.columns:
                    weighting_col = 'MASS' if 'MASS' in df_stype.columns else df_stype.columns[0]
                    
                df_stype['STYPE_Aggregation'] = df_stype[agg_field] * df_stype[weighting_col] if agg_field in df_stype.columns else df_stype['MASS']
                df_agg = df_stype.groupby('BIN', as_index=False)['STYPE_Aggregation'].sum()
                perc_val = float(np.percentile(df_agg['STYPE_Aggregation'], percentile))
                df_agg['STYPE_Remove'] = df_agg['STYPE_Aggregation'] <= perc_val
            else:
                qty_col = agg_field if agg_field in df_stype.columns else 'MASS'
                df_agg = df_stype.groupby('BIN', as_index=False)[qty_col].sum()
                perc_val = float(np.percentile(df_agg[qty_col], percentile))
                df_agg['STYPE_Remove'] = df_agg[qty_col] <= perc_val

            bins_to_collapse = df_agg[df_agg['STYPE_Remove'] == True]['BIN'].unique()
            
            stype_cog_bins_mapped = self.stype_bin_search(full_cog_bins.copy(), bins_to_collapse, stype_flexorder)
            
            remap_dict = dict(zip(stype_cog_bins_mapped['BIN_ID'], stype_cog_bins_mapped['STYPE_BIN_ID']))
            df_stype['REDUCED_BIN'] = df_stype['BIN'].map(remap_dict).fillna(df_stype['BIN'])

            reduced_bin_count = int(len(df_stype['REDUCED_BIN'].unique()))
            reduction_pct = round(((original_bin_count - reduced_bin_count) / original_bin_count * 100.0) if original_bin_count > 0 else 0.0, 1)

            agg_reduced = df_stype.groupby('REDUCED_BIN', as_index=False).agg({'MASS': 'sum'}) if 'MASS' in df_stype.columns else df_stype.groupby('REDUCED_BIN', as_index=False).size().rename(columns={'size': 'MASS'})
            
            dist = []
            for _, r in agg_reduced.iterrows():
                b_id = int(r['REDUCED_BIN'])
                mass = float(r['MASS'])
                dist.append({
                    'bin_id': b_id,
                    'mass': round(mass, 1),
                    'percentage': round((mass / total_mass * 100.0) if total_mass > 0 else 0.0, 2)
                })

            grade_preservation = {}
            if 'weighted_fields' in self.config:
                for _, r in self.config['weighted_fields'].iterrows():
                    f = r['Field']
                    w = r['Weighting']
                    if f in df_stype.columns and w in df_stype.columns and df_stype[w].sum() > 0:
                        orig_val = float((df_model[f] * df_model[w]).sum() / df_model[w].sum())
                        red_val = float((df_stype[f] * df_stype[w]).sum() / df_stype[w].sum())
                        delta = round(((red_val - orig_val) / orig_val * 100.0) if orig_val != 0 else 0.0, 3)
                        grade_preservation[f] = delta

            res_item = {
                'percentile': float(percentile),
                'original_bins_count': original_bin_count,
                'reduced_bins_count': reduced_bin_count,
                'reduction_pct': reduction_pct,
                'percentile_value': round(perc_val, 2),
                'bins_collapsed_count': len(bins_to_collapse),
                'bin_distribution': dist,
                'grade_preservation': grade_preservation,
                'mass_preservation_pct': 100.0
            }
            results.append(res_item)
            self.stype_results_cache[percentile] = (df_stype, res_item)

        return results

    def export_zip_bundle(self) -> bytes:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            if self.standard_phase_data is not None:
                mtype_csv = self.standard_phase_data.to_csv(index=False)
                zf.writestr('MTYPE_PhaseFiles/Standard_PhaseFile_Data.csv', mtype_csv)
                if self.standard_mtype_bins is not None:
                    zf.writestr('MTYPE_PhaseFiles/MTYPE_df_mtypebins.csv', self.standard_mtype_bins.to_csv())
            
            for perc, (df_stype, meta) in self.stype_results_cache.items():
                stype_csv = df_stype.to_csv(index=False)
                zf.writestr(f'STYPE_{perc}_PhaseFiles/STYPE_{perc}_PhaseFile_Data.csv', stype_csv)
                val_log = f"Percentile: {perc}%\nOriginal Bins: {meta['original_bins_count']}\nReduced Bins: {meta['reduced_bins_count']}\nReduction: {meta['reduction_pct']}%\n"
                zf.writestr(f'STYPE_{perc}_PhaseFiles/Audit_Report.txt', val_log)
                
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
