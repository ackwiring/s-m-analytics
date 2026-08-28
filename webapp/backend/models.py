from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class FlexOrderRule(BaseModel):
    fieldname: str
    flex_order: int
    flex_option: str = "STATIC"

class STypeParameters(BaseModel):
    sets: Optional[int] = 5
    percentiles: List[float] = [20.0, 40.0, 60.0, 80.0]
    aggregation_field: str = "d1_Ranking"
    aggregation_type: str = "GRADE"
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

class PipelineNodeInfo(BaseModel):
    name: str
    display_name: str
    version: str
    description: str
    category: str
    status: str
    timing_ms: float
    logs: List[str] = []

class FullAnalysisResponse(BaseModel):
    status: str
    message: str
    app_name: str = "M & S Type Analyzer"
    app_version: str = "v2.0.0"
    dataset_name: str
    config_name: str
    mtype_baseline: Optional[MTypeResult] = None
    stype_results: List[STypePercentileResult] = []
    available_dimensions: List[str] = []
    available_weighted_fields: List[Dict[str, str]] = []
    available_sum_fields: List[str] = []
    current_stype_params: Optional[STypeParameters] = None
    pipeline_nodes: List[PipelineNodeInfo] = []
