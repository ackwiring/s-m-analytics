import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class SkillResult(BaseModel):
    success: bool
    skill_name: str
    execution_time_ms: float
    data: Dict[str, Any] = {}
    logs: List[str] = []
    error: Optional[str] = None

class BaseSkill(ABC):
    name: str = "base_skill"
    display_name: str = "Base Skill"
    version: str = "1.0.0"
    description: str = ""
    category: str = "General"

    @abstractmethod
    def run(self, context: Any, params: Dict[str, Any]) -> SkillResult:
        """Executes the discrete skill logic."""
        pass
