from __future__ import annotations
from typing import Any, Dict, List, Optional
from agents.base_agent import BaseAgent
from engines.recommendation_engine import RecommendationEngine
from models.schemas import AgentResult
from models.contexts import LearningAgentContext


CERTIFICATION_MAPPING = {
    "docker": [{"title": "Docker Certified Associate (DCA)", "target_skill": "Docker", "level": "Intermediate"}],
    "kubernetes": [{"title": "Certified Kubernetes Application Developer (CKAD)", "target_skill": "Kubernetes", "level": "Advanced"}],
    "mlops": [{"title": "AWS Certified Machine Learning - Specialty", "target_skill": "MLOps", "level": "Advanced"}],
    "aws": [{"title": "AWS Certified Solutions Architect - Associate", "target_skill": "AWS", "level": "Intermediate"}],
    "azure": [{"title": "Microsoft Certified: Azure AI Engineer Associate", "target_skill": "Azure", "level": "Intermediate"}],
    "gcp": [{"title": "Google Cloud Professional Machine Learning Engineer", "target_skill": "GCP", "level": "Advanced"}],
    "tensorflow": [{"title": "TensorFlow Developer Certificate", "target_skill": "TensorFlow", "level": "Intermediate"}],
    "pytorch": [{"title": "PyTorch Certification", "target_skill": "PyTorch", "level": "Intermediate"}],
    "spark": [{"title": "Databricks Certified Associate Developer for Apache Spark", "target_skill": "Spark", "level": "Intermediate"}],
    "sql": [{"title": "Microsoft Certified: Azure Data Fundamentals", "target_skill": "SQL", "level": "Entry"}],
    "tableau": [{"title": "Tableau Desktop Specialist", "target_skill": "Tableau", "level": "Entry"}],
    "power_bi": [{"title": "Microsoft Power BI Data Analyst Associate", "target_skill": "Power BI", "level": "Intermediate"}],
    "terraform": [{"title": "HashiCorp Certified: Terraform Associate", "target_skill": "Terraform", "level": "Intermediate"}],
    "kafka": [{"title": "Confluent Certified Developer for Apache Kafka", "target_skill": "Kafka", "level": "Intermediate"}],
    "airflow": [{"title": "Astronomer Certification for Apache Airflow", "target_skill": "Airflow", "level": "Intermediate"}],
    "dbt": [{"title": "dbt Certified Analytics Engineer", "target_skill": "dbt", "level": "Intermediate"}],
    "snowflake": [{"title": "Snowflake SnowPro Core Certification", "target_skill": "Snowflake", "level": "Intermediate"}],
    "databricks": [{"title": "Databricks Certified Data Engineer Associate", "target_skill": "Databricks", "level": "Intermediate"}],
}


class LearningAgent(BaseAgent):
    """Learning Agent: Finds relevant courses, recommends certifications, and generates sequenced learning plans."""

    def __init__(self, recommendation_engine: RecommendationEngine = None, data_service=None, llm_service=None):
        super().__init__(name="learning", llm_service=llm_service)
        self.recommendation_engine = recommendation_engine or RecommendationEngine()
        self.data_service = data_service

    def _get_relevant_certifications(self, skill_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map skill gaps to relevant certifications."""
        certifications = []
        gap_skills = {g.get("skill", "").lower().replace(" ", "_").replace(".", "").replace("#", "sharp") for g in skill_gaps if g.get("skill")}
        
        for skill_name in gap_skills:
            if skill_name in CERTIFICATION_MAPPING:
                certifications.extend(CERTIFICATION_MAPPING[skill_name])
        
        # Deduplicate certifications
        seen = set()
        unique_certs = []
        for cert in certifications:
            key = cert["title"]
            if key not in seen:
                seen.add(key)
                unique_certs.append(cert)
        
        return unique_certs[:5]

    def run(self, context: LearningAgentContext) -> AgentResult:
        gaps = context.skill_gaps
        courses = context.courses

        # Fetch courses from DataService if none provided (works for both JSON and HANA modes)
        if not courses and self.data_service:
            gap_skill_names = [g.get("skill", "") for g in gaps if g.get("skill")]
            if gap_skill_names:
                courses = self.data_service.get_courses(
                    skill_names=gap_skill_names, limit=100
                )
            else:
                courses = self.data_service.get_courses(limit=100)

        # In HANA mode, if still no courses, return partial (don't use hardcoded fallbacks)
        is_hana_mode = bool(self.data_service and self.data_service.is_hana)
        if is_hana_mode and not courses:
            return AgentResult(
                agent=self.name,
                status="partial",
                summary="No HANA learning resources were available for the identified gaps.",
                data={"learning_plan": [], "recommended_courses": [], "certifications": []},
                warnings=["HANA returned no courses; hard-coded learning fallbacks were not used."],
            )

        # Default standard course catalog only for explicit local/test mode (JSON mode)
        if not courses:
            courses = [
                {"title": "Docker Fundamentals & Containerization", "skills": ["Docker"], "platform": "Coursera", "duration_hours": 15, "rating": 4.8},
                {"title": "Kubernetes for Developers", "skills": ["Kubernetes"], "platform": "edX", "duration_hours": 20, "rating": 4.7},
                {"title": "Production MLOps Engineering", "skills": ["MLOps"], "platform": "Udemy", "duration_hours": 25, "rating": 4.9},
                {"title": "Advanced SQL for Data Science", "skills": ["SQL"], "platform": "DataCamp", "duration_hours": 10, "rating": 4.6},
            ]

        # Use only actual detected gaps - no artificial gap creation
        effective_gaps = list(gaps)

        # If there are genuinely no gaps, use the target role's required skills to recommend advanced courses
        if not effective_gaps:
            target_skills = context.target_role.get("required_skills", [])
            for ts in target_skills:
                effective_gaps.append({
                    "skill": ts.get("name", "Advanced Concepts"),
                    "priority": "medium",
                    "reason": "Continuous learning and mastery."
                })
            
            # If still no gaps (e.g., no target skills found), we use a generic upskilling approach
            if not effective_gaps:
                effective_gaps.append({
                    "skill": "Advanced " + context.target_role.get("name", "Domain Expertise"),
                    "priority": "low",
                    "reason": "General domain mastery."
                })

        rec_courses = self.recommendation_engine.recommend_courses(
            skill_gaps=effective_gaps,
            courses=courses,
            top_k=20,
        )

        # Fallback: If no exact matches are found, recommend the top 3 highly-rated courses for general upskilling
        if not rec_courses and courses:
            generic_courses = sorted(courses, key=lambda c: float(c.get("rating", 0)), reverse=True)[:3]
            for c in generic_courses:
                rec_courses.append({
                    "title": c.get("title", ""),
                    "platform": c.get("provider", c.get("platform", "Online")),
                    "primary_skill": c.get("skills", ["General"])[0] if c.get("skills") else "General",
                    "priority": "low",
                    "duration_hours": c.get("duration_hours", 10),
                    "url": c.get("url", ""),
                    "match_confidence": 50,
                    "relevance_reason": "General upskilling recommended as no exact skill matches were found.",
                })

        # Generate sequenced learning steps
        learning_plan = []
        for idx, course in enumerate(rec_courses, start=1):
            learning_plan.append({
                "step": idx,
                "skill": course["primary_skill"],
                "course_title": course["title"],
                "platform": course["platform"],
                "priority": course["priority"],
                "duration_hours": course["duration_hours"],
                "match_confidence": course.get("match_confidence", 0),
                "relevance_reason": course.get("relevance_reason", ""),
                "url": course.get("url", ""),
            })

        # Generate certifications based on actual skill gaps
        certifications = self._get_relevant_certifications(effective_gaps)

        data_payload = {
            "learning_plan": learning_plan,
            "recommended_courses": rec_courses,
            "certifications": certifications,
        }

        # Build evidence with source, record reference, and derived claim
        evidence = []
        
        # Evidence for course recommendations
        if self.data_service and self.data_service.is_hana:
            evidence.append({
                "source": "Course Catalog (SAP HANA)",
                "dataset_record_id": f"courses.filtered_{len(courses)}",
                "claim": f"Retrieved {len(courses)} courses from HANA catalog matching {len(gaps)} skill gaps"
            })
        else:
            evidence.append({
                "source": "Course Catalog (local)",
                "dataset_record_id": f"courses.local_{len(courses)}",
                "claim": f"Using {len(courses)} courses from local catalog for {len(gaps)} skill gaps"
            })
        
        # Evidence for recommendation engine matching
        evidence.append({
            "source": "Recommendation Engine",
            "dataset_record_id": f"rec_engine.matches_{len(rec_courses)}",
            "claim": f"Matched {len(rec_courses)} courses to {len(effective_gaps)} prioritized skill gaps using skill overlap scoring"
        })
        
        # Evidence for certifications
        if certifications:
            cert_skills = [c.get("target_skill", "").lower() for c in certifications]
            evidence.append({
                "source": "Certification Mapping Database",
                "dataset_record_id": f"certs.mapped_{len(certifications)}",
                "claim": f"Mapped {len(certifications)} certifications to skill gaps: {', '.join(cert_skills)}"
            })

        # LLM Synthesis setup (executed later by orchestrator)
        system_prompt = (
            "You are a specialized Learning & Development Architect. Review the provided JSON data containing the "
            "sequenced learning plan and recommended certifications. Provide a narrative rationale for why this "
            "exact sequence of learning is optimal for the candidate's transition. If the plan or certifications "
            "are empty, acknowledge that no direct matches were found for their current specific gaps. "
            "Make sure you read the JSON payload carefully. Do not return any flowcharts or use bold letters."
        )

        return AgentResult(
            agent=self.name,
            status="success",
            summary=f"Generated {len(learning_plan)}-step sequenced learning plan and recommended {len(certifications)} certifications.",
            system_prompt=system_prompt,
            data=data_payload,
            evidence=evidence,
        )