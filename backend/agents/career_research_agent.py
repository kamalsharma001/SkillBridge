from __future__ import annotations
from typing import Any, Dict, List, Optional
from agents.base_agent import BaseAgent
from engines.market_engine import MarketEngine
from models.schemas import AgentResult
from models.contexts import CareerAgentContext

class CareerResearchAgent(BaseAgent):
    """Career Research Agent: Researches career paths, market demand, and alternative roles using job market data & evidence."""

    ROLE_TRANSITIONS = {
        "Data Analyst": ["Data Scientist", "Analytics Engineer", "Business Intelligence Engineer", "Data Engineer"],
        "Software Engineer": ["ML Engineer", "Backend Engineer", "Full Stack Engineer", "Platform Engineer"],
        "ML Engineer": ["Senior ML Engineer", "MLOps Engineer", "AI Research Engineer", "Data Scientist"],
        "Data Scientist": ["Senior Data Scientist", "ML Engineer", "Applied Scientist", "Analytics Lead"],
        "Data Engineer": ["Senior Data Engineer", "Platform Engineer", "MLOps Engineer", "Analytics Engineer"],
        "Business Intelligence Engineer": ["Analytics Engineer", "Data Analyst", "Data Scientist", "Analytics Lead"],
        "Analytics Engineer": ["Data Engineer", "Data Scientist", "Analytics Lead", "ML Engineer"],
        "Frontend Developer": ["Full Stack Engineer", "UI Engineer", "Frontend Architect", "Software Engineer"],
        "Backend Developer": ["Platform Engineer", "Software Engineer", "DevOps Engineer", "Full Stack Engineer"],
        "DevOps Engineer": ["Platform Engineer", "Site Reliability Engineer", "Cloud Engineer", "MLOps Engineer"],
        "Product Manager": ["Senior Product Manager", "Group Product Manager", "Product Lead", "Head of Product"],
    }

    ROLE_SKILL_OVERLAP = {
        "ML Engineer": ["python", "machine_learning", "tensorflow", "pytorch", "mlops", "docker", "kubernetes"],
        "Data Engineer": ["python", "sql", "spark", "airflow", "kafka", "aws", "docker"],
        "Data Scientist": ["python", "sql", "machine_learning", "pandas", "statistics", "scikit_learn"],
        "Analytics Engineer": ["sql", "python", "dbt", "airflow", "looker", "tableau"],
        "Business Intelligence Engineer": ["sql", "tableau", "power_bi", "looker", "excel"],
        "Software Engineer": ["python", "java", "javascript", "git", "docker", "aws"],
        "MLOps Engineer": ["python", "docker", "kubernetes", "mlops", "aws", "ci_cd"],
        "AI Research Engineer": ["python", "machine_learning", "deep_learning", "pytorch", "tensorflow", "research"],
    }

    def __init__(self, market_engine: MarketEngine = None, retriever=None, data_service=None, llm_service=None):
        super().__init__(name="career_research", llm_service=llm_service)
        self.market_engine = market_engine or MarketEngine()
        self.retriever = retriever
        self.data_service = data_service

    def _calculate_role_fit(self, candidate_skills: List[Dict[str, Any]], target_role: str) -> float:
        """Calculate fit score based on skill overlap with target role requirements."""
        target_skills = set(self.ROLE_SKILL_OVERLAP.get(target_role, []))
        if not target_skills:
            return 0.5
        
        cand_skill_names = set()
        for s in candidate_skills:
            norm_name = s.get("normalized_name", "").lower().replace(" ", "_").replace(".", "").replace("#", "sharp")
            cand_skill_names.add(norm_name)
        
        overlap = len(cand_skill_names.intersection(target_skills))
        return min(0.95, 0.4 + (overlap / max(len(target_skills), 1)) * 0.55)

    def _get_alternatives(self, current_role: str, target_role: str, candidate_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate alternative career paths based on skill overlap."""
        possible_transitions = self.ROLE_TRANSITIONS.get(current_role, [])
        if target_role in possible_transitions:
            possible_transitions.remove(target_role)
        
        alternatives = []
        for role in possible_transitions[:4]:
            fit = self._calculate_role_fit(candidate_skills, role)
            if fit > 0.45:
                alternatives.append({"role": role, "fit_score": round(fit, 2)})
        
        alternatives.sort(key=lambda x: x["fit_score"], reverse=True)
        return alternatives[:3]

    def run(self, context: CareerAgentContext) -> AgentResult:
        cand_dict = context.candidate
        current_role = cand_dict.get("current_role", "Data Analyst")
        target_role = context.target_role.get("name", "Data Scientist")
        jobs = context.jobs

        # Fetch jobs from data service if none provided
        if not jobs and self.data_service:
            jobs = self.data_service.get_jobs(limit=50)

        # Analyze market demand deterministically
        market_stats = self.market_engine.analyze_skill_demand(jobs)

        # Dynamic career paths based on candidate skills and role transitions
        candidate_skills = cand_dict.get("skills", [])
        
        # Primary target role
        target_fit = self._calculate_role_fit(candidate_skills, target_role)
        
        career_paths = [
            {"role": target_role, "fit_score": round(target_fit, 2), "transition_ease": "High" if target_fit > 0.7 else "Medium"}
        ]

        # Add alternatives based on transitions from current role
        alternatives = self._get_alternatives(current_role, target_role, candidate_skills)
        
        # Also add roles with high skill overlap that aren't in direct transitions
        all_known_roles = list(self.ROLE_SKILL_OVERLAP.keys())
        for role in all_known_roles:
            if role != target_role and role not in [a["role"] for a in alternatives] and role not in [c["role"] for c in career_paths]:
                fit = self._calculate_role_fit(candidate_skills, role)
                if fit > 0.6:
                    career_paths.append({"role": role, "fit_score": round(fit, 2), "transition_ease": "Medium"})

        career_paths.sort(key=lambda x: x["fit_score"], reverse=True)
        career_paths = career_paths[:4]

        # Build evidence with source, record reference, and derived claim
        evidence = []
        
        # Evidence for career path calculation
        evidence.append({
            "source": "Career Transition Knowledge Graph",
            "dataset_record_id": f"transitions.{current_role.lower().replace(' ', '_')}",
            "claim": f"Identified {len(self.ROLE_TRANSITIONS.get(current_role, []))} known transition paths from {current_role}"
        })
        
        # Evidence for fit scores
        evidence.append({
            "source": "Role Skill Overlap Analysis",
            "dataset_record_id": f"skill_overlap.{target_role.lower().replace(' ', '_')}",
            "claim": f"Calculated fit scores using {len(self.ROLE_SKILL_OVERLAP.get(target_role, []))} core {target_role} skills against candidate profile"
        })
        
        # Evidence for market demand if jobs available
        if jobs:
            evidence.append({
                "source": "Job Market Analysis",
                "dataset_record_id": f"jobs.analyzed_{len(jobs)}",
                "claim": f"Analyzed demand for {len(market_stats)} skills across {len(jobs)} job postings"
            })

        data_payload = {
            "current_role": current_role,
            "target_role": target_role,
            "career_paths": career_paths,
            "market_demand": market_stats,
            "alternatives": alternatives,
        }

        # LLM Synthesis setup (executed later by orchestrator)
        system_prompt = (
            "You are a strategic Career Coach. Review the calculated career transition paths "
            "and market demand data. Explain WHY these paths are a good fit for the candidate "
            "and provide an encouraging but realistic outlook on their transition."
            "do not return any flowcharts or use bold letters."
        )

        return AgentResult(
            agent=self.name,
            status="success",
            summary=f"Career research completed for transition from '{current_role}' to '{target_role}'. Identified {len(career_paths)} career paths and {len(alternatives)} alternatives.",
            system_prompt=system_prompt,
            data=data_payload,
            evidence=evidence,
        )