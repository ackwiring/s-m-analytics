import time
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from skills.base import BaseSkill, SkillResult

class STypeReductionSkill(BaseSkill):
    name = "stype_reduction"
    display_name = "3. N-D S-Type Flex Reduction"
    version = "1.0.0"
    description = "Calculates ranking percentiles, flags low-value bins, and collapses dimensions according to priority flex order rules."
    category = "Valuation"

    def calc_bin_table(self, cog_bins: pd.DataFrame) -> pd.DataFrame:
        dim_fields = cog_bins['FIELDNAME'].unique()
        combos = []
        for d in dim_fields:
            sub = cog_bins[cog_bins['FIELDNAME'] == d]
            combos.append(sub[['INTERVAL', 'FIELDNAME', 'STYPE OPTION']].rename(
                columns={'INTERVAL': f"{d}_INTERVAL", 'FIELDNAME': f"{d}_FIELDNAME", 'STYPE OPTION': f"{d}_STYPE_OPTION"}
            ))

        if not combos:
            return pd.DataFrame()

        bin_table = combos[0]
        for c in combos[1:]:
            bin_table = bin_table.merge(c, how='cross')

        bin_table.drop_duplicates(inplace=True)
        bin_table.reset_index(drop=True, inplace=True)
        bin_table['BIN_ID'] = bin_table.index + 1
        return bin_table

    def stype_bin_search(self, full_cog_bins: pd.DataFrame, bins_to_collapse: List[int], stype_flexorder: pd.DataFrame) -> pd.DataFrame:
        if stype_flexorder.empty or full_cog_bins.empty:
            full_cog_bins['STYPE_BIN_ID'] = full_cog_bins['BIN_ID']
            return full_cog_bins

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

    def run(self, context: Any, params: Dict[str, Any]) -> SkillResult:
        start_t = time.time()
        logs = []
        try:
            if context.mtype_phase_data is None or context.mtype_cog_bins is None:
                raise ValueError("Upstream M-Type baseline data not found in context.")

            percentiles = params.get("percentiles", [20.0, 40.0, 60.0, 80.0])
            agg_field = params.get("aggregation_field", "d1_Ranking")
            agg_type = params.get("aggregation_type", "GRADE")
            grade_agg_method = params.get("grade_aggregation_method", "weighted_average")
            flex_rules = params.get("flex_rules", [])

            df_model = context.mtype_phase_data.copy()
            cog_bins = context.mtype_cog_bins.copy()
            weighted_fields = context.raw_config.get('weighted_fields', pd.DataFrame())

            if flex_rules:
                stype_flexorder = pd.DataFrame(flex_rules)
                if 'fieldname' in stype_flexorder.columns:
                    stype_flexorder.rename(columns={'fieldname': 'FIELDNAME', 'flex_order': 'Flex Order'}, inplace=True)
            else:
                stype_flexorder = context.raw_config.get('stype_flexorder', pd.DataFrame())

            full_cog_bins = self.calc_bin_table(cog_bins)
            original_bin_count = len(df_model['BIN'].unique())
            total_mass = float(df_model['MASS'].sum()) if 'MASS' in df_model.columns else 1.0

            results = []
            context.stype_runs = {}

            for percentile in percentiles:
                df_stype = df_model.copy()
                
                if agg_type == 'GRADE':
                    tonnes_field = 'MASS'
                    if not weighted_fields.empty and 'Field' in weighted_fields.columns:
                        match_w = weighted_fields[weighted_fields['Field'] == agg_field]
                        if not match_w.empty:
                            tonnes_field = match_w['Weighting'].iloc[0]

                    if tonnes_field in df_stype.columns and agg_field in df_stype.columns:
                        df_stype['agg_mass'] = df_stype[tonnes_field]
                        df_stype['agg_weight'] = df_stype[agg_field] * df_stype[tonnes_field]
                        bin_summary = df_stype.groupby('BIN', as_index=False).agg({'agg_weight': 'sum', 'agg_mass': 'sum', 'MASS': 'sum'})
                        if grade_agg_method == 'weighted_sum':
                            # Total contained metal per bin (grade*weight summed, not divided
                            # by summed weight) - matches legacy phase_file_generator.py.
                            # A bin needs both grade and tonnage to rank highly; low-tonnage
                            # bins get suppressed even at high grade.
                            bin_summary['calc_grade'] = bin_summary['agg_weight']
                        else:
                            # Weighted-average grade (metal concentration) per bin - a small
                            # but high-grade bin can still rank highly regardless of tonnage.
                            bin_summary['calc_grade'] = bin_summary['agg_weight'] / bin_summary['agg_mass'].replace(0, np.nan)
                        calc_series = bin_summary['calc_grade']
                    else:
                        bin_summary = df_stype.groupby('BIN', as_index=False).agg({'MASS': 'sum'})
                        calc_series = bin_summary['MASS']
                else:
                    bin_summary = df_stype.groupby('BIN', as_index=False).agg({'MASS': 'sum'})
                    calc_series = bin_summary['MASS']

                perc_val = float(np.percentile(calc_series.dropna(), percentile)) if not calc_series.dropna().empty else 0.0
                bin_summary['STYPE_Remove'] = calc_series <= perc_val
                bins_to_collapse = bin_summary[bin_summary['STYPE_Remove']]['BIN'].values

                stype_cog_bins_mapped = self.stype_bin_search(full_cog_bins.copy(), bins_to_collapse, stype_flexorder)
                bin_map = dict(zip(stype_cog_bins_mapped['BIN_ID'], stype_cog_bins_mapped['STYPE_BIN_ID']))
                df_stype['STYPE_BIN'] = df_stype['BIN'].map(bin_map).fillna(df_stype['BIN'])

                reduced_bin_count = len(df_stype['STYPE_BIN'].unique())
                reduction_pct = round(((original_bin_count - reduced_bin_count) / original_bin_count * 100.0) if original_bin_count > 0 else 0.0, 1)

                stype_bin_counts = df_stype.groupby('STYPE_BIN', as_index=False).agg({'MASS': 'sum'})
                bin_distribution = []
                for _, row in stype_bin_counts.iterrows():
                    b_id = int(row['STYPE_BIN'])
                    mass = float(row['MASS'])
                    pct = round((mass / total_mass * 100.0) if total_mass > 0 else 0.0, 2)
                    bin_distribution.append({'bin_id': b_id, 'mass': round(mass, 1), 'percentage': pct})

                run_payload = {
                    'percentile': percentile,
                    'original_bins_count': original_bin_count,
                    'reduced_bins_count': reduced_bin_count,
                    'reduction_pct': reduction_pct,
                    'percentile_value': round(perc_val, 2),
                    'bins_collapsed_count': len(bins_to_collapse),
                    'bin_distribution': bin_distribution,
                    'grade_preservation': {},
                    'mass_preservation_pct': 100.0,
                    'grade_aggregation_method': grade_agg_method if agg_type == 'GRADE' else None
                }
                context.stype_runs[percentile] = {
                    'df_stype': df_stype,
                    'payload': run_payload
                }
                results.append(run_payload)
                logs.append(f"Cut {percentile}%: {original_bin_count} bins -> {reduced_bin_count} bins ({reduction_pct}% reduction)")

            exec_time = (time.time() - start_t) * 1000.0
            return SkillResult(
                success=True,
                skill_name=self.name,
                execution_time_ms=round(exec_time, 2),
                logs=logs,
                data={'results': results}
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
