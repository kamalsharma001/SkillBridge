"""Tests for DataService — both JSON and HANA modes."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.connection import is_hana_available
from database.data_service import DataService

SKIP_REASON = "HANA credentials not configured (set HANA_HOST, HANA_USER, HANA_PASSWORD)"


class TestDataServiceJsonMode:
    """Tests for DataService in JSON mode (always runs, no HANA needed)."""

    @pytest.fixture
    def ds(self):
        return DataService(data_source="json")

    def test_json_mode_is_not_hana(self, ds):
        assert not ds.is_hana
        assert ds.data_source == "json"

    def test_json_mode_returns_empty_for_unknown_candidate(self, ds):
        result = ds.get_candidate("NONEXISTENT_ID")
        assert result is None

    def test_json_mode_get_jobs(self, ds):
        jobs = ds.get_jobs(limit=5)
        assert isinstance(jobs, list)
        # May be empty if jobs.json doesn't exist in test env

    def test_json_mode_get_courses(self, ds):
        courses = ds.get_courses(limit=5)
        assert isinstance(courses, list)

    def test_json_mode_find_occupations(self, ds):
        results = ds.find_occupations("software", limit=5)
        assert isinstance(results, list)

    def test_json_mode_find_skills_returns_empty(self, ds):
        # ESCO skills are only in HANA, not JSON
        results = ds.find_skills("python", limit=5)
        assert isinstance(results, list)
        assert len(results) == 0


@pytest.mark.skipif(not is_hana_available(), reason=SKIP_REASON)
class TestDataServiceHanaMode:
    """Tests for DataService in HANA mode."""

    @pytest.fixture
    def ds(self):
        return DataService(data_source="hana")

    def test_hana_mode_is_hana(self, ds):
        assert ds.is_hana
        assert ds.data_source == "hana"

    def test_hana_mode_get_jobs(self, ds):
        jobs = ds.get_jobs(limit=5)
        assert isinstance(jobs, list)
        assert len(jobs) > 0

    def test_hana_mode_find_occupations(self, ds):
        results = ds.find_occupations("software", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_hana_mode_find_skills(self, ds):
        results = ds.find_skills("python", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_hana_mode_get_courses(self, ds):
        courses = ds.get_courses(limit=5)
        assert isinstance(courses, list)
        assert len(courses) > 0

    def test_hana_mode_get_candidate_with_skills(self, ds):
        # Get a candidate ID first
        from database.repositories.skillbridge_repository import SkillBridgeRepository
        repo = SkillBridgeRepository()
        candidates = repo.find_candidates(limit=1)
        if candidates:
            cid = candidates[0]["candidate_id"]
            candidate = ds.get_candidate(cid)
            assert candidate is not None
            assert "skills" in candidate
            assert isinstance(candidate["skills"], list)
