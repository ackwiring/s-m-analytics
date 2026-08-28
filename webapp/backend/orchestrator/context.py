from typing import Any, Dict, List, Optional
import pandas as pd

class WorkflowContext:
    def __init__(self):
        self.config_name: str = "None"
        self.dataset_name: str = "No Block Model Loaded"
        self.raw_config: Dict[str, Any] = {}
        self.block_model_df: Optional[pd.DataFrame] = None
        self.mtype_phase_data: Optional[pd.DataFrame] = None
        self.mtype_cog_bins: Optional[pd.DataFrame] = None
        self.mtype_bins_index: Optional[pd.DataFrame] = None
        self.mtype_summary: Dict[str, Any] = {}
        self.stype_runs: Dict[float, Dict[str, Any]] = {}
        self.export_zip_bytes: Optional[bytes] = None
        
        # Pipeline State
        self.node_states: Dict[str, str] = {
            "ingestion_config": "IDLE",
            "mtype_baseline": "IDLE",
            "stype_reduction": "IDLE",
            "audit_verification": "IDLE",
            "export_bundle": "IDLE"
        }
        self.node_timings: Dict[str, float] = {}
        self.node_logs: Dict[str, List[str]] = {}
