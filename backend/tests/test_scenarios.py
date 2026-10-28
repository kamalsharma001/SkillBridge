from __future__ import annotations
import json
import os
import unittest

from engines import ReadinessEngine, MatchingEngine
from orchestrator import AgentOrchestrator


class TestEvaluationScenarios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data"
        )
        with open(os.path.join(cls.data_dir, "candidates.json"), "r", encoding="utf-8") as f:
            cls.candidates = {c["candidate_id"]: c for c in json.load(f)}
        with open(os.path.join(cls.data_dir, "target_roles.json"), "r", encoding="utf-8") as f:
            cls.target_roles = {r["role_id"]: r for r in json.load(f)}
        with open(os.path.join(cls.data_dir, "courses.json"), "r", encoding="utf-8") as f:
            cls.courses = json.load(f)
        with open(os.path.join(cls.data_dir, "opportunities.json"), "r", encoding="utf-8") as f:
            cls.opportunities = json.load(f)
        with open(os.path.join(cls.data_dir, "jobs.json"), "r", encoding="utf-8") as f:
            cls.jobs = json.load(f)

        cls.orchestrator = AgentOrchestrator()

    def test_scenario_S001_protected_gap(self):
        cand = self.candidates["C001"]
        role = self.target_roles["R001"]
        ctx = {"candidate": cand, "target_role": role, "courses": self.courses, "opportunities": self.opportunities, "jobs": self.jobs, "include_llm_reasoning": False}
        res = self.orchestrator.run_career_pipeline(ctx)
        
        high_gaps = [g["skill"].lower() for g in res["skill_gaps"] if g["priority"] == "high"]
        self.assertIn("docker", high_gaps)
        self.assertIn("kubernetes", high_gaps)

    def test_scenario_S002_beginner_ml(self):
        cand = self.candidates["C002"]
        role = self.target_roles["R001"]
        ctx = {"candidate": cand, "target_role": role, "courses": self.courses, "opportunities": self.opportunities, "jobs": self.jobs, "include_llm_reasoning": False}
        res = self.orchestrator.run_career_pipeline(ctx)
        self.assertIn("developing", res["readiness"]["status"].lower())

    def test_scenario_S003_strong_ml(self):
        cand = self.candidates["C003"]
        role = self.target_roles["R001"]
        ctx = {"candidate": cand, "target_role": role, "courses": self.courses, "opportunities": self.opportunities, "jobs": self.jobs, "include_llm_reasoning": False}
        res = self.orchestrator.run_career_pipeline(ctx)
        high_gaps = [g["skill"] for g in res["skill_gaps"] if g["priority"] == "high"]
        self.assertEqual(len(high_gaps), 0)
        self.assertIn("job ready", res["readiness"]["status"].lower())

    def test_scenario_S004_career_switcher(self):
        cand = self.candidates["C004"]
        role = self.target_roles["R002"]
        ctx = {"candidate": cand, "target_role": role, "courses": self.courses, "opportunities": self.opportunities, "jobs": self.jobs, "include_llm_reasoning": False}
        res = self.orchestrator.run_career_pipeline(ctx)
        top_opp = res["matched_opportunities"][0]["title"]
        self.assertIn("Data Analyst", top_opp)

    def test_scenario_S005_backend_specialist(self):
        cand = self.candidates["C005"]
        role = self.target_roles["R003"]
        ctx = {"candidate": cand, "target_role": role, "courses": self.courses, "opportunities": self.opportunities, "jobs": self.jobs, "include_llm_reasoning": False}
        res = self.orchestrator.run_career_pipeline(ctx)
        top_opp = res["matched_opportunities"][0]["title"]
        self.assertIn("Backend Developer", top_opp)
        self.assertIn("job ready", res["readiness"]["status"].lower())

    def test_scenario_S006_fairness_parity(self):
        cand_A = dict(self.candidates["C001"])
        cand_B = dict(self.candidates["C001"])
        cand_B["career_gaps"] = []

        role = self.target_roles["R001"]
        readiness_engine = ReadinessEngine()
        matching_engine = MatchingEngine()

        read_A = readiness_engine.calculate(cand_A, role)["readiness_score"]
        read_B = readiness_engine.calculate(cand_B, role)["readiness_score"]

        opp_A = matching_engine.rank(cand_A, self.opportunities)[0]["compatibility_score"]
        opp_B = matching_engine.rank(cand_B, self.opportunities)[0]["compatibility_score"]

        self.assertEqual(read_A, read_B)
        self.assertEqual(opp_A, opp_B)


if __name__ == "__main__":
    unittest.main()
