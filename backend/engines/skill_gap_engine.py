from __future__ import annotations
from typing import Dict, List, Any
from models.schemas import Skill, SkillGap, Priority
from engines.skill_engine import SkillEngine


class SkillGapEngine:
    """Deterministic calculation of skill gaps between candidate and target role requirements."""

    def __init__(self, skill_engine: SkillEngine = None):
        self.skill_engine = skill_engine or SkillEngine()

    def analyze(
        self,
        candidate_skills: List[Dict[str, Any]],
        required_skills: List[Dict[str, Any]],
        preferred_skills: List[Dict[str, Any]] = None,
        candidate_experience_years: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Calculates exact numerical gap for each required/preferred skill and prioritizes them."""
        preferred_skills = preferred_skills or []
        
        # Build map of candidate skills by normalized name, taking max proficiency for duplicates
        cand_map: Dict[str, float] = {}
        for s in candidate_skills:
            raw_name = s.get("name", "")
            norm_name = s.get("normalized_name") or self.skill_engine.normalize_skill_name(raw_name)
            norm_name = self.skill_engine.normalize_skill_name(norm_name)
            prof = float(s.get("proficiency", 0.0))
            # Take max proficiency if duplicate skill exists
            cand_map[norm_name] = max(cand_map.get(norm_name, 0.0), prof)

        gaps: List[SkillGap] = []

        # Check if candidate is experienced (>= 3 years) in domain
        is_experienced = candidate_experience_years >= 3.0

        # Analyze required skills
        for r_skill in required_skills:
            raw_name = r_skill.get("name", "")
            r_norm = r_skill.get("normalized_name") or self.skill_engine.normalize_skill_name(raw_name)
            r_norm = self.skill_engine.normalize_skill_name(r_norm)
            
            req_level = float(r_skill.get("proficiency", 0.7))
            curr_level = cand_map.get(r_norm, 0.0)
            
            if curr_level < req_level:
                gap_val = round(req_level - curr_level, 2)
                
                # Priority determination:
                # HIGH: missing core domain skill or significant gap (>= 0.35) for non-secondary tools
                # If experienced candidate missing secondary utility tool (git/sql), demote to medium
                is_secondary_utility = r_norm in ["git", "sql"] and is_experienced and len(cand_map) >= 3

                if (curr_level == 0.0 or gap_val >= 0.35) and not is_secondary_utility:
                    priority: Priority = "high"
                elif gap_val >= 0.10 or is_secondary_utility:
                    priority: Priority = "medium"
                else:
                    priority: Priority = "low"

                display_name = raw_name if raw_name else r_norm.title()

                gaps.append(
                    SkillGap(
                        skill=display_name,
                        required_level=req_level,
                        current_level=curr_level,
                        gap=gap_val,
                        priority=priority,
                        evidence=[f"Required by target role (minimum level: {req_level})"],
                    )
                )

        # Analyze preferred skills
        for p_skill in preferred_skills:
            raw_name = p_skill.get("name", "")
            p_norm = p_skill.get("normalized_name") or self.skill_engine.normalize_skill_name(raw_name)
            p_norm = self.skill_engine.normalize_skill_name(p_norm)

            req_level = float(p_skill.get("proficiency", 0.5))
            curr_level = cand_map.get(p_norm, 0.0)

            if curr_level < req_level and not any(self.skill_engine.normalize_skill_name(g.skill) == p_norm for g in gaps):
                gap_val = round(req_level - curr_level, 2)
                display_name = raw_name if raw_name else p_norm.title()
                gaps.append(
                    SkillGap(
                        skill=display_name,
                        required_level=req_level,
                        current_level=curr_level,
                        gap=gap_val,
                        priority="low",
                        evidence=[f"Preferred skill for role (target level: {req_level})"],
                    )
                )

        # Sort gaps by priority (high first, medium second, low third) and then by gap size descending
        priority_order = {"high": 0, "medium": 1, "low": 2}
        gaps.sort(key=lambda x: (priority_order[x.priority], -x.gap))

        return [g.model_dump() for g in gaps]