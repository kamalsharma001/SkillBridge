from typing import Any, Dict, List
from models.schemas import AgentResult


class CareerFactPackBuilder:
    """Builds the compact, verified payload sent to each LLM perspective."""

    @classmethod
    def build_fact_pack(
        cls,
        context: Dict[str, Any],
        agent_results: Dict[str, AgentResult],
    ) -> Dict[str, Any]:
        """Create the compact, verified payload sent to each LLM perspective."""
        candidate = context.get("candidate", {})
        target_role = context.get("target_role", {})
        
        profile_res = agent_results.get("profile_intelligence")
        profile_data = profile_res.data if profile_res else {}
        
        learning_res = agent_results.get("learning")
        learning_data = learning_res.data if learning_res else {}
        
        opportunity_res = agent_results.get("opportunity")
        opportunity_data = opportunity_res.data if opportunity_res else {}
        
        industry_res = agent_results.get("industry_intelligence")
        industry_data = industry_res.data if industry_res else {}

        readiness = profile_data.get("readiness", {})
        courses = learning_data.get("recommended_courses", []) or learning_data.get("learning_plan", [])
        jobs = opportunity_data.get("matched_opportunities", [])

        return {
            "candidate": {
                "candidate_id": candidate.get("candidate_id", "unknown"),
                "current_role": candidate.get("current_role", ""),
                "experience_years": candidate.get("experience_years", 0),
                "education": cls._limit_list(candidate.get("education", []), 3),
                "location": candidate.get("location", ""),
            },
            "target_role": {
                "name": target_role.get("name", "Target Role"),
                "required_skills": cls._skill_names(target_role.get("required_skills", []), 10),
            },
            "readiness_score": readiness.get("readiness_score"),
            "readiness_status": readiness.get("status"),
            "strengths": cls._compact_skills(context.get("strengths", []), 10),
            "skill_gaps": cls._compact_gaps(context.get("skill_gaps", []), 10),
            "top_jobs": cls._compact_jobs(jobs, 5),
            "recommended_courses": cls._compact_courses(courses, 8),
            "emerging_skills": cls._limit_list(industry_data.get("emerging_skills", []), 10),
            "skill_trends": cls._limit_list(industry_data.get("skill_trends", []), 10),
            "roadmap": cls._limit_list(profile_data.get("roadmap", []), 8),
            "agent_summaries": {
                name: result.summary
                for name, result in agent_results.items()
            },
        }

    @classmethod
    def compact_agent_data(cls, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if name == "opportunity":
            return {"matched_opportunities": cls._compact_jobs(data.get("matched_opportunities", []), 5)}
        if name == "learning":
            courses = data.get("recommended_courses", []) or data.get("learning_plan", [])
            return {
                "learning_plan": cls._limit_list(data.get("learning_plan", []), 8),
                "recommended_courses": cls._compact_courses(courses, 8),
                "certifications": cls._limit_list(data.get("certifications", []), 5),
            }
        if name == "skill_analysis":
            return {
                "strengths": cls._compact_skills(data.get("strengths", []), 10),
                "skill_gaps": cls._compact_gaps(data.get("skill_gaps", []), 10),
            }
        return cls._limit_mapping(data, 10)

    @staticmethod
    def _limit_list(items: Any, limit: int) -> List[Any]:
        if not isinstance(items, list):
            return []
        return items[:limit]

    @staticmethod
    def _limit_mapping(data: Dict[str, Any], limit: int) -> Dict[str, Any]:
        compact: Dict[str, Any] = {}
        for idx, (key, value) in enumerate(data.items()):
            if idx >= limit:
                break
            compact[key] = value[:limit] if isinstance(value, list) else value
        return compact

    @staticmethod
    def _skill_names(skills: Any, limit: int) -> List[str]:
        names = []
        for skill in skills if isinstance(skills, list) else []:
            if isinstance(skill, dict):
                name = skill.get("name") or skill.get("normalized_name")
            else:
                name = getattr(skill, "name", str(skill))
            if name:
                names.append(str(name))
            if len(names) >= limit:
                break
        return names

    @classmethod
    def _compact_skills(cls, skills: Any, limit: int) -> List[Dict[str, Any]]:
        compact = []
        for skill in skills if isinstance(skills, list) else []:
            if not isinstance(skill, dict):
                continue
            compact.append({
                "name": skill.get("name") or skill.get("normalized_name"),
                "proficiency": skill.get("proficiency"),
                "evidence": cls._limit_list(skill.get("evidence", []), 2),
            })
            if len(compact) >= limit:
                break
        return compact

    @staticmethod
    def _compact_gaps(gaps: Any, limit: int) -> List[Dict[str, Any]]:
        compact = []
        for gap in gaps if isinstance(gaps, list) else []:
            if not isinstance(gap, dict):
                continue
            compact.append({
                "skill": gap.get("skill"),
                "priority": gap.get("priority"),
                "current_level": gap.get("current_level"),
                "required_level": gap.get("required_level"),
                "gap": gap.get("gap"),
            })
            if len(compact) >= limit:
                break
        return compact

    @staticmethod
    def _compact_jobs(jobs: Any, limit: int) -> List[Dict[str, Any]]:
        compact = []
        for job in jobs if isinstance(jobs, list) else []:
            if not isinstance(job, dict):
                continue
            compact.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "compatibility_score": job.get("compatibility_score"),
                "breakdown": job.get("breakdown", {}),
                "why_matched": job.get("why_matched", [])[:4],
                "gaps": job.get("gaps", [])[:4],
            })
            if len(compact) >= limit:
                break
        return compact

    @staticmethod
    def _compact_courses(courses: Any, limit: int) -> List[Dict[str, Any]]:
        compact = []
        for course in courses if isinstance(courses, list) else []:
            if not isinstance(course, dict):
                continue
            compact.append({
                "title": course.get("title") or course.get("course_title"),
                "platform": course.get("platform"),
                "primary_skill": course.get("primary_skill") or course.get("skill"),
                "priority": course.get("priority"),
                "duration_hours": course.get("duration_hours"),
                "match_confidence": course.get("match_confidence"),
                "relevance_reason": course.get("relevance_reason"),
            })
            if len(compact) >= limit:
                break
        return compact
