from __future__ import annotations
import json
import os
import unittest

from models import CandidateProfile, TargetRole, Skill
from engines import SkillGapEngine, MatchingEngine, ReadinessEngine
from agents import (
    SkillAnalysisAgent,
    CareerResearchAgent,
    LearningAgent,
    OpportunityAgent,
    IndustryIntelligenceAgent,
    ProfileIntelligenceAgent,
)
from orchestrator import AgentOrchestrator
from config.settings import Settings


class FakeLLMService:
    def __init__(self):
        self.calls = []
        self.active_calls = 0
        self.max_active_calls = 0

    async def generate_reasoning_async(self, system_prompt: str, user_data: str, model: str) -> str:
        self.active_calls += 1
        self.max_active_calls = max(self.max_active_calls, self.active_calls)
        payload = json.loads(user_data)
        self.calls.append((system_prompt, payload, model))

        import asyncio
        await asyncio.sleep(0)

        self.active_calls -= 1
        return f"{payload['perspective']} synthesized by {model}"


class TestAICareerEngine(unittest.TestCase):

    def setUp(self):
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples",
            "sample_candidate.json",
        )
        with open(sample_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def test_schemas(self):
        cand = CandidateProfile.model_validate(self.data["candidate"])
        role = TargetRole.model_validate(self.data["target_role"])
        self.assertEqual(cand.name, "Alex Mercer")
        self.assertEqual(role.name, "ML Engineer")
        self.assertTrue(cand.career_gaps[0].protected)

    def test_skill_gap_engine(self):
        engine = SkillGapEngine()
        cand_skills = self.data["candidate"]["skills"]
        req_skills = self.data["target_role"]["required_skills"]
        gaps = engine.analyze(cand_skills, req_skills)
        
        gap_names = [g["skill"].lower() for g in gaps]
        self.assertIn("docker", gap_names)
        self.assertIn("kubernetes", gap_names)
        self.assertIn("mlops", gap_names)

    def test_matching_engine_proficiency_threshold(self):
        engine = MatchingEngine()
        cand_data = {
            "skills": [
                {"name": "Python", "proficiency": 0.85},
                {"name": "SQL", "proficiency": 0.75},
                {"name": "MLOps", "proficiency": 0.0},
                {"name": "Kubernetes", "proficiency": 0.0},
            ],
            "education": ["Bachelor"],
            "experience_years": 2.5,
            "location": "Remote",
        }
        opps = [
            {
                "title": "ML Engineer",
                "company": "TechCorp",
                "required_skills": ["Python", "SQL", "MLOps", "Kubernetes"],
                "preferred_skills": [],
                "experience_required": 2.0,
                "education_required": "Bachelor",
                "location": "Remote",
            }
        ]


        ranked = engine.rank(cand_data, opps)
        matched = ranked[0]["why_matched"]
        gaps = ranked[0]["gaps"]

        # MLOps and Kubernetes have 0.0 proficiency so they MUST NOT appear in why_matched
        self.assertIn("Python", matched)
        self.assertIn("SQL", matched)
        self.assertNotIn("MLOps", matched)
        self.assertNotIn("Kubernetes", matched)
        self.assertIn("MLOps", gaps)
        self.assertIn("Kubernetes", gaps)

    def test_matching_engine_protected_gaps_fairness(self):
        engine = MatchingEngine()
        opps = [
            {
                "title": "Senior Engineer",
                "company": "TechCorp",
                "required_skills": ["Python"],
                "preferred_skills": [],
                "experience_required": 2.0,
                "education_required": "Bachelor",
                "location": "Remote",
            }
        ]

        # Candidate A: 1.0 year raw experience + 12-month (1.0 yr) protected gap = 2.0 yrs effective
        cand_A = {
            "skills": [{"name": "Python", "proficiency": 0.85}],
            "education": ["Bachelor"],
            "experience_years": 1.0,
            "location": "Remote",
            "career_gaps": [{"reason": "Medical Leave", "duration_months": 12, "protected": True}],
        }

        # Candidate B: 2.0 years raw experience + 0 gap = 2.0 yrs effective
        cand_B = {
            "skills": [{"name": "Python", "proficiency": 0.85}],
            "education": ["Bachelor"],
            "experience_years": 2.0,
            "location": "Remote",
            "career_gaps": [],
        }

        ranked_A = engine.rank(cand_A, opps)
        ranked_B = engine.rank(cand_B, opps)

        # Both candidates must receive exact 100% experience match and identical compatibility score
        self.assertEqual(ranked_A[0]["breakdown"]["experience_match"], 100)
        self.assertEqual(ranked_B[0]["breakdown"]["experience_match"], 100)
        self.assertEqual(ranked_A[0]["compatibility_score"], ranked_B[0]["compatibility_score"])

    def test_orchestrator_pipeline(self):
        import asyncio
        orchestrator = AgentOrchestrator()
        result_state = asyncio.run(orchestrator.run_career_pipeline_async(self.data))

        self.assertIn("strengths", result_state)
        self.assertIn("skill_gaps", result_state)
        self.assertIn("learning_plan", result_state)
        self.assertIn("matched_opportunities", result_state)
        self.assertIn("readiness", result_state)
        self.assertIn("roadmap", result_state)

    def test_llm_synthesis_uses_parallel_fact_packs(self):
        import asyncio

        previous_parallelism = Settings.LLM_PARALLEL_REQUESTS
        Settings.LLM_PARALLEL_REQUESTS = 6
        fake_llm = FakeLLMService()
        input_data = json.loads(json.dumps(self.data))
        input_data["include_llm_reasoning"] = True

        try:
            orchestrator = AgentOrchestrator(llm_service=fake_llm)
            result_state = asyncio.run(orchestrator.run_career_pipeline_async(input_data))
        finally:
            Settings.LLM_PARALLEL_REQUESTS = previous_parallelism

        self.assertEqual(len(fake_llm.calls), 6)
        self.assertEqual(fake_llm.max_active_calls, 6)
        self.assertIn("llm_perspectives", result_state)

        for _prompt, payload, _model in fake_llm.calls:
            self.assertIn("fact_pack", payload)
            self.assertIn("focus_data", payload)
            self.assertIn("readiness_score", payload["fact_pack"])
            self.assertLessEqual(len(payload["fact_pack"]["top_jobs"]), 5)
            self.assertLessEqual(len(payload["fact_pack"]["recommended_courses"]), 8)


if __name__ == "__main__":
    unittest.main()
