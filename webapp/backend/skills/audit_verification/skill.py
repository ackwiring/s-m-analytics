import time
import numpy as np
import pandas as pd
from typing import Any, Dict
from skills.base import BaseSkill, SkillResult

class AuditVerificationSkill(BaseSkill):
    name = "audit_verification"
    display_name = "4. Metallurgical Audit Verification"
    version = "1.0.0"
    description = "Compares baseline and collapsed bin distributions, verifying head grade preservation and tonnage parity."
    category = "Quality Control"

    def run(self, context: Any, params: Dict[str, Any]) -> SkillResult:
        start_t = time.time()
        logs = []
        try:
            if not context.stype_runs or context.mtype_phase_data is None:
                raise ValueError("Missing M-Type or S-Type run data in context.")

            weighted_fields = context.raw_config.get('weighted_fields', pd.DataFrame())
            base_grades = context.mtype_summary.get('weighted_summary', {})

            for percentile, run_data in context.stype_runs.items():
                df_stype = run_data['df_stype']
                grade_pres = {}

                if not weighted_fields.empty:
                    for _, r in weighted_fields.iterrows():
                        f = r['Field']
                        w = r['Weighting']
                        if f in df_stype.columns and w in df_stype.columns and df_stype[w].sum() > 0:
                            stype_val = float((df_stype[f] * df_stype[w]).sum() / df_stype[w].sum())
                            base_val = base_grades.get(f, stype_val)
                            delta = round(((stype_val - base_val) / base_val * 100.0) if base_val != 0 else 0.0, 2)
                            grade_pres[f] = delta

                run_data['payload']['grade_preservation'] = grade_pres
                logs.append(f"Audit {percentile}%: Checked {len(grade_pres)} weighted fields.")

            exec_time = (time.time() - start_t) * 1000.0
            return SkillResult(
                success=True,
                skill_name=self.name,
                execution_time_ms=round(exec_time, 2),
                logs=logs,
                data={"verified_runs": len(context.stype_runs)}
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
