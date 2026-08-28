from typing import Dict, Type
from skills.base import BaseSkill
from skills.ingestion.skill import IngestionSkill
from skills.mtype_baseline.skill import MTypeBaselineSkill
from skills.stype_reduction.skill import STypeReductionSkill
from skills.audit_verification.skill import AuditVerificationSkill
from skills.export_bundle.skill import ExportBundleSkill

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self.register(IngestionSkill())
        self.register(MTypeBaselineSkill())
        self.register(STypeReductionSkill())
        self.register(AuditVerificationSkill())
        self.register(ExportBundleSkill())

    def register(self, skill: BaseSkill):
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill:
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' not found in registry.")
        return self._skills[name]

    def list_skills(self):
        return [
            {
                "name": s.name,
                "display_name": s.display_name,
                "version": s.version,
                "description": s.description,
                "category": s.category
            }
            for s in self._skills.values()
        ]
