"""
Unified Data Service — the single integration point between agents/engines and data sources.

Abstracts over two data sources:
    - "json"  → loads from ai-career-engine/data/*.json (test fixtures)
    - "hana"  → delegates to repository classes (SAP HANA Cloud production)

Agents and the orchestrator interact ONLY with DataService. They never
import repositories or execute SQL directly.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


class DataService:
    """Unified data access service toggling between JSON fixtures and SAP HANA Cloud."""

    def __init__(self, data_source: Optional[str] = None):
        """Initialize DataService.

        Args:
            data_source: "json" or "hana". If None, reads DATA_SOURCE env var
                         (defaults to "hana").
        """
        self.data_source = (
            data_source or os.getenv("DATA_SOURCE", "hana")
        ).strip().lower()
        if self.data_source not in {"hana", "json"}:
            raise ValueError("DATA_SOURCE must be either 'hana' or 'json'")

        # Lazy-init repositories only when needed
        self._onet_repo = None
        self._esco_repo = None
        self._skillbridge_repo = None

        # Cache for JSON data
        self._json_cache: Dict[str, Any] = {}

    @property
    def is_hana(self) -> bool:
        return self.data_source == "hana"

    # ------------------------------------------------------------------
    # Repository accessors (lazy init)
    # ------------------------------------------------------------------

    def _get_onet_repo(self):
        if self._onet_repo is None:
            from database.repositories.onet_repository import ONetRepository
            self._onet_repo = ONetRepository()
        return self._onet_repo

    def _get_esco_repo(self):
        if self._esco_repo is None:
            from database.repositories.esco_repository import ESCORepository
            self._esco_repo = ESCORepository()
        return self._esco_repo

    def _get_skillbridge_repo(self):
        if self._skillbridge_repo is None:
            from database.repositories.skillbridge_repository import SkillBridgeRepository
            self._skillbridge_repo = SkillBridgeRepository()
        return self._skillbridge_repo

    # ------------------------------------------------------------------
    # JSON file helpers
    # ------------------------------------------------------------------

    def _get_data_dir(self) -> str:
        """Resolve the data/ directory relative to ai-career-engine root."""
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
        """Fetch a candidate profile by ID.

        JSON mode: searches data/candidates.json.
        HANA mode: queries SYNTHETIC.CANDIDATES + CANDIDATE_SKILLS.
        """
        if self.is_hana:
            repo = self._get_skillbridge_repo()
            candidate = repo.get_candidate(candidate_id)
            if candidate:
                candidate["skills"] = repo.get_candidate_skills(candidate_id)
            return candidate
        else:
            candidates = self._load_json("candidates.json")
            for c in candidates:
                if c.get("candidate_id") == candidate_id:
                    return c
            return None

    def get_candidate_skills(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Fetch skills for a candidate."""
        if self.is_hana:
            return self._get_skillbridge_repo().get_candidate_skills(candidate_id)
        else:
            candidate = self.get_candidate(candidate_id)
            return candidate.get("skills", []) if candidate else []

    # ------------------------------------------------------------------
    # Jobs / Opportunities
    # ------------------------------------------------------------------

    def get_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch job postings for opportunity matching.

        JSON mode: loads data/jobs.json.
        HANA mode: queries SYNTHETIC.COURSES.
        """
        if self.is_hana:
            return self._get_skillbridge_repo().get_jobs(limit=limit)
        else:
            jobs = self._load_json("jobs.json")
            return jobs[:limit]

    def get_opportunities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch opportunities (alias for jobs)."""
        if self.is_hana:
            return self._get_skillbridge_repo().get_opportunities(limit=limit)
        else:
            # Try opportunities.json first, fall back to jobs.json
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
        """Fetch courses, optionally filtered by skill coverage.

        JSON mode: loads data/courses.json.
        HANA mode: queries SYNTHETIC.COURSES.
        """
        if self.is_hana:
            if skill_names:
                return self._get_skillbridge_repo().get_courses_for_skills(
                    skill_names, limit=limit
                )
            else:
                return self._get_skillbridge_repo().get_courses(limit=limit)
        else:
            courses = self._load_json("courses.json")
            if skill_names:
                # Filter courses by skill overlap
                filtered = []
                for course in courses:
                    c_skills = [str(s).lower().replace(" ", "_") for s in course.get("skills", [])]
                    if any(skill.lower().replace(" ", "_") in c_skills for skill in skill_names):
                        filtered.append(course)
                return filtered[:limit]
            return courses[:limit]

    # ------------------------------------------------------------------
    # O*NET Data
    # ------------------------------------------------------------------

    def find_occupations(
        self, search_term: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search O*NET occupations by title."""
        if self.is_hana:
            return self._get_onet_repo().find_occupations(search_term, limit=limit)
        else:
            # JSON fallback — search target_roles.json
            roles = self._load_json("target_roles.json")
            term_lower = search_term.lower()
            return [
                r for r in roles
                if term_lower in r.get("name", "").lower()
            ][:limit]

    def get_occupation_skills(
        self, onetsoc_code: str, scale_id: str = "IM", limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get essential skills for an O*NET occupation."""
        if self.is_hana:
            return self._get_onet_repo().get_essential_skills(
                onetsoc_code, scale_id=scale_id, limit=limit
            )
        else:
            return []

    # ------------------------------------------------------------------
    # ESCO Data
    # ------------------------------------------------------------------

    def find_skills(
        self, search_term: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search ESCO skills by label."""
        if self.is_hana:
            return self._get_esco_repo().find_skills(search_term, limit=limit)
        else:
            return []

    def get_esco_occupation_skills(
        self, occupation_uri: str, relation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get skills linked to an ESCO occupation."""
        if self.is_hana:
            return self._get_esco_repo().get_occupation_skills(
                occupation_uri, relation_type=relation_type
            )
        else:
            return []

    # ------------------------------------------------------------------
    # Market Data
    # ------------------------------------------------------------------

    def get_market_history(self) -> List[Dict[str, Any]]:
        """Load market history data.

        Production analysis is intentionally HANA-only; JSON market history is
        reserved for explicit local test mode.
        """
        if self.is_hana:
            return []
        return self._load_json("market_history.json")
