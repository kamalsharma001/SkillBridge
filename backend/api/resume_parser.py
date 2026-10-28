import os
import json
import re
import pdfplumber
import docx
from typing import Dict, Any, List, Optional
from uuid import uuid4

from config.settings import Settings


async def extract_text_from_file(file_path: str) -> str:
    """Extracts text content from a PDF or DOCX file."""
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    elif ext == ".docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX.")
        
    return text


# Common skill keywords for regex-based extraction (fallback when LLM unavailable)
SKILL_KEYWORDS = [
    "python", "sql", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php",
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "keras", "xgboost",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible",
    "git", "github", "gitlab", "ci/cd", "jenkins", "github actions",
    "react", "vue", "angular", "next.js", "node.js", "express", "django", "flask", "fastapi",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka", "rabbitmq",
    "spark", "hadoop", "airflow", "dbt", "snowflake", "databricks",
    "tableau", "power bi", "looker", "excel", "powerpoint",
    "agile", "scrum", "jira", "confluence",
    "mlops", "data engineering", "data analysis", "data science", "statistics",
    "nlp", "computer vision", "reinforcement learning", "transformers", "bert", "gpt",
    "api", "rest", "graphql", "microservices", "spring boot", "spring",
]


def _extract_skills_regex(text: str) -> List[Dict[str, Any]]:
    """Extract skills from text using regex pattern matching as fallback."""
    text_lower = text.lower()
    found_skills = []
    
    for skill in SKILL_KEYWORDS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            # Base proficiency - don't inflate based on keyword frequency
            # Keyword presence alone indicates familiarity, not proficiency
            found_skills.append({
                "name": skill.title(),
                "normalized_name": skill.lower().replace(" ", "_").replace(".", "").replace("#", "sharp"),
                "proficiency": 0.4,  # Base level for keyword detection
                "experience_months": 6,  # Conservative default
                "evidence": [f"Mentioned in resume"],
                "project_evidence": 0,
                "course_completion": 0.0,
                "recency_score": 1.0,
            })
    
    # Deduplicate by normalized_name
    seen = set()
    deduped = []
    for s in found_skills:
        if s["normalized_name"] not in seen:
            seen.add(s["normalized_name"])
            deduped.append(s)
    
    return deduped


def _extract_basic_profile(text: str) -> Dict[str, Any]:
    """Extract basic profile info using regex patterns."""
    lines = text.split('\n')
    name = ""
    current_role = ""
    location = ""
    education = []
    experience_years = 0.0
    
    # Try to find name (first non-empty line that looks like a name)
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) < 50 and not any(kw in line.lower() for kw in ["email", "phone", "linkedin", "github", "objective", "summary", "experience", "education", "skills", "project", "certification"]):
            name = line
            break
    
    # Try to find current role - look for explicit "current" or "present" markers
    for line in lines:
        line = line.strip()
        line_lower = line.lower()
        if ("current" in line_lower or "present" in line_lower) and len(line) < 100:
            # Check if it's actually a job title line
            if any(kw in line_lower for kw in ["engineer", "developer", "analyst", "scientist", "manager", "lead", "architect", "consultant", "specialist"]):
                current_role = line
                break
    
    # Fallback: first line with job title keywords
    if not current_role:
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            if any(kw in line_lower for kw in ["software engineer", "data scientist", "ml engineer", "machine learning engineer", "data analyst", "backend engineer", "frontend engineer", "full stack"]):
                if len(line) < 100:
                    current_role = line
                    break
    
    # Try to find location
    for line in lines:
        line = line.strip()
        if any(kw in line.lower() for kw in ["location", "city", "state", "country", "remote"]):
            location = line
            break
    
    # Try to find education
    for line in lines:
        line = line.strip()
        if any(kw in line.lower() for kw in ["bachelor", "master", "phd", "degree", "university", "college", "institute"]):
            education.append(line)
    
    return {
        "name": name,
        "current_role": current_role,
        "location": location,
        "education": education,
        "experience_years": experience_years,
    }


async def parse_resume_to_profile(file_path: str, llm_service) -> Dict[str, Any]:
    """Uses LLM to extract and normalize resume text into a CandidateProfile schema.
    
    Falls back to regex-based extraction if LLM is unavailable.
    """
    text = await extract_text_from_file(file_path)
    
    if not text.strip():
        raise ValueError("No readable text found in the file.")
    
    # Try LLM-based extraction first
    model = Settings.LLM_MODEL_FAST
    
    system_prompt = """You are an expert Resume Parser. Your job is to extract the candidate's professional profile from the provided raw resume text and output it EXACTLY as a JSON object matching the CandidateProfile schema. 

IMPORTANT SCHEMA RULES:
1. "candidate_id": Generate a random UUID string.
2. "name": The candidate's full name.
3. "current_role": Their most recent job title.
4. "skills": An array of skill objects. Each skill MUST have:
   - "name": The original skill name.
   - "normalized_name": The standardized O*NET/ESCO name (e.g., "Python", "Docker", "Machine Learning").
   - "proficiency": A float between 0.0 and 1.0 based on their experience.
   - "experience_months": Total months using this skill.
   - "evidence": An array of strings citing where they used it (e.g. "Used Python in 3 projects").
5. "experience_years": Total years of professional experience (float).
6. "projects": Array of projects with "name", "description", "skills" (array of strings), "outcomes" (array of strings).
7. "education": Array of degree strings.
8. "location": Candidate's location.

Return ONLY the valid JSON object, no markdown, no backticks, no explanations.
"""

    # Try LLM extraction
    if llm_service and llm_service.client and getattr(Settings, "ENABLE_LLM_SYNTHESIS", True):
        try:
            response_text = await llm_service.generate_reasoning_async(system_prompt, text[:15000], model)
            
            import json_repair

            # Try json-repair on the raw response first as it is very robust
            try:
                repaired = json_repair.repair_json(response_text, return_objects=True)
                if isinstance(repaired, dict):
                    # Ensure candidate_id exists
                    if not repaired.get("candidate_id"):
                        repaired["candidate_id"] = str(uuid4())
                    return repaired
            except Exception:
                pass

            import re
            # Try to find the JSON object within the response using regex as a fallback
            match = re.search(r'\{[\s\S]*\}', response_text)
            first_brace_match = re.search(r'\{[\s\S]*', response_text)
            
            candidates = []
            if match:
                candidates.append(match.group(0))
            if first_brace_match:
                candidates.append(first_brace_match.group(0))
            candidates.append(response_text.strip())

            for text_to_parse in candidates:
                try:
                    repaired = json_repair.repair_json(text_to_parse, return_objects=True)
                    if isinstance(repaired, dict):
                        if not repaired.get("candidate_id"):
                            repaired["candidate_id"] = str(uuid4())
                        return repaired
                except Exception:
                    pass
        except Exception as e:
            # LLM failed, fall through to regex extraction
            pass
    
    # Fallback: Regex-based extraction
    print("LLM extraction failed or unavailable, using regex-based fallback...")
    basic_info = _extract_basic_profile(text)
    skills = _extract_skills_regex(text)
    
    # If we still have very few skills, add some defaults based on common patterns
    if len(skills) < 3:
        # Try to infer from text
        if "python" in text.lower() and not any(s["normalized_name"] == "python" for s in skills):
            skills.append({"name": "Python", "normalized_name": "python", "proficiency": 0.4, "experience_months": 6, "evidence": ["Inferred from resume"], "project_evidence": 0, "course_completion": 0.0, "recency_score": 1.0})
        if "sql" in text.lower() and not any(s["normalized_name"] == "sql" for s in skills):
            skills.append({"name": "SQL", "normalized_name": "sql", "proficiency": 0.4, "experience_months": 6, "evidence": ["Inferred from resume"], "project_evidence": 0, "course_completion": 0.0, "recency_score": 1.0})
    
    profile = {
        "candidate_id": str(uuid4()),
        "name": basic_info["name"] or "Unknown Candidate",
        "current_role": basic_info["current_role"] or "Not specified",
        "education": basic_info["education"] if basic_info["education"] else ["Not specified"],
        "skills": skills,
        "experience_years": basic_info["experience_years"],
        "projects": [],
        "certifications": [],
        "courses_completed": [],
        "location": basic_info["location"] or "Not specified",
    }
    
    return profile