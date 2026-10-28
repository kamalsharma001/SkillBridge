from __future__ import annotations
from typing import Dict, List, Any


class RoadmapEngine:
    """Deterministic engine to construct sequenced learning & project roadmaps."""

    def generate(
        self,
        skill_gaps: List[Dict[str, Any]],
        courses: List[Dict[str, Any]] = None,
        projects: List[Dict[str, Any]] = None,
        target_role: str = "Target Role",
    ) -> List[Dict[str, Any]]:
        """Generates sequenced roadmap steps based on prioritized skill gaps."""
        courses = courses or []
        projects = projects or []
        roadmap = []

        step_counter = 1
        for gap in skill_gaps:
            skill_name = gap.get("skill", "Required Skill")
            prio = gap.get("priority", "medium")

            # Find matching course
            matching_course = next(
                (c for c in courses if c.get("primary_skill", "").lower() == skill_name.lower()),
                None
            )
            course_title = matching_course.get("title") if matching_course else f"{skill_name} Fundamentals & Best Practices"

            roadmap.append({
                "step": step_counter,
                "title": f"Master {skill_name}",
                "skill": skill_name,
                "priority": prio,
                "action": f"Complete '{course_title}'",
                "milestone": f"Build hands-on project utilizing {skill_name}",
                "target_role": target_role,
            })
            step_counter += 1

        if not roadmap:
            roadmap.append({
                "step": 1,
                "title": "Role Consolidation",
                "skill": "Advanced Skills",
                "priority": "low",
                "action": "Build portfolio project showcasing target role competencies",
                "milestone": "Submit applications for target role",
                "target_role": target_role,
            })

        return roadmap
