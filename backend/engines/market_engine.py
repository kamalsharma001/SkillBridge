from __future__ import annotations
from typing import Dict, List, Any


class MarketEngine:
    """Deterministic engine for job market statistics, skill demand, and trend calculation."""

    def analyze_skill_demand(self, jobs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Calculates percentage demand for skills across a collection of job postings."""
        if not jobs:
            return {}

        total_jobs = len(jobs)
        skill_counts: Dict[str, int] = {}
        for j in jobs:
            # Deduplicate skills per job to avoid double counting
            job_skills = set()
            for s in j.get("required_skills", []) + j.get("preferred_skills", []):
                s_clean = s.strip().lower()
                job_skills.add(s_clean)
            for s_clean in job_skills:
                skill_counts[s_clean] = skill_counts.get(s_clean, 0) + 1

        results = {}
        for s_name, count in skill_counts.items():
            pct = int((count / total_jobs) * 100)
            results[s_name] = {
                "demand_pct": pct,
                "trend": "GROWING" if pct > 30 else "STABLE",
            }
        return results

    def calculate_trends(
        self,
        current_jobs: List[Dict[str, Any]],
        previous_jobs: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Calculates demand changes between past and current job postings."""
        curr_demand = self.analyze_skill_demand(current_jobs)
        
        if not previous_jobs:
            # No historical data - return current demand with neutral trend
            trends = []
            for s_name, data in curr_demand.items():
                trends.append({
                    "skill": s_name.title() if s_name not in ["sql", "mlops", "aws"] else s_name.upper(),
                    "current_demand": f"{data['demand_pct']}%",
                    "trend": "UNKNOWN",
                    "change_pct": 0,
                })
            return trends

        prev_demand = self.analyze_skill_demand(previous_jobs)
        
        trends = []
        all_skills = set(curr_demand.keys()) | set(prev_demand.keys())
        for s_name in all_skills:
            curr_pct = curr_demand.get(s_name, {}).get("demand_pct", 0)
            prev_pct = prev_demand.get(s_name, {}).get("demand_pct", 0)
            
            change_pct = curr_pct - prev_pct
            
            if change_pct > 10:
                trend = "GROWING"
            elif change_pct < -10:
                trend = "DECLINING"
            else:
                trend = "STABLE"
            
            trends.append({
                "skill": s_name.title() if s_name not in ["sql", "mlops", "aws"] else s_name.upper(),
                "current_demand": f"{curr_pct}%",
                "previous_demand": f"{prev_pct}%",
                "change_pct": change_pct,
                "trend": trend,
            })
        
        # Sort by absolute change descending
        trends.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        return trends

    def emerging_skills(self, trends: List[Dict[str, Any]]) -> List[str]:
        """Identifies skills with strong upward growth trends."""
        emerging = []
        for t in trends:
            if t.get("trend") in ["GROWING", "HIGH GROWTH", "↑", "↑↑"]:
                emerging.append(t["skill"])
        return emerging