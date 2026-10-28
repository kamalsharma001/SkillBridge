from __future__ import annotations
from typing import Any, Dict
from agents.base_agent import BaseAgent
from engines.readiness_engine import ReadinessEngine
from engines.roadmap_engine import RoadmapEngine
from models.schemas import AgentResult, CandidateProfile, TargetRole


from models.contexts import ProfileAgentContext

class ProfileIntelligenceAgent(BaseAgent):
    """Profile Intelligence Agent: Tracks user progress, evaluates project additions, and monitors continuous career readiness."""

    def __init__(
        self,
        readiness_engine: ReadinessEngine = None,
        roadmap_engine: RoadmapEngine = None,
        llm_service=None,
    ):
        super().__init__(name="profile_intelligence", llm_service=llm_service)
        self.readiness_engine = readiness_engine or ReadinessEngine()
        self.roadmap_engine = roadmap_engine or RoadmapEngine()

    def run(self, context: ProfileAgentContext) -> AgentResult:
        cand_dict = context.candidate
        target_dict = context.target_role

        candidate = CandidateProfile.model_validate(cand_dict) if isinstance(cand_dict, dict) else cand_dict
        target_role = TargetRole.model_validate(target_dict) if isinstance(target_dict, dict) else target_dict

        # Calculate readiness score deterministically
        readiness_data = self.readiness_engine.calculate(
            candidate=candidate.model_dump(),
            target_role=target_role.model_dump(),
        )

        # Generate sequenced roadmap
        skill_gaps = context.skill_gaps
        recommended_courses = context.recommended_courses
        
        roadmap = self.roadmap_engine.generate(
            skill_gaps=skill_gaps,
            courses=recommended_courses,
            projects=[p.model_dump() for p in candidate.projects],
            target_role=target_role.name,
        )

        data_payload = {
            "readiness": readiness_data,
            "roadmap": roadmap,
            "project_count": len(candidate.projects),
            "completed_courses_count": len(candidate.courses_completed),
        }

        # Build evidence with source, record reference, and derived claim
        evidence = []
        
        # Evidence for readiness calculation
        evidence.append({
            "source": "Readiness Engine",
            "dataset_record_id": f"readiness.{candidate.candidate_id}.{target_role.name.lower().replace(' ', '_')}",
            "claim": f"Calculated readiness score: {readiness_data['readiness_score']}% (Skill: {readiness_data['skill_readiness']}%, Project: {readiness_data['project_readiness']}%, Experience: {readiness_data['experience_readiness']}%) - Status: {readiness_data['status']}"
        })
        
        # Evidence for roadmap generation
        evidence.append({
            "source": "Roadmap Engine",
            "dataset_record_id": f"roadmap.{candidate.candidate_id}.steps_{len(roadmap)}",
            "claim": f"Generated {len(roadmap)}-step roadmap from {len(skill_gaps)} skill gaps and {len(recommended_courses)} recommended courses"
        })
        
        # Evidence for profile completeness
        evidence.append({
            "source": "Profile Analysis",
            "dataset_record_id": f"profile.{candidate.candidate_id}",
            "claim": f"Profile contains {len(candidate.skills)} skills, {len(candidate.projects)} projects, {len(candidate.courses_completed)} completed courses, {len(candidate.certifications)} certifications"
        })

        # LLM Synthesis setup (executed later by orchestrator)
        system_prompt = (
            "You are the Chief AI Career Strategist. Read the final readiness score and the "
            "generated roadmap. Write a cohesive, empowering executive summary for the user, "
            "celebrating their current strengths and providing an inspiring closing thought on their journey."
            "do not return any flowcharts or use bold letters."
        )

        return AgentResult(
            agent=self.name,
            status="success",
            summary=f"Profile intelligence updated: overall career readiness is {readiness_data['readiness_score']}%.",
            system_prompt=system_prompt,
            data=data_payload,
            evidence=evidence,
        )
