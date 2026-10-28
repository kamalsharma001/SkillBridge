from __future__ import annotations
from typing import Any, Dict, List, Optional
from agents.base_agent import BaseAgent
from engines.skill_engine import SkillEngine
from engines.skill_gap_engine import SkillGapEngine
from models.schemas import AgentResult, CandidateProfile, TargetRole

from models.contexts import SkillAgentContext

class SkillAnalysisAgent(BaseAgent):
    """Skill Analysis Agent: Compares candidate skills with target role requirements, identifies missing skills, and prioritizes gaps."""

    def __init__(
        self,
        skill_engine: SkillEngine = None,
        gap_engine: SkillGapEngine = None,
        data_service=None,
        llm_service=None,
    ):
        super().__init__(name="skill_analysis", llm_service=llm_service)
        self.skill_engine = skill_engine or SkillEngine()
        self.gap_engine = gap_engine or SkillGapEngine()
        self.data_service = data_service

    def run(self, context: SkillAgentContext) -> AgentResult:
        cand_dict = context.candidate
        target_dict = context.target_role

        # In HANA mode: if candidate_id is provided but no full candidate data,
        # fetch from SAP HANA via DataService
        if self.data_service and self.data_service.is_hana:
            if not cand_dict.get("skills") and cand_dict.get("candidate_id"):
                hana_candidate = self.data_service.get_candidate(cand_dict["candidate_id"])
                if hana_candidate:
                    cand_dict = {**cand_dict, **hana_candidate}
                    context.candidate = cand_dict

        candidate = CandidateProfile.model_validate(cand_dict) if isinstance(cand_dict, dict) else cand_dict
        target_role = TargetRole.model_validate(target_dict) if isinstance(target_dict, dict) else target_dict

        # 1. Process candidate skills with recency & evidence weighting
        processed_cand_skills = self.skill_engine.process_candidate_skills(
            [s.model_dump() for s in candidate.skills]
        )

        # 2. Process required/preferred skills
        required_skills = [s.model_dump() for s in target_role.required_skills]
        preferred_skills = [s.model_dump() for s in target_role.preferred_skills]

        # 3. Calculate skill gaps deterministically via SkillGapEngine
        gaps = self.gap_engine.analyze(
            candidate_skills=[s.model_dump() for s in processed_cand_skills],
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            candidate_experience_years=candidate.experience_years,
        )

        # Categorize strengths (>= 70%) and moderate skills (40-69%)
        strengths = [s.model_dump() for s in processed_cand_skills if s.proficiency >= 0.70]
        moderate = [s.model_dump() for s in processed_cand_skills if 0.40 <= s.proficiency < 0.70]

        data_payload = {
            "target_role": target_role.name,
            "strengths": strengths,
            "moderate_skills": moderate,
            "skill_gaps": gaps,
        }

        # Build evidence with source, record reference, and derived claim
        evidence = []
        
        # Evidence for target role requirements source
        if self.data_service and self.data_service.is_hana:
            evidence.append({
                "source": "O*NET Database (SAP HANA)",
                "dataset_record_id": f"ONET occupation skills for {target_role.name}",
                "claim": f"Retrieved {len(required_skills)} required and {len(preferred_skills)} preferred skills from O*NET for {target_role.name}"
            })
        elif required_skills:
            evidence.append({
                "source": "O*NET / ESCO Framework (local)",
                "dataset_record_id": f"target_role.{target_role.name}",
                "claim": f"Using {len(required_skills)} required and {len(preferred_skills)} preferred skills defined for {target_role.name}"
            })
        else:
            evidence.append({
                "source": "O*NET / ESCO Framework",
                "dataset_record_id": "generic_role_mapping",
                "claim": f"Mapped generic requirements for {target_role.name}"
            })

        # Evidence for candidate skill assessment
        evidence.append({
            "source": "Candidate Profile Analysis",
            "dataset_record_id": f"candidate.{candidate.candidate_id}",
            "claim": f"Assessed {len(strengths)} strengths (>=70% proficiency) and {len(moderate)} moderate skills (40-69%) from candidate's {len(processed_cand_skills)} declared skills"
        })

        # Evidence for each high-priority gap
        high_priority_gaps = [g for g in gaps if g.get("priority") == "high"]
        for gap in high_priority_gaps[:3]:  # Limit to top 3
            evidence.append({
                "source": "Skill Gap Engine",
                "dataset_record_id": f"gap.{gap.get('skill', 'unknown').lower().replace(' ', '_')}",
                "claim": f"Gap detected: {gap.get('skill')} (current: {gap.get('current_level', 0):.0%}, required: {gap.get('required_level', 0):.0%}, gap: {gap.get('gap', 0):.0%})"
            })

        # LLM Synthesis setup (executed later by orchestrator)
        system_prompt = (
            "You are an expert Technical Skill Assessor. Analyze the calculated skill gaps "
            "and output an encouraging, precise summary of where the candidate needs to focus. "
            "Explain exactly why these gaps matter for the target role."
            "do not return any flowcharts or use bold letters."
        )

        return AgentResult(
            agent=self.name,
            status="success",
            summary=f"Skill analysis completed for target role: {target_role.name}. Identified {len(strengths)} strengths and {len(gaps)} skill gaps.",
            system_prompt=system_prompt,
            data=data_payload,
            evidence=evidence,
        )