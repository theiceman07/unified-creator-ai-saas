from typing import Any

import yaml


class JudgeService:
    def __init__(self):
        self.rubrics: dict[str, dict] = {}
        
    def load_rubric(self, path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            self.rubrics[data["id"]] = data
            
    async def judge(self, rubric_id: str, asset: Any, llm: Any) -> dict:
        """Evaluates an asset against a rubric."""
        if rubric_id not in self.rubrics:
            return {"pass": True, "overall": 5.0, "scores": {}, "critique": f"Rubric {rubric_id} not loaded, automatic pass."}
            
        # Simulated LLM judgment
        rubric = self.rubrics[rubric_id]
        scores = {crit: 4.0 for crit in rubric.get("universal", [])}
        scores.update({crit["key"]: 4.0 for crit in rubric.get("specific", [])})
        
        return {
            "pass": True,
            "overall": 4.0,
            "scores": scores,
            "critique": "Looks good in mock judge."
        }
        
    async def pairwise(self, rubric_id: str, items: list[Any], llm: Any) -> list[Any]:
        """Runs a tournament best-of-N."""
        # Just return top 3 for mock
        return items[:3]
