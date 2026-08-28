import io
import time
import zipfile
import pandas as pd
from typing import Any, Dict
from skills.base import BaseSkill, SkillResult

class ExportBundleSkill(BaseSkill):
    name = "export_bundle"
    display_name = "5. COMET Deliverables Packager"
    version = "1.0.0"
    description = "Packages standard 1D and collapsed N-D phase files along with QA audit reports into a structured ZIP bundle."
    category = "Export"

    def run(self, context: Any, params: Dict[str, Any]) -> SkillResult:
        start_t = time.time()
        logs = []
        try:
            if context.mtype_phase_data is None:
                raise ValueError("No baseline phase data available for export.")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 1. MTYPE standard files
                mtype_csv = context.mtype_phase_data.to_csv(index=False)
                zf.writestr("MTYPE_PhaseFiles/Standard_PhaseFile_Data.csv", mtype_csv)
                logs.append("Bundled MTYPE_PhaseFiles/Standard_PhaseFile_Data.csv")

                if hasattr(context, 'mtype_bins_index') and context.mtype_bins_index is not None:
                    bins_csv = context.mtype_bins_index.to_csv(index=False)
                    zf.writestr("MTYPE_PhaseFiles/MTYPE_df_mtypebins.csv", bins_csv)

                # 2. STYPE percentile files
                for percentile, run_data in context.stype_runs.items():
                    df_stype = run_data['df_stype']
                    p_str = str(int(percentile))
                    folder = f"STYPE_{p_str}pct_PhaseFiles"
                    stype_csv = df_stype.to_csv(index=False)
                    zf.writestr(f"{folder}/STYPE_{p_str}pct_PhaseFile_Data.csv", stype_csv)

                    # Audit report text
                    audit_txt = (
                        f"M & S TYPE ANALYSIS AUDIT REPORT\n"
                        f"================================\n"
                        f"Percentile Cut: {percentile}%\n"
                        f"Original Bins: {run_data['payload']['original_bins_count']}\n"
                        f"Reduced Bins: {run_data['payload']['reduced_bins_count']}\n"
                        f"Reduction: {run_data['payload']['reduction_pct']}%\n"
                        f"Grade Preservation Deltas: {run_data['payload']['grade_preservation']}\n"
                    )
                    zf.writestr(f"{folder}/Audit_Report.txt", audit_txt)
                    logs.append(f"Bundled {folder} deliverables.")

            zip_bytes = zip_buffer.getvalue()
            context.export_zip_bytes = zip_bytes

            exec_time = (time.time() - start_t) * 1000.0
            return SkillResult(
                success=True,
                skill_name=self.name,
                execution_time_ms=round(exec_time, 2),
                logs=logs,
                data={"zip_size_bytes": len(zip_bytes)}
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
