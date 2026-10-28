"""Tests for O*NET repository — SAP HANA Cloud."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.connection import is_hana_available
from database.repositories.onet_repository import ONetRepository

SKIP_REASON = "HANA credentials not configured (set HANA_HOST, HANA_USER, HANA_PASSWORD)"


@pytest.mark.skipif(not is_hana_available(), reason=SKIP_REASON)
class TestONetRepository:
    """Tests that require a live SAP HANA Cloud connection with ONET data."""

    @pytest.fixture
    def repo(self):
        return ONetRepository()

    def test_find_occupations_returns_results(self, repo):
        results = repo.find_occupations("software", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        first = results[0]
        assert "onetsoc_code" in first
        assert "title" in first
        assert "description" in first

    def test_find_occupations_empty_search(self, repo):
        results = repo.find_occupations("zzz_nonexistent_zzz", limit=5)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_occupation_by_code(self, repo):
        # First find an occupation
        results = repo.find_occupations("software", limit=1)
        if results:
            code = results[0]["onetsoc_code"]
            occ = repo.get_occupation(code)
            assert occ is not None
            assert occ["onetsoc_code"] == code

    def test_get_essential_skills(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            code = results[0]["onetsoc_code"]
            skills = repo.get_essential_skills(code, scale_id="IM", limit=10)
            assert isinstance(skills, list)
            if skills:
                first = skills[0]
                assert "element_name" in first
                assert "data_value" in first
                assert isinstance(first["data_value"], float)

    def test_get_transferable_skills(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            code = results[0]["onetsoc_code"]
            skills = repo.get_transferable_skills(code, limit=10)
            assert isinstance(skills, list)

    def test_get_knowledge(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            code = results[0]["onetsoc_code"]
            knowledge = repo.get_knowledge(code, limit=10)
            assert isinstance(knowledge, list)

    def test_get_abilities(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            code = results[0]["onetsoc_code"]
            abilities = repo.get_abilities(code, limit=10)
            assert isinstance(abilities, list)

    def test_get_work_activities(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            code = results[0]["onetsoc_code"]
            activities = repo.get_work_activities(code, limit=10)
            assert isinstance(activities, list)
