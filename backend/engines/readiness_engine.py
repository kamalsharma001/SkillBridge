from __future__ import annotations
from typing import Dict, List, Any
from engines.matching_engine import calculate_effective_experience
from engines.skill_engine import SkillEngine


class ReadinessEngine:
    """Deterministic engine to evaluate candidate career readiness score (0-100%)."""

    def __init__(self, skill_engine: SkillEngine = None):
        self.skill_engine = skill_engine or SkillEngine()

    def calculate(
        self,
        candidate: Dict[str, Any],
        target_role: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculates readiness score based on skill overlap, project coverage, and effective experience."""
        cand_skills = {}
        for s in candidate.get("skills", []):
            raw_name = s.get("name", "")
            norm = s.get("normalized_name") or self.skill_engine.normalize_skill_name(raw_name)
            norm = self.skill_engine.normalize_skill_name(norm)
            cand_skills[norm] = float(s.get("proficiency", 0.0))

        req_skills = target_role.get("required_skills", [])
        missing_required = 0
        if not req_skills:
            skill_score = 0.45
        else:
            total_req = len(req_skills)
            met_sum = 0.0
            for r in req_skills:
                raw_name = r.get("name", "")
                r_norm = r.get("normalized_name") or self.skill_engine.normalize_skill_name(raw_name)
                r_norm = self.skill_engine.normalize_skill_name(r_norm)

                req_level = float(r.get("proficiency", 0.7))
                curr_level = cand_skills.get(r_norm, 0.0)

                if curr_level == 0.0:
                    missing_required += 1

                if curr_level >= req_level:
                    met_sum += 1.0
                else:
                    met_sum += (curr_level / req_level) if req_level > 0 else 0.0
            skill_score = met_sum / total_req

        # Project score (0-1)
        num_projects = len(candidate.get("projects", []))
        project_score = min(1.0, num_projects * 0.40)

        # Experience score using effective experience (restoring protected career gaps)
        cand_exp = calculate_effective_experience(
            candidate.get("experience_years", 0.0),
            candidate.get("career_gaps", []),
        )
        target_exp = target_role.get("experience_min", 1.0)
        exp_score = 1.0 if cand_exp >= target_exp else (cand_exp / target_exp if target_exp > 0 else 1.0)

        # Weighted calculation (Skill 60%, Project 25%, Experience 15%)
        raw_readiness = (skill_score * 0.60 + project_score * 0.25 + exp_score * 0.15) * 100

        # Missing target-role skills should leave room for course recommendations
        # without collapsing an otherwise promising engineering profile.
        if missing_required:
            gap_cap = 82.0 if missing_required == 1 else 76.0
            raw_readiness = min(raw_readiness, gap_cap)

        overall_readiness = int(round(raw_readiness))

        # Allow scores up to 100 for truly exceptional candidates
        # The cap was removed to reflect actual readiness accurately
        # overall_readiness = min(overall_readiness, 89)  # REMOVED

        # Readiness Category mapping:
        # >= 75%: Job Ready
        # >= 45%: Developing
        # < 45%: Early Preparation
        if overall_readiness >= 75:
            status = "Job Ready"
        elif overall_readiness >= 45:
            status = "Developing"
        else:
            status = "Early Preparation"

        return {
            "readiness_score": overall_readiness,
            "status": status,
            "skill_readiness": int(skill_score * 100),
            "project_readiness": int(project_score * 100),
            "experience_readiness": int(exp_score * 100),
        }