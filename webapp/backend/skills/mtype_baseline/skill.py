import time
import numpy as np
import pandas as pd
from typing import Any, Dict
from skills.base import BaseSkill, SkillResult

class MTypeBaselineSkill(BaseSkill):
    name = "mtype_baseline"
    display_name = "2. 1D M-Type Baseline Slicing"
    version = "1.0.0"
    description = "Applies 1-dimensional Cut-Off Grade (COG) intervals to slice raw block models into discrete unreduced reserve bins."
    category = "Valuation"

    def dcog(self, df_model: pd.DataFrame, cog_bins: pd.DataFrame) -> pd.DataFrame:
        df1 = df_model
        field_names = cog_bins['FIELDNAME'].unique()
        cog_bins_res = cog_bins.copy()

        for name in field_names:
            if name not in df1.columns:
                continue
            df_sub = cog_bins_res.query(f"FIELDNAME == '{name}'").copy()
            if df_sub.empty:
                continue
            df_sub.sort_values(by=['INTERVAL'], inplace=True)
            # COG_CUTOFF (note: underscore, not a space - the previous
            # 'COG CUTOFF' never matched the real column at all, KeyError on
            # any real config) uses the literal string 'MIN' as a sentinel
            # meaning "the lowest bin has no fixed lower edge - use the
            # data's actual minimum". Resolve it to a real number before
            # using these values as pd.cut() bin edges: left as the string
            # 'MIN', pd.cut can't sort it against numeric edges
            # (TypeError: '<' not supported between 'int' and 'str'), so
            # even after fixing the column name this never ran successfully
            # against the real COG_Bins schema (verified live, 2026-09-01 -
            # every dimension in the production config uses this sentinel).
            # COG_TOP's equivalent 'MAX' sentinel doesn't need the same
            # treatment - top_bound below already always uses the data's
            # actual max as the final bin edge regardless of what COG_TOP's
            # last row says.
            data_min = df1[name].min() if len(df1) > 0 else 0.0
            cutoffs = df_sub['COG_CUTOFF'].replace('MIN', data_min).astype(float).values

            top_bound = df1[name].max() + 0.01 if len(df1) > 0 else 100.0
            bins = np.append(cutoffs, [top_bound])
            bins = np.unique(bins)
            bins.sort()

            labels = range(1, len(bins))
            if len(bins) > 1:
                df1[f"{name}_BIN"] = pd.cut(df1[name], bins=bins, labels=labels, right=False)
                df1[f"{name}_BIN"] = pd.to_numeric(df1[f"{name}_BIN"], errors='coerce').fillna(1).astype(int)

        return cog_bins_res

    def bin_data(self, df_model: pd.DataFrame, cog_bins: pd.DataFrame) -> pd.DataFrame:
        field_names = cog_bins['FIELDNAME'].unique()
        df_binned = df_model.copy()
        
        dim_bins = []
        for name in field_names:
            col_bin = f"{name}_BIN"
            if col_bin in df_binned.columns:
                dim_bins.append(df_binned[col_bin])

        if dim_bins:
            if len(dim_bins) == 1:
                df_binned['BIN'] = dim_bins[0]
            else:
                bin_series = dim_bins[0].astype(str)
                for s in dim_bins[1:]:
                    bin_series = bin_series + "_" + s.astype(str)
                unique_combos = {val: i+1 for i, val in enumerate(bin_series.unique())}
                df_binned['BIN'] = bin_series.map(unique_combos)
        else:
            df_binned['BIN'] = 1

        return df_binned

    def run(self, context: Any, params: Dict[str, Any]) -> SkillResult:
        start_t = time.time()
        logs = []
        try:
            if context.block_model_df is None:
                raise ValueError("No Block Model loaded in workflow context.")
            if not context.raw_config:
                raise ValueError("No Configuration loaded in workflow context.")

            logs.append("Executing 1D COG interval slicing across active dimensions...")
            cog_bins = self.dcog(context.block_model_df, context.raw_config['cog_bins'])
            context.mtype_cog_bins = cog_bins.copy()

            if 'PHASENAME' not in context.block_model_df.columns:
                context.block_model_df['PHASENAME'] = 'Phase01'
            if 'BENCH' not in context.block_model_df.columns:
                context.block_model_df['BENCH'] = 100.0

            df_binned = self.bin_data(context.block_model_df, cog_bins)
            context.mtype_phase_data = df_binned.copy()

            # M-Type bins index
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
            context.mtype_bins_index = df_mtypebins

            total_mass = float(df_binned['MASS'].sum()) if 'MASS' in df_binned.columns else float(len(df_binned))
            bin_counts = df_binned.groupby('BIN', as_index=False).agg({'MASS': 'sum'}) if 'MASS' in df_binned.columns else df_binned.groupby('BIN', as_index=False).size().rename(columns={'size': 'MASS'})
            
            bin_dist = []
            for _, row in bin_counts.iterrows():
                b_id = int(row['BIN'])
                mass = float(row['MASS'])
                pct = round((mass / total_mass * 100.0) if total_mass > 0 else 0.0, 2)
                bin_dist.append({'bin_id': b_id, 'mass': round(mass, 1), 'percentage': pct})

            weighted_summary = {}
            if 'weighted_fields' in context.raw_config:
                for _, r in context.raw_config['weighted_fields'].iterrows():
                    f = r['Field']
                    w = r['Weighting']
                    if f in df_binned.columns and w in df_binned.columns and df_binned[w].sum() > 0:
                        weighted_val = float((df_binned[f] * df_binned[w]).sum() / df_binned[w].sum())
                        weighted_summary[f] = round(weighted_val, 3)

            dims = [str(d) for d in context.raw_config['cog_bins']['FIELDNAME'].unique()]
            phases = [str(p) for p in df_binned['PHASENAME'].dropna().unique()]
            benches = [float(b) for b in df_binned['BENCH'].dropna().unique() if pd.notna(b)]

            context.mtype_summary = {
                'total_mass': round(total_mass, 1),
                'total_bins': len(df_binned['BIN'].unique()),
                'dimension_count': len(dims),
                'phases': phases,
                'benches': benches,
                'bin_distribution': bin_dist,
                'weighted_summary': weighted_summary
            }
            logs.append(f"M-Type baseline generated: {context.mtype_summary['total_bins']} bins sliced across {len(phases)} phases.")

            exec_time = (time.time() - start_t) * 1000.0
            return SkillResult(
                success=True,
                skill_name=self.name,
                execution_time_ms=round(exec_time, 2),
                logs=logs,
                data=context.mtype_summary
            )
        except Exception as e:
            exec_time = (time.time() - start_t) * 1000.0
            return SkillResult(
                success=False,
                skill_name=self.name,
                execution_time_ms=round(exec_time, 2),
                error=str(e),
                logs=logs
            )
