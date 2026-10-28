"""
Unified Data Service — the single integration point between agents/engines and data sources.

Loads from backend/data/*.json verified benchmark datasets in memory:
    - candidates.json
    - target_roles.json
    - courses.json
    - jobs.json
    - opportunities.json
    - market_history.json
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


class DataService:
    """Unified in-memory data access service for verified benchmark datasets."""

    def __init__(self, data_source: Optional[str] = None):
        self.data_source = (data_source or os.getenv("DATA_SOURCE", "json")).strip().lower()
        self._json_cache: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # JSON file helpers
    # ------------------------------------------------------------------

    def _get_data_dir(self) -> str:
        """Resolve the data/ directory relative to backend root."""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
        )

    def _load_json(self, filename: str) -> Any:
        """Load and cache a JSON file from the data/ directory."""
        if filename not in self._json_cache:
            filepath = os.path.join(self._get_data_dir(), filename)
            if not os.path.exists(filepath):
                self._json_cache[filename] = []
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    self._json_cache[filename] = json.load(f)
        return self._json_cache[filename]

    # ------------------------------------------------------------------
    # Candidates
    # ------------------------------------------------------------------

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a candidate profile by ID from candidates.json."""
        candidates = self._load_json("candidates.json")
        for c in candidates:
            if c.get("candidate_id") == candidate_id:
                return c
        return None

    def get_candidate_skills(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Fetch skills for a candidate."""
        candidate = self.get_candidate(candidate_id)
        return candidate.get("skills", []) if candidate else []

    # ------------------------------------------------------------------
    # Jobs / Opportunities
    # ------------------------------------------------------------------

    def get_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch job postings from jobs.json."""
        jobs = self._load_json("jobs.json")
        return jobs[:limit]

    def get_opportunities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch opportunities from opportunities.json or jobs.json."""
        opps = self._load_json("opportunities.json")
        if opps:
            return opps[:limit]
        jobs = self._load_json("jobs.json")
        return jobs[:limit]

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------

    def get_courses(
        self, skill_names: Optional[List[str]] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch courses, optionally filtered by skill coverage."""
        courses = self._load_json("courses.json")
        if skill_names:
            filtered = []
            for course in courses:
                c_skills = [str(s).lower().replace(" ", "_") for s in course.get("skills", [])]
                if any(skill.lower().replace(" ", "_") in c_skills for skill in skill_names):
                    filtered.append(course)
            return filtered[:limit]
        return courses[:limit]

    # ------------------------------------------------------------------
    # Occupations / Roles
    # ------------------------------------------------------------------

    def find_occupations(
        self, search_term: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search target roles by title."""
        roles = self._load_json("target_roles.json")
        term_lower = search_term.lower()
        return [
            r for r in roles
            if term_lower in r.get("name", "").lower()
        ][:limit]

    def get_occupation_skills(
        self, onetsoc_code: str, scale_id: str = "IM", limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get essential skills for an occupation."""
        roles = self._load_json("target_roles.json")
        for r in roles:
            if r.get("id") == onetsoc_code or r.get("name", "").lower() == onetsoc_code.lower():
                return [{"skill": s, "importance": 4.5} for s in r.get("required_skills", [])][:limit]
        return []

    def find_skills(
        self, search_term: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search skills across course and role taxonomies."""
        courses = self._load_json("courses.json")
        all_skills = set()
        term = search_term.lower()
        for c in courses:
            for s in c.get("skills", []):
                if term in str(s).lower():
                    all_skills.add(str(s))
        return [{"skill": s} for s in sorted(all_skills)][:limit]

    def get_esco_occupation_skills(
        self, occupation_uri: str, relation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get skills linked to an occupation."""
        return []

    # ------------------------------------------------------------------
    # Market Data
    # ------------------------------------------------------------------

    def get_market_history(self) -> List[Dict[str, Any]]:
        """Load historical market data from market_history.json."""
        return self._load_json("market_history.json")
