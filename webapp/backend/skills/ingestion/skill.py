import io
import time
import numpy as np
import pandas as pd
from typing import Any, Dict
from skills.base import BaseSkill, SkillResult

class IngestionSkill(BaseSkill):
    name = "ingestion_config"
    display_name = "1. Data & Config Ingestion"
    version = "1.0.0"
    description = "Parses Excel configuration workbooks and decodes raw block models with multi-encoding support."
    category = "Ingestion"

    def run(self, context: Any, params: Dict[str, Any]) -> SkillResult:
        start_t = time.time()
        logs = []
        try:
            config_source = params.get("config_source")
            dataset_source = params.get("dataset_source")
            config_name = params.get("config_name", "Default Config")
            dataset_name = params.get("dataset_name", "No Block Model Loaded")

            # 1. Parse Excel Configuration
            if config_source is not None:
                logs.append(f"Parsing configuration workbook: {config_name}")
                if isinstance(config_source, bytes):
                    xl = pd.ExcelFile(io.BytesIO(config_source))
                else:
                    xl = pd.ExcelFile(config_source)

                cog_bins = xl.parse('COG_Bins')
                weighted_fields = xl.parse('WeightedFields')
                sum_fields = xl.parse('SumFields')
                field_order = xl.parse('FieldOrder')
                stype_flexorder = xl.parse('STYPE_FlexOrder') if 'STYPE_FlexOrder' in xl.sheet_names else pd.DataFrame()

                # Clean column headers
                for df in [cog_bins, weighted_fields, sum_fields, field_order, stype_flexorder]:
                    if not df.empty:
                        df.columns = df.columns.str.strip()

                stype_sets = 5
                stype_agg_field = 'd1_Ranking'
                stype_agg_type = 'GRADE'
                if 'STYPE_Options' in xl.sheet_names:
                    opts = xl.parse('STYPE_Options')
                    opts.columns = opts.columns.str.strip()
                    if 'STYPE Sets' in opts.columns:
                        stype_sets = int(opts['STYPE Sets'].dropna().iloc[0])
                    if 'STYPE Aggregation Field' in opts.columns:
                        stype_agg_field = str(opts['STYPE Aggregation Field'].dropna().iloc[0])
                    if 'STYPE Aggregation Type' in opts.columns:
                        stype_agg_type = str(opts['STYPE Aggregation Type'].dropna().iloc[0])

                context.raw_config = {
                    'cog_bins': cog_bins,
                    'weighted_fields': weighted_fields,
                    'sum_fields': sum_fields,
                    'field_order': field_order,
                    'stype_flexorder': stype_flexorder,
                    'stype_sets': stype_sets,
                    'stype_agg_field': stype_agg_field,
                    'stype_agg_type': stype_agg_type
                }
                context.config_name = config_name
                logs.append(f"Extracted {len(cog_bins['FIELDNAME'].unique())} COG dimensions and {len(weighted_fields)} weighted fields.")

            # 2. Parse Block Model Dataset
            if dataset_source is not None:
                logs.append(f"Parsing block model dataset: {dataset_name}")
                df_model = None
                if isinstance(dataset_source, pd.DataFrame):
                    df_model = dataset_source.copy()
                elif isinstance(dataset_source, bytes):
                    # Order matters: latin-1/iso-8859-1 map every possible byte
                    # value to a character, so they never raise a decode error -
                    # tried early, they silently "succeed" on genuinely
                    # non-Latin-1 data (e.g. Windows-1252 smart quotes/em-dashes
                    # from an Excel export) instead of falling through to the
                    # encoding that would have decoded it correctly. utf-8-sig
                    # goes first since it's a strict superset of plain utf-8
                    # decoding (identical result when there's no BOM, correctly
                    # strips one when present); cp1252 comes before the
                    # always-succeeds latin-1/iso-8859-1 fallbacks since it's
                    # the far more common real-world source of non-UTF-8 bytes
                    # in these exports and would otherwise never get a chance.
                    for enc in ['utf-8-sig', 'cp1252', 'latin-1', 'iso-8859-1']:
                        try:
                            df_model = pd.read_csv(io.BytesIO(dataset_source), encoding=enc)
                            logs.append(f"Successfully decoded CSV with encoding: {enc}")
                            break
                        except Exception:
                            pass
                    if df_model is None:
                        try:
                            df_model = pd.read_parquet(io.BytesIO(dataset_source))
                            logs.append("Successfully decoded Parquet dataset.")
                        except Exception:
                            pass
                    if df_model is None:
                        try:
                            df_model = pd.read_excel(io.BytesIO(dataset_source))
                            logs.append("Successfully decoded Excel dataset.")
                        except Exception:
                            pass
                else:
                    df_model = pd.read_csv(dataset_source)

                if df_model is None:
                    raise ValueError("Could not parse dataset with any supported encoding (UTF-8, Latin-1, Parquet, Excel).")

                df_model.columns = [str(c).strip().replace(' ', '_') for c in df_model.columns]
                # -99 is this dataset family's null sentinel, but only within
                # numeric fields - scoping to numeric dtypes stops it from
                # nulling a legitimate text/ID field that happens to contain
                # the string "-99". This is still a blanket sentinel across
                # every numeric column (no per-field allowlist exists in the
                # config schema to say which fields actually use -99 as null
                # vs. a real value), so a numeric field that legitimately uses
                # -99 would still be affected - that needs a field-level list
                # from whoever owns the COG_Bins config schema.
                numeric_cols = df_model.select_dtypes(include=[np.number]).columns
                df_model[numeric_cols] = df_model[numeric_cols].replace(-99, np.nan)

                context.block_model_df = df_model
                context.dataset_name = dataset_name
                logs.append(f"Block model loaded: {len(df_model):,} rows and {len(df_model.columns)} columns.")

            exec_time = (time.time() - start_t) * 1000.0
            return SkillResult(
                success=True,
                skill_name=self.name,
                execution_time_ms=round(exec_time, 2),
                logs=logs,
                data={
                    "config_name": context.config_name,
                    "dataset_name": context.dataset_name,
                    "rows_loaded": len(context.block_model_df) if context.block_model_df is not None else 0
                }
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
