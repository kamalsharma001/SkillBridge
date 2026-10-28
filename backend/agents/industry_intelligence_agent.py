from __future__ import annotations
from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent
from engines.market_engine import MarketEngine
from models.schemas import AgentResult


from models.contexts import IndustryAgentContext

class IndustryIntelligenceAgent(BaseAgent):
    """Industry Intelligence Agent: Monitors technology trends, analyzes changing skill requirements, and identifies emerging tools."""

    def __init__(self, market_engine: MarketEngine = None, data_service=None, llm_service=None):
        super().__init__(name="industry_intelligence", llm_service=llm_service)
        self.market_engine = market_engine or MarketEngine()
        self.data_service = data_service

    def run(self, context: IndustryAgentContext) -> AgentResult:
        jobs = context.jobs

        # In HANA mode: fetch jobs from SAP HANA if none provided
        if not jobs and self.data_service and self.data_service.is_hana:
            jobs = self.data_service.get_jobs(limit=50)

        trends = self.market_engine.calculate_trends(current_jobs=jobs)
        emerging = self.market_engine.emerging_skills(trends)

        insights = [
            f"Demand for {skill} is increasing across target role postings. Prioritize in roadmap."
            for skill in emerging
        ]

        data_payload = {
            "skill_trends": trends,
            "emerging_skills": emerging,
            "insights": insights,
        }

        # Build evidence with source, record reference, and derived claim
        evidence = []
        
        # Evidence for market data source
        if self.data_service and self.data_service.is_hana:
            evidence.append({
                "source": "Market History (SAP HANA)",
                "dataset_record_id": f"market_history.jobs_{len(jobs)}",
                "claim": f"Analyzed trends across {len(jobs)} job postings from HANA"
            })
        elif jobs:
            evidence.append({
                "source": "Job Postings (local/test fixtures)",
                "dataset_record_id": f"jobs.local_{len(jobs)}",
                "claim": f"Analyzed trends across {len(jobs)} local job fixtures"
            })
        else:
            evidence.append({
                "source": "Market Engine",
                "dataset_record_id": "market_engine.no_jobs",
                "claim": "No job data available for trend analysis"
            })
        
        # Evidence for trend calculation
        growing_skills = [t for t in trends if t.get("trend") == "GROWING"]
        declining_skills = [t for t in trends if t.get("trend") == "DECLINING"]
        evidence.append({
            "source": "Market Engine - Trend Analysis",
            "dataset_record_id": f"trends.calculated_{len(trends)}",
            "claim": f"Calculated trends for {len(trends)} skills: {len(growing_skills)} growing, {len(declining_skills)} declining, {len(trends) - len(growing_skills) - len(declining_skills)} stable"
        })
        
        # Evidence for emerging skills
        if emerging:
            evidence.append({
                "source": "Market Engine - Emerging Skills",
                "dataset_record_id": f"emerging.skills_{len(emerging)}",
                "claim": f"Identified {len(emerging)} emerging skills with upward growth trends: {', '.join(emerging[:5])}"
            })

        # LLM Synthesis setup (executed later by orchestrator)
        system_prompt = (
            "You are a highly analytical Tech Industry Analyst. Review the job market trends "
            "and emerging skills data. Synthesize a concise market narrative detailing what is "
            "currently in high demand and what technologies the candidate should prioritize to stay competitive."
            "do not return any flowcharts or use bold letters."
        )

        return AgentResult(
            agent=self.name,
            status="success",
            summary=f"Analyzed industry market intelligence: identified {len(trends)} skill trends and {len(emerging)} emerging tools.",
            system_prompt=system_prompt,
            data=data_payload,
            evidence=evidence,
        )
