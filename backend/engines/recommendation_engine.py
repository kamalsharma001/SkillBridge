from __future__ import annotations
from typing import Dict, List, Any
from engines.skill_engine import SkillEngine


class RecommendationEngine:
    """Deterministic engine to match courses & certifications to skill gaps and generate ordered learning sequences."""

    def __init__(self, skill_engine: SkillEngine = None):
        self.skill_engine = skill_engine or SkillEngine()

    def recommend_courses(
        self,
        skill_gaps: List[Dict[str, Any]],
        courses: List[Dict[str, Any]],
        candidate_level: str = "beginner",
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Matches available courses to prioritized skill gaps."""
        # Map gaps by normalized skill name so course taxonomies and resume
        # variants still resolve to the same learning need.
        gap_skills = {
            self.skill_engine.normalize_skill_name(g.get("skill", "")): g
            for g in (skill_gaps or [])
            if g.get("skill")
        }

        matched_courses = []
        for course in courses:
            c_skills = [
                self.skill_engine.normalize_skill_name(str(s))
                for s in course.get("skills", [])
                if s
            ]
            # Check overlap with gaps
            overlap = [s for s in c_skills if s in gap_skills]

            if overlap:
                target_gap = gap_skills[overlap[0]]
                priority = target_gap.get("priority", "medium")
                primary_skill = target_gap.get("skill", overlap[0].title())
            else:
                continue

            priority_boost = 1.5 if priority == "high" else (1.2 if priority == "medium" else 1.0)

            score = round(course.get("rating", 4.5) * priority_boost, 2)
            relevance_score = min(88, int(round(58 + len(overlap) * 10 + score * 3)))
            matched_courses.append({
                "title": course.get("title", ""),
                "platform": course.get("platform", "Online"),
                "primary_skill": primary_skill,
                "priority": priority,
                "duration_hours": course.get("duration_hours", 10),
                "url": course.get("url", ""),
                "score": score,
                "match_confidence": relevance_score,
                "relevance_reason": f"Covers {primary_skill}, which is a {priority}-priority gap for the target role.",
            })

        # Sort courses by priority (high > medium > low) and then by score descending
        prio_map = {"high": 0, "medium": 1, "low": 2}
        matched_courses.sort(key=lambda x: (prio_map[x["priority"]], -x["score"]))

        return matched_courses[:top_k]
