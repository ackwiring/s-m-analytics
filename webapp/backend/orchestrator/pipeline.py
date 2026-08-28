from typing import Any, Dict, List, Optional
from orchestrator.context import WorkflowContext
from orchestrator.registry import SkillRegistry
from skills.base import SkillResult

class PipelineOrchestrator:
    def __init__(self):
        self.registry = SkillRegistry()
        self.context = WorkflowContext()

    def run_node(self, skill_name: str, params: Optional[Dict[str, Any]] = None) -> SkillResult:
        skill = self.registry.get(skill_name)
        self.context.node_states[skill_name] = "RUNNING"
        res = skill.run(self.context, params or {})
        self.context.node_states[skill_name] = "COMPLETED" if res.success else "ERROR"
        self.context.node_timings[skill_name] = res.execution_time_ms
        self.context.node_logs[skill_name] = res.logs
        return res

    def run_pipeline(self, stype_params: Optional[Dict[str, Any]] = None) -> Dict[str, SkillResult]:
        results = {}
        # 1. M-Type Baseline
        if self.context.block_model_df is not None:
            results['mtype_baseline'] = self.run_node('mtype_baseline')
            
            # 2. S-Type Reduction
            results['stype_reduction'] = self.run_node('stype_reduction', stype_params)
            
            # 3. Audit Verification
            results['audit_verification'] = self.run_node('audit_verification')
            
            # 4. Export Bundle
            results['export_bundle'] = self.run_node('export_bundle')
            
        return results

    def get_pipeline_graph_state(self) -> List[Dict[str, Any]]:
        nodes = self.registry.list_skills()
        for n in nodes:
            n['status'] = self.context.node_states.get(n['name'], 'IDLE')
            n['timing_ms'] = self.context.node_timings.get(n['name'], 0.0)
            n['logs'] = self.context.node_logs.get(n['name'], [])
        return nodes
