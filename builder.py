import os
import io

os.makedirs('webapp/backend', exist_ok=True)
os.makedirs('webapp/frontend', exist_ok=True)

# 1. Write models.py
models_code = '''from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class FlexOrderRule(BaseModel):
    fieldname: str
    flex_order: int
    flex_option: str = "STATIC" # "STATIC", "FLEX UP", "FLEX DOWN"

class STypeParameters(BaseModel):
    sets: Optional[int] = 5
    percentiles: List[float] = [20.0, 40.0, 60.0, 80.0]
    aggregation_field: str = "d1_Ranking"
    aggregation_type: str = "GRADE" # "GRADE" or "QUANTITY"
    flex_rules: List[FlexOrderRule] = []

class MTypeResult(BaseModel):
    total_mass: float
    total_bins: int
    dimension_count: int
    phases: List[str]
    benches: List[float]
    bin_distribution: List[Dict[str, Any]]
    weighted_summary: Dict[str, float] = {}

class STypePercentileResult(BaseModel):
    percentile: float
    original_bins_count: int
    reduced_bins_count: int
    reduction_pct: float
    percentile_value: float
    bins_collapsed_count: int
    bin_distribution: List[Dict[str, Any]]
    grade_preservation: Dict[str, float] = {}
    mass_preservation_pct: float = 100.0

class FullAnalysisResponse(BaseModel):
    status: str
    message: str
    dataset_name: str
    config_name: str
    mtype_baseline: MTypeResult
    stype_results: List[STypePercentileResult]
    available_dimensions: List[str]
    available_weighted_fields: List[Dict[str, str]]
    available_sum_fields: List[str]
    current_stype_params: STypeParameters
'''

with open('webapp/backend/models.py', 'w', encoding='utf-8') as f:
    f.write(models_code)
print('models.py written.')

# 2. Write engine.py
engine_code = '''import os, io, re, zipfile
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
        if isinstance(bm_source, bytes):
            self.df_model = pd.read_csv(io.BytesIO(bm_source))
        elif isinstance(bm_source, pd.DataFrame):
            self.df_model = bm_source.copy()
        else:
            self.df_model = pd.read_csv(bm_source)
        
        self.df_model.columns = self.df_model.columns.str.replace(' ', '_')
        self.df_model.replace(-99, np.nan, inplace=True)
        return self.df_model

    def generate_synthetic_blockmodel(self, num_rows=2500):
        np.random.seed(42)
        dimensions = self.config['cog_bins']['FIELDNAME'].unique() if 'cog_bins' in self.config else ['d1_Ranking', 'd2_CSRRanking']
        
        phases = ['Pit01', 'Pit02', 'Pit03']
        benches = [100.0, 115.0, 130.0, 145.0, 160.0]
        
        data = {
            'PHASENAME': np.random.choice(phases, num_rows),
            'BENCH': np.random.choice(benches, num_rows),
            'MASS': np.random.uniform(500, 25000, num_rows).round(1),
            'ROM_Tonnes': np.random.uniform(400, 20000, num_rows).round(1),
            'Best_Product_Prim_Tonnes': np.random.uniform(300, 15000, num_rows).round(1),
            'Coal_Loss_Tonnes': np.random.uniform(10, 500, num_rows).round(1),
            'ROM_Coal_Only_Tonnes': np.random.uniform(350, 18000, num_rows).round(1)
        }
        
        for dim in dimensions:
            if 'Ranking' in dim:
                data[dim] = np.random.uniform(60000, 350000, num_rows).round(1)
            elif 'Fe' in dim or 'Cu' in dim:
                data[dim] = np.random.uniform(0.2, 5.0, num_rows).round(3)
            elif 'Yield' in dim:
                data[dim] = np.random.uniform(40.0, 95.0, num_rows).round(2)
            else:
                data[dim] = np.random.uniform(10.0, 100.0, num_rows).round(2)
                
        if 'sum_fields' in self.config:
            for _, r in self.config['sum_fields'].iterrows():
                f = r['Field']
                if f not in data:
                    data[f] = np.random.uniform(100, 5000, num_rows).round(1)
                    
        if 'weighted_fields' in self.config:
            for _, r in self.config['weighted_fields'].iterrows():
                f = r['Field']
                w = r['Weighting']
                if f not in data:
                    data[f] = np.random.uniform(1.0, 80.0, num_rows).round(2)
                if w not in data:
                    data[w] = np.random.uniform(100, 5000, num_rows).round(1)

        self.df_model = pd.DataFrame(data)
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

            remaining = full_cog_bins.query(f'BIN_ID not in {list(bins_to_collapse)}').copy()
            if remaining.empty:
                continue
                
            filter_strings = []
            for f in sortfields:
                opt_col = f.replace('INTERVAL', 'STYPE OPTION')
                stype_option = current_bin[opt_col] if opt_col in current_bin else 'FLEX DOWN'
                if stype_option == 'FLEX UP':
                    filter_strings.append(f'({f} >= {current_bin[f]})')
                elif stype_option == 'FLEX DOWN':
                    filter_strings.append(f'({f} <= {current_bin[f]})')
                elif stype_option == 'STATIC':
                    filter_strings.append(f'({f} == {current_bin[f]})')

            if filter_strings:
                remaining = remaining.query(' & '.join(filter_strings))
                
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
                val_log = f"Percentile: {perc}%\\nOriginal Bins: {meta['original_bins_count']}\\nReduced Bins: {meta['reduced_bins_count']}\\nReduction: {meta['reduction_pct']}%\\n"
                zf.writestr(f'STYPE_{perc}_PhaseFiles/Audit_Report.txt', val_log)
                
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
'''

with open('webapp/backend/engine.py', 'w', encoding='utf-8') as f:
    f.write(engine_code)
print('engine.py written.')

# 3. Write main.py
main_code = '''import os
import io
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from models import STypeParameters, FullAnalysisResponse, MTypeResult, STypePercentileResult, FlexOrderRule
from engine import PhaseEngine

app = FastAPI(title="M and S Type Reserve Phase Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine state
CURRENT_ENGINE = PhaseEngine()
ACTIVE_CONFIG_NAME = "Default (PhaseCalculator_V3)"
ACTIVE_DATASET_NAME = "Synthetic MetCoal Reserve Model"

# Initialize default configuration if available
DEFAULT_EXCEL = "PhaseCalculator_V3_MetCoal_2021-06-03.xlsx"
if os.path.exists(DEFAULT_EXCEL):
    CURRENT_ENGINE.load_config(DEFAULT_EXCEL)
    CURRENT_ENGINE.generate_synthetic_blockmodel()
    CURRENT_ENGINE.run_mtype_baseline()

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "M & S Type Analysis WebApp"}

@app.get("/api/state", response_model=FullAnalysisResponse)
def get_current_state():
    global CURRENT_ENGINE, ACTIVE_CONFIG_NAME, ACTIVE_DATASET_NAME
    if not CURRENT_ENGINE.config or CURRENT_ENGINE.df_model is None:
        if os.path.exists(DEFAULT_EXCEL):
            CURRENT_ENGINE.load_config(DEFAULT_EXCEL)
            CURRENT_ENGINE.generate_synthetic_blockmodel()
            CURRENT_ENGINE.run_mtype_baseline()
        else:
            raise HTTPException(status_code=400, detail="No configuration or dataset loaded.")

    mtype_res = CURRENT_ENGINE.run_mtype_baseline()
    
    # Extract flex rules
    flex_rules = []
    if 'stype_flexorder' in CURRENT_ENGINE.config and not CURRENT_ENGINE.config['stype_flexorder'].empty:
        for _, r in CURRENT_ENGINE.config['stype_flexorder'].iterrows():
            fieldname = str(r['FIELDNAME']) if 'FIELDNAME' in r else str(r[0])
            flex_order = int(r['Flex Order']) if 'Flex Order' in r else 0
            
            # Lookup default flex option in COG_Bins
            opt = "STATIC"
            if 'cog_bins' in CURRENT_ENGINE.config:
                cog = CURRENT_ENGINE.config['cog_bins']
                sub = cog.query(f"FIELDNAME == '{fieldname}'")
                if not sub.empty and 'STYPE OPTION' in sub.columns:
                    opt = str(sub['STYPE OPTION'].dropna().iloc[0])
            flex_rules.append(FlexOrderRule(fieldname=fieldname, flex_order=flex_order, flex_option=opt))

    stype_params = STypeParameters(
        sets=CURRENT_ENGINE.config.get('stype_sets', 5),
        percentiles=[20.0, 40.0, 60.0, 80.0],
        aggregation_field=CURRENT_ENGINE.config.get('stype_agg_field', 'd1_Ranking'),
        aggregation_type=CURRENT_ENGINE.config.get('stype_agg_type', 'GRADE'),
        flex_rules=flex_rules
    )

    stype_res = CURRENT_ENGINE.run_stype_reduction(
        percentiles=stype_params.percentiles,
        agg_field=stype_params.aggregation_field,
        agg_type=stype_params.aggregation_type,
        flex_rules=[r.dict() for r in stype_params.flex_rules]
    )

    weighted_fields = []
    if 'weighted_fields' in CURRENT_ENGINE.config:
        for _, r in CURRENT_ENGINE.config['weighted_fields'].iterrows():
            weighted_fields.append({"field": str(r['Field']), "weighting": str(r['Weighting'])})

    sum_fields = []
    if 'sum_fields' in CURRENT_ENGINE.config:
        sum_fields = [str(f) for f in CURRENT_ENGINE.config['sum_fields']['Field'].unique()]

    dims = [str(d) for d in CURRENT_ENGINE.config['cog_bins']['FIELDNAME'].unique()] if 'cog_bins' in CURRENT_ENGINE.config else []

    return FullAnalysisResponse(
        status="success",
        message="Current analysis state loaded successfully.",
        dataset_name=ACTIVE_DATASET_NAME,
        config_name=ACTIVE_CONFIG_NAME,
        mtype_baseline=MTypeResult(**mtype_res),
        stype_results=[STypePercentileResult(**r) for r in stype_res],
        available_dimensions=dims,
        available_weighted_fields=weighted_fields,
        available_sum_fields=sum_fields,
        current_stype_params=stype_params
    )

@app.post("/api/upload-files")
async def upload_files(
    config_file: Optional[UploadFile] = File(None),
    dataset_file: Optional[UploadFile] = File(None)
):
    global CURRENT_ENGINE, ACTIVE_CONFIG_NAME, ACTIVE_DATASET_NAME
    
    if config_file is not None:
        contents = await config_file.read()
        CURRENT_ENGINE.load_config(contents)
        ACTIVE_CONFIG_NAME = config_file.filename

    if dataset_file is not None:
        contents = await dataset_file.read()
        CURRENT_ENGINE.load_blockmodel(contents)
        ACTIVE_DATASET_NAME = dataset_file.filename
    elif CURRENT_ENGINE.df_model is None:
        CURRENT_ENGINE.generate_synthetic_blockmodel()
        ACTIVE_DATASET_NAME = "Synthetic MetCoal Reserve Model"

    return get_current_state()

@app.post("/api/run-stype", response_model=FullAnalysisResponse)
def run_stype(params: STypeParameters):
    global CURRENT_ENGINE
    if not CURRENT_ENGINE.config or CURRENT_ENGINE.df_model is None:
        raise HTTPException(status_code=400, detail="Engine not initialized with data.")

    stype_res = CURRENT_ENGINE.run_stype_reduction(
        percentiles=params.percentiles,
        agg_field=params.aggregation_field,
        agg_type=params.aggregation_type,
        flex_rules=[r.dict() for r in params.flex_rules]
    )

    state = get_current_state()
    state.stype_results = [STypePercentileResult(**r) for r in stype_res]
    state.current_stype_params = params
    return state

@app.get("/api/export-zip")
def export_zip():
    global CURRENT_ENGINE
    if not CURRENT_ENGINE.stype_results_cache:
        raise HTTPException(status_code=400, detail="No calculation results available for export.")
    
    zip_bytes = CURRENT_ENGINE.export_zip_bundle()
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=MetCoal_PhaseFiles_Export.zip"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''

with open('webapp/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(main_code)
print('main.py written.')

# ----------------- FRONTEND COMPONENTS ----------------- #
os.makedirs('webapp/frontend/src/components', exist_ok=True)

# 1. DragDropCanvas.jsx
dragdrop_code = '''import React, { useState } from "react";
import { UploadCloud, FileSpreadsheet, Database, CheckCircle, AlertCircle } from "lucide-react";

export default function DragDropCanvas({ onUpload, isUploading, uploadStatus, children }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (!files.length) return;

    let configFile = null;
    let datasetFile = null;

    files.forEach(f => {
      if (f.name.endsWith('.xlsx') || f.name.endsWith('.xls')) {
        configFile = f;
      } else if (f.name.endsWith('.csv') || f.name.endsWith('.parquet') || f.name.endsWith('.txt')) {
        datasetFile = f;
      }
    });

    if (configFile || datasetFile) {
      await onUpload(configFile, datasetFile);
    }
  };

  const handleManualUpload = async (e, type) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (type === 'config') {
      await onUpload(file, null);
    } else {
      await onUpload(null, file);
    }
  };

  return (
    <div 
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="relative min-h-screen w-full bg-white flex"
    >
      {/* Drag & Drop Visual Overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-50 bg-[#0a192f]/90 flex flex-col items-center justify-center p-8 backdrop-blur-sm border-4 border-dashed border-[#ea580c]">
          <UploadCloud className="w-20 h-20 text-[#ea580c] animate-bounce mb-4" />
          <h2 className="text-3xl font-bold text-white mb-2">Drop Files to Ingest Data</h2>
          <p className="text-[#0d9488] font-medium text-lg text-center max-w-md">
            Drop your <span className="text-white font-semibold">PhaseCalculator Config (.xlsx)</span> or <span className="text-white font-semibold">Block Model (.csv, .parquet)</span> anywhere.
          </p>
        </div>
      )}

      {/* Uploading Status Banner */}
      {isUploading && (
        <div className="fixed bottom-6 right-6 z-40 bg-[#0a192f] border-2 border-black rounded-md px-6 py-3 text-white shadow-xl flex items-center gap-3">
          <div className="w-4 h-4 border-2 border-[#ea580c] border-t-transparent rounded-full animate-spin"></div>
          <span className="font-semibold text-sm">Processing uploaded dataset...</span>
        </div>
      )}

      {children}
    </div>
  );
}
'''

with open('webapp/frontend/src/components/DragDropCanvas.jsx', 'w', encoding='utf-8') as f:
    f.write(dragdrop_code)
print('DragDropCanvas.jsx written.')

# 2. Sidebar.jsx
sidebar_code = '''import React from "react";
import { Layers, Sliders, BarChart3, Download, FileText, Database, ShieldCheck, RefreshCw } from "lucide-react";

export default function Sidebar({ activeTab, setActiveTab, appState, onResetSample }) {
  const tabs = [
    { id: "mtype", label: "1. Base M-Type Baseline", icon: Layers, desc: "Standard 1D Cutoff Bins" },
    { id: "stype", label: "2. S-Type Parameter Tuning", icon: Sliders, desc: "Percentiles & Flex Rules" },
    { id: "comparison", label: "3. Comparative Analytics", icon: BarChart3, desc: "Bin Reduction & Preservation" },
    { id: "export", label: "4. Export Phase Files", icon: Download, desc: "COMET Package Download" },
  ];

  return (
    <aside className="w-72 bg-[#0a192f] text-slate-200 flex flex-col justify-between border-r-2 border-black flex-shrink-0 h-screen sticky top-0">
      <div>
        {/* App Branding */}
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2 mb-1">
            <Layers className="w-6 h-6 text-[#ea580c]" />
            <h1 className="text-xl font-bold text-white tracking-tight">PhaseAnalyzer</h1>
          </div>
          <p className="text-xs font-semibold text-[#0d9488] uppercase tracking-wider">
            M & S Type Reserve Engine
          </p>
        </div>

        {/* Navigation Tabs */}
        <nav className="p-4 space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-start gap-3 p-3 rounded-md border text-left transition-all ${
                  isActive
                    ? "bg-[#1e293b] border-[#ea580c] text-white shadow-md"
                    : "bg-transparent border-transparent text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <Icon className={`w-5 h-5 mt-0.5 ${isActive ? "text-[#ea580c]" : "text-[#0d9488]"}`} />
                <div>
                  <div className="font-semibold text-sm leading-snug">{tab.label}</div>
                  <div className="text-xs text-slate-400 font-normal">{tab.desc}</div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Active Data Context Status */}
      <div className="p-4 border-t border-slate-800 space-y-3 bg-[#081224]">
        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Workspace</div>
        
        <div className="bg-slate-900/90 p-2.5 rounded border border-slate-700 text-xs space-y-1.5">
          <div className="flex items-center gap-2 text-slate-300 truncate">
            <FileText className="w-3.5 h-3.5 text-[#ea580c] flex-shrink-0" />
            <span className="truncate font-mono" title={appState?.config_name}>{appState?.config_name || "None loaded"}</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300 truncate">
            <Database className="w-3.5 h-3.5 text-[#0d9488] flex-shrink-0" />
            <span className="truncate font-mono" title={appState?.dataset_name}>{appState?.dataset_name || "None loaded"}</span>
          </div>
        </div>

        <button
          onClick={onResetSample}
          className="w-full flex items-center justify-center gap-2 text-xs py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-600 transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-[#ea580c]" />
          Reload Sample Model
        </button>

        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" /> MetCoal Engine v26
          </span>
          <span>Port 1943</span>
        </div>
      </div>
    </aside>
  );
}
'''

with open('webapp/frontend/src/components/Sidebar.jsx', 'w', encoding='utf-8') as f:
    f.write(sidebar_code)
print('Sidebar.jsx written.')

# 3. MTypeBaselineView.jsx
mtype_view_code = '''import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { Layers, Database, Sparkles, Scale, Grid, ArrowRight } from "lucide-react";

export default function MTypeBaselineView({ appState, onProceedToStype }) {
  const mtype = appState?.mtype_baseline;
  if (!mtype) return null;

  const chartData = (mtype.bin_distribution || []).map(b => ({
    name: `Bin ${b.bin_id}`,
    mass: b.mass,
    percentage: b.percentage
  }));

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold title-orange">Stage 1: Base M-Type Analysis</h2>
          <p className="subtitle-teal text-sm">
            Unreduced 1-Dimensional Cut-Off Grade (COG) baseline calculated directly from the block model.
          </p>
        </div>
        <button
          onClick={onProceedToStype}
          className="btn-primary px-5 py-2.5 flex items-center gap-2 text-sm"
        >
          <span>Tune S-Type Parameters</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="app-card p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            <Scale className="w-4 h-4 text-[#ea580c]" /> Total Reserve Mass
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {mtype.total_mass.toLocaleString()} <span className="text-xs font-normal text-slate-600">Tonnes</span>
          </div>
        </div>

        <div className="app-card p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            <Grid className="w-4 h-4 text-[#0d9488]" /> Total Active Bins
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {mtype.total_bins} <span className="text-xs font-normal text-slate-600">Discrete Bins</span>
          </div>
        </div>

        <div className="app-card p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            <Layers className="w-4 h-4 text-[#ea580c]" /> Active Phases
          </div>
          <div className="text-xl font-bold text-slate-900 truncate">
            {mtype.phases.join(", ") || "None"}
          </div>
        </div>

        <div className="app-card p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4 text-[#0d9488]" /> Dimension Fields
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {mtype.dimension_count} <span className="text-xs font-normal text-slate-600">COG Dimensions</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid: Chart & Weighted Grades */}
      <div className="grid grid-cols-3 gap-6">
        {/* Baseline Bin Distribution Chart */}
        <div className="col-span-2 app-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Baseline Bin Mass Distribution</h3>
              <p className="text-xs subtitle-teal">Unreduced mass distribution across discrete COG intervals</p>
            </div>
            <span className="px-2.5 py-1 text-xs font-semibold rounded bg-slate-200 border border-slate-800">
              {mtype.total_bins} Bins Sliced
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                <XAxis dataKey="name" stroke="#475569" fontSize={11} interval={0} />
                <YAxis stroke="#475569" fontSize={11} />
                <Tooltip 
                  formatter={(val) => [`${val.toLocaleString()} Tonnes`, "Mass"]}
                  contentStyle={{ backgroundColor: "#0f172a", border: "1.5px solid black", borderRadius: "6px", color: "#fff" }}
                />
                <Bar dataKey="mass" fill="#ea580c" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weighted Grades Table */}
        <div className="app-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-base text-slate-900 mb-1">Weighted Head Grades</h3>
            <p className="text-xs subtitle-teal mb-4">Calculated against designated mass weightings</p>

            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {Object.entries(mtype.weighted_summary || {}).map(([field, val]) => (
                <div key={field} className="app-card-sm p-2.5 flex items-center justify-between">
                  <span className="text-xs font-mono font-medium text-slate-700 truncate mr-2" title={field}>
                    {field}
                  </span>
                  <span className="text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-300">
                    {val}
                  </span>
                </div>
              ))}
              {Object.keys(mtype.weighted_summary || {}).length === 0 && (
                <div className="text-xs text-slate-500 italic p-4 text-center">No weighted grade fields configured.</div>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-300 text-xs text-slate-600">
            <span className="font-semibold text-slate-900">Next Step:</span> Proceed to the S-Type dashboard to collapse low-priority bins.
          </div>
        </div>
      </div>
    </div>
  );
}
'''

with open('webapp/frontend/src/components/MTypeBaselineView.jsx', 'w', encoding='utf-8') as f:
    f.write(mtype_view_code)
print('MTypeBaselineView.jsx written.')

# 4. STypeDashboard.jsx
stype_dashboard_code = '''import React, { useState } from "react";
import { Sliders, CheckCircle2, Play, RefreshCw, Layers, ArrowDownUp } from "lucide-react";

export default function STypeDashboard({ appState, onRunStype, isCalculating }) {
  const currentParams = appState?.current_stype_params || {
    sets: 5,
    percentiles: [20.0, 40.0, 60.0, 80.0],
    aggregation_field: "d1_Ranking",
    aggregation_type: "GRADE",
    flex_rules: []
  };

  const [aggField, setAggField] = useState(currentParams.aggregation_field);
  const [aggType, setAggType] = useState(currentParams.aggregation_type);
  const [numSets, setNumSets] = useState(currentParams.sets || 5);
  const [customPercentiles, setCustomPercentiles] = useState(currentParams.percentiles.join(", "));
  const [flexRules, setFlexRules] = useState(currentParams.flex_rules || []);

  const handleFlexOrderChange = (idx, newOrder) => {
    const updated = [...flexRules];
    updated[idx].flex_order = parseInt(newOrder) || 0;
    setFlexRules(updated);
  };

  const handleFlexOptionChange = (idx, newOption) => {
    const updated = [...flexRules];
    updated[idx].flex_option = newOption;
    setFlexRules(updated);
  };

  const handleSetsChange = (sets) => {
    const val = parseInt(sets);
    setNumSets(val);
    const step = 100 / val;
    const percs = [];
    for (let p = step; p < 100; p += step) {
      percs.push(Math.round(p));
    }
    setCustomPercentiles(percs.join(", "));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const parsedPercentiles = customPercentiles
      .split(",")
      .map(s => parseFloat(s.trim()))
      .filter(n => !isNaN(n) && n > 0 && n < 100);

    onRunStype({
      sets: numSets,
      percentiles: parsedPercentiles.length ? parsedPercentiles : [20.0, 40.0, 60.0, 80.0],
      aggregation_field: aggField,
      aggregation_type: aggType,
      flex_rules: flexRules
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold title-orange">Stage 2: S-Type Parameter Tuning</h2>
          <p className="subtitle-teal text-sm">
            Adjust percentile intervals, ranking drivers, and dimension flex rules to optimize bin reduction.
          </p>
        </div>
        <button
          type="submit"
          disabled={isCalculating}
          className="btn-primary px-6 py-2.5 flex items-center gap-2 text-sm"
        >
          {isCalculating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Calculating Reduction...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute S-Type Reduction</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Col: Aggregation Drivers */}
        <div className="app-card p-5 space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-200 pb-2">
            1. Aggregation Driver
          </h3>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              STYPE Aggregation Field
            </label>
            <select
              value={aggField}
              onChange={(e) => setAggField(e.target.value)}
              className="w-full bg-white border border-black rounded px-3 py-2 text-sm text-slate-900 font-mono focus:ring-2 focus:ring-[#ea580c]"
            >
              {(appState?.available_dimensions || ["d1_Ranking"]).map((dim) => (
                <option key={dim} value={dim}>{dim}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              STYPE Aggregation Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setAggType("GRADE")}
                className={`py-2 text-xs font-bold rounded border transition ${
                  aggType === "GRADE"
                    ? "bg-[#0a192f] text-white border-black"
                    : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
                }`}
              >
                GRADE (Weighted)
              </button>
              <button
                type="button"
                onClick={() => setAggType("QUANTITY")}
                className={`py-2 text-xs font-bold rounded border transition ${
                  aggType === "QUANTITY"
                    ? "bg-[#0a192f] text-white border-black"
                    : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
                }`}
              >
                QUANTITY (Summed)
              </button>
            </div>
          </div>
        </div>

        {/* Middle Col: Percentiles Control */}
        <div className="app-card p-5 space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-200 pb-2">
            2. Percentile Intervals
          </h3>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-slate-700">Preset S-Type Sets ({numSets})</label>
              <span className="text-xs text-[#0d9488] font-bold">100 / {numSets} = {100 / numSets}% steps</span>
            </div>
            <input
              type="range"
              min="2"
              max="10"
              value={numSets}
              onChange={(e) => handleSetsChange(e.target.value)}
              className="w-full accent-[#ea580c]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Active Percentile Cuts (%)
            </label>
            <input
              type="text"
              value={customPercentiles}
              onChange={(e) => setCustomPercentiles(e.target.value)}
              placeholder="e.g. 20, 40, 60, 80"
              className="w-full bg-white border border-black rounded px-3 py-2 text-sm font-mono text-slate-900 focus:ring-2 focus:ring-[#ea580c]"
            />
            <p className="text-[11px] text-slate-500 mt-1">Comma-separated percentile cuts to generate.</p>
          </div>
        </div>

        {/* Right Col: Summary Overview */}
        <div className="app-card p-5 space-y-3 bg-slate-100">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-300 pb-2">
            Configuration Notes
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            <strong className="text-slate-900">Flexing Mechanics:</strong> Bins falling below each percentile threshold are flagged and merged into neighboring bins using your Flex Rules.
          </p>
          <ul className="text-xs text-slate-600 space-y-1 list-disc list-inside">
            <li><span className="font-semibold text-slate-900">FLEX UP:</span> Merges into higher bin interval.</li>
            <li><span className="font-semibold text-slate-900">FLEX DOWN:</span> Merges into lower bin interval.</li>
            <li><span className="font-semibold text-slate-900">STATIC:</span> Preserves exact bin selectivity.</li>
          </ul>
        </div>
      </div>

      {/* Interactive Flex Order & Options Table */}
      <div className="app-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-base text-slate-900">3. Interactive Dimension Flex Table</h3>
            <p className="subtitle-teal text-xs">Define priority sequence and flexing direction for each dimension</p>
          </div>
          <span className="text-xs font-semibold bg-[#0a192f] text-white px-3 py-1 rounded">
            {flexRules.length} Configured Dimensions
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#0a192f] text-white text-xs uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3 rounded-tl">Dimension Field</th>
                <th className="px-4 py-3">Flex Order Priority</th>
                <th className="px-4 py-3">Flex Direction Rule</th>
                <th className="px-4 py-3 rounded-tr">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-300 bg-white">
              {flexRules.map((rule, idx) => (
                <tr key={rule.fieldname} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono font-bold text-slate-900">
                    {rule.fieldname}
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      min="0"
                      max="10"
                      value={rule.flex_order}
                      onChange={(e) => handleFlexOrderChange(idx, e.target.value)}
                      className="w-20 bg-slate-50 border border-black rounded px-2 py-1 text-sm font-bold text-slate-900 text-center"
                    />
                    <span className="text-xs text-slate-500 ml-2">
                      {rule.flex_order === 0 ? "(Ignored)" : `Priority ${rule.flex_order}`}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={rule.flex_option}
                      onChange={(e) => handleFlexOptionChange(idx, e.target.value)}
                      className="bg-slate-50 border border-black rounded px-3 py-1.5 text-xs font-bold text-slate-900"
                    >
                      <option value="FLEX DOWN">FLEX DOWN (Collapse to lower)</option>
                      <option value="FLEX UP">FLEX UP (Collapse to upper)</option>
                      <option value="STATIC">STATIC (Do not collapse)</option>
                    </select>
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {rule.flex_order > 0 ? (
                      <span className="text-emerald-700 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Active in Collapse
                      </span>
                    ) : (
                      <span className="text-slate-400 font-medium">Bypassed (0)</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </form>
  );
}
'''

with open('webapp/frontend/src/components/STypeDashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(stype_dashboard_code)
print('STypeDashboard.jsx written.')

# 5. ComparisonView.jsx
comparison_view_code = '''import React, { useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { BarChart3, TrendingDown, CheckCircle, Percent, ArrowRight } from "lucide-react";

export default function ComparisonView({ appState, onProceedToExport }) {
  const mtype = appState?.mtype_baseline;
  const stypeResults = appState?.stype_results || [];

  const [selectedPerc, setSelectedPerc] = useState(
    stypeResults.length ? stypeResults[0].percentile : 20.0
  );

  const activeStype = stypeResults.find(r => r.percentile === selectedPerc) || stypeResults[0];

  if (!mtype || !activeStype) {
    return (
      <div className="app-card p-12 text-center">
        <p className="text-slate-600">Please run the S-Type calculation first to view comparative analytics.</p>
      </div>
    );
  }

  // Build combined chart data
  const mtypeDist = mtype.bin_distribution || [];
  const stypeDist = activeStype.bin_distribution || [];

  const chartData = stypeDist.map(b => {
    const orig = mtypeDist.find(m => m.bin_id === b.bin_id);
    return {
      bin: `Bin ${b.bin_id}`,
      Reduced: b.mass,
      Original: orig ? orig.mass : 0,
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold title-orange">Stage 3: Comparative Analysis</h2>
          <p className="subtitle-teal text-sm">
            Evaluate bin collapsing effectiveness and grade preservation across percentiles.
          </p>
        </div>
        <button
          onClick={onProceedToExport}
          className="btn-primary px-5 py-2.5 flex items-center gap-2 text-sm"
        >
          <span>Export Phase Files</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Percentile Selector Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-300 pb-3">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mr-2">Select Percentile:</span>
        {stypeResults.map((res) => (
          <button
            key={res.percentile}
            onClick={() => setSelectedPerc(res.percentile)}
            className={`px-4 py-1.5 text-xs font-bold rounded-md border transition ${
              selectedPerc === res.percentile
                ? "bg-[#ea580c] text-white border-black shadow"
                : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
            }`}
          >
            {res.percentile}% S-Type
          </button>
        ))}
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-4 gap-4">
        <div className="app-card p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            Original Bins
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {activeStype.original_bins_count} <span className="text-xs font-normal text-slate-500">Bins</span>
          </div>
        </div>

        <div className="app-card p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            Reduced Bins ({activeStype.percentile}%)
          </div>
          <div className="text-2xl font-bold text-[#ea580c]">
            {activeStype.reduced_bins_count} <span className="text-xs font-normal text-slate-500">Remaining</span>
          </div>
        </div>

        <div className="app-card p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
            <TrendingDown className="w-4 h-4 text-emerald-600" /> Bin Reduction
          </div>
          <div className="text-2xl font-bold text-emerald-600">
            {activeStype.reduction_pct}% <span className="text-xs font-normal text-slate-500">Reduction</span>
          </div>
        </div>

        <div className="app-card p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
            <CheckCircle className="w-4 h-4 text-[#0d9488]" /> Mass Preservation
          </div>
          <div className="text-2xl font-bold text-slate-900">
            100.0% <span className="text-xs font-normal text-slate-500">Preserved</span>
          </div>
        </div>
      </div>

      {/* Side by Side Chart & Grade Deltas */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 app-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Bin Collapsing Comparison ({activeStype.percentile}% Cut)</h3>
              <p className="subtitle-teal text-xs">Visualizing original vs collapsed bin distribution</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                <XAxis dataKey="bin" stroke="#475569" fontSize={11} />
                <YAxis stroke="#475569" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0f172a", border: "1.5px solid black", borderRadius: "6px", color: "#fff" }}
                />
                <Legend />
                <Bar dataKey="Original" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Reduced" fill="#ea580c" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Grade Preservation Deltas */}
        <div className="app-card p-6 space-y-4">
          <div>
            <h3 className="font-bold text-base text-slate-900 mb-1">Grade Variance Check</h3>
            <p className="subtitle-teal text-xs">Variance (% Delta) from Baseline M-Type</p>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {Object.entries(activeStype.grade_preservation || {}).map(([field, delta]) => (
              <div key={field} className="app-card-sm p-3 flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-800 truncate mr-2" title={field}>
                  {field}
                </span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded border ${
                  Math.abs(delta) < 0.5 
                    ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                    : "bg-amber-100 text-amber-800 border-amber-300"
                }`}>
                  {delta > 0 ? `+${delta}%` : `${delta}%`}
                </span>
              </div>
            ))}
            {Object.keys(activeStype.grade_preservation || {}).length === 0 && (
              <div className="text-xs text-slate-500 italic p-4 text-center">0.0% variance across all fields.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
'''

with open('webapp/frontend/src/components/ComparisonView.jsx', 'w', encoding='utf-8') as f:
    f.write(comparison_view_code)
print('ComparisonView.jsx written.')

# 6. ExportView.jsx
export_view_code = '''import React from "react";
import { Download, FileArchive, CheckCircle2, ShieldAlert } from "lucide-react";

export default function ExportView({ appState }) {
  const handleDownload = () => {
    window.location.href = "/api/export-zip";
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold title-orange">Stage 4: Export Phase Files</h2>
        <p className="subtitle-teal text-sm">
          Download COMET-ready N-dimensional and 1-dimensional phase files and audit reports.
        </p>
      </div>

      <div className="app-card p-8 text-center space-y-6">
        <div className="w-16 h-16 bg-slate-200 border-2 border-black rounded-full flex items-center justify-center mx-auto text-[#ea580c]">
          <FileArchive className="w-8 h-8" />
        </div>

        <div className="max-w-md mx-auto space-y-2">
          <h3 className="text-xl font-bold text-slate-900">Compile & Bundle Deliverables</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Packages the standard M-Type files, all calculated S-Type percentile models, and verification audit sheets into a structured ZIP archive.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 max-w-lg mx-auto text-left text-xs font-mono bg-white p-4 rounded border border-slate-400">
          <div className="space-y-1 text-slate-700">
            <div>📁 MTYPE_PhaseFiles/</div>
            <div className="pl-4 text-slate-500">- Standard_PhaseFile_Data.csv</div>
            <div className="pl-4 text-slate-500">- MTYPE_df_mtypebins.csv</div>
          </div>
          <div className="space-y-1 text-slate-700">
            <div>📁 STYPE_*_PhaseFiles/</div>
            <div className="pl-4 text-slate-500">- STYPE_PhaseFile_Data.csv</div>
            <div className="pl-4 text-slate-500">- Audit_Report.txt</div>
          </div>
        </div>

        <button
          onClick={handleDownload}
          className="btn-primary px-8 py-3 text-base flex items-center gap-3 mx-auto"
        >
          <Download className="w-5 h-5" />
          <span>Download MetCoal_PhaseFiles_Export.zip</span>
        </button>
      </div>
    </div>
  );
}
'''

with open('webapp/frontend/src/components/ExportView.jsx', 'w', encoding='utf-8') as f:
    f.write(export_view_code)
print('ExportView.jsx written.')

# 7. App.jsx
app_code = '''import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import DragDropCanvas from "./components/DragDropCanvas";
import MTypeBaselineView from "./components/MTypeBaselineView";
import STypeDashboard from "./components/STypeDashboard";
import ComparisonView from "./components/ComparisonView";
import ExportView from "./components/ExportView";
import { UploadCloud, CheckCircle } from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("mtype");
  const [appState, setAppState] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchState = async () => {
    try {
      setIsLoading(true);
      const res = await fetch("/api/state");
      if (!res.ok) throw new Error("Failed to load initial engine state.");
      const data = await res.json();
      setAppState(data);
      setErrorMessage(null);
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchState();
  }, []);

  const handleUpload = async (configFile, datasetFile) => {
    try {
      setIsUploading(true);
      const formData = new FormData();
      if (configFile) formData.append("config_file", configFile);
      if (datasetFile) formData.append("dataset_file", datasetFile);

      const res = await fetch("/api/upload-files", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to process uploaded files.");
      const data = await res.json();
      setAppState(data);
      setActiveTab("mtype");
    } catch (err) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRunStype = async (params) => {
    try {
      setIsCalculating(true);
      const res = await fetch("/api/run-stype", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });

      if (!res.ok) throw new Error("S-Type calculation failed.");
      const data = await res.json();
      setAppState(data);
      setActiveTab("comparison");
    } catch (err) {
      alert(`Calculation error: ${err.message}`);
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <DragDropCanvas onUpload={handleUpload} isUploading={isUploading}>
      {/* Dark Navy Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        appState={appState}
        onResetSample={fetchState}
      />

      {/* Main Content Canvas */}
      <main className="flex-1 bg-white p-8 overflow-y-auto h-screen">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Canvas Drag-and-Drop Prompt Bar */}
          <div className="app-card p-3.5 bg-slate-50 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-700">
              <UploadCloud className="w-4 h-4 text-[#ea580c]" />
              <span>
                <strong className="text-slate-900">Drag & Drop Active:</strong> Drag new <code className="bg-slate-200 px-1 py-0.5 rounded">.xlsx</code> or <code className="bg-slate-200 px-1 py-0.5 rounded">.csv</code> files anywhere onto the screen to reload data.
              </span>
            </div>
            <label className="btn-secondary px-3 py-1 cursor-pointer text-xs">
              Browse Files
              <input
                type="file"
                className="hidden"
                accept=".xlsx,.xls,.csv,.parquet,.txt"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  if (file.name.endsWith(".xlsx") || file.name.endsWith(".xls")) {
                    handleUpload(file, null);
                  } else {
                    handleUpload(null, file);
                  }
                }}
              />
            </label>
          </div>

          {/* Active View Render */}
          {isLoading ? (
            <div className="app-card p-16 text-center">
              <div className="w-8 h-8 border-4 border-[#ea580c] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <h3 className="font-bold text-slate-900 text-lg">Initializing Valuation Engine...</h3>
              <p className="subtitle-teal text-xs mt-1">Extracting COG Bins and building M-Type baseline</p>
            </div>
          ) : (
            <>
              {activeTab === "mtype" && (
                <MTypeBaselineView
                  appState={appState}
                  onProceedToStype={() => setActiveTab("stype")}
                />
              )}

              {activeTab === "stype" && (
                <STypeDashboard
                  appState={appState}
                  onRunStype={handleRunStype}
                  isCalculating={isCalculating}
                />
              )}

              {activeTab === "comparison" && (
                <ComparisonView
                  appState={appState}
                  onProceedToExport={() => setActiveTab("export")}
                />
              )}

              {activeTab === "export" && (
                <ExportView appState={appState} />
              )}
            </>
          )}
        </div>
      </main>
    </DragDropCanvas>
  );
}
'''

with open('webapp/frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(app_code)
print('App.jsx written.')
print('All frontend components written successfully.')

