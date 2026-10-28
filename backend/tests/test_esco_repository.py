"""Tests for ESCO repository — SAP HANA Cloud."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.connection import is_hana_available
from database.repositories.esco_repository import ESCORepository

SKIP_REASON = "HANA credentials not configured (set HANA_HOST, HANA_USER, HANA_PASSWORD)"


@pytest.mark.skipif(not is_hana_available(), reason=SKIP_REASON)
class TestESCORepository:
    """Tests that require a live SAP HANA Cloud connection with ESCO data."""

    @pytest.fixture
    def repo(self):
        return ESCORepository()

    def test_find_skills_returns_results(self, repo):
        results = repo.find_skills("python", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        first = results[0]
        assert "uri" in first
        assert "name" in first
        assert "type" in first

    def test_find_skills_empty_search(self, repo):
        results = repo.find_skills("zzz_nonexistent_zzz", limit=5)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_skill_by_uri(self, repo):
        results = repo.find_skills("python", limit=1)
        if results:
            uri = results[0]["uri"]
            skill = repo.get_skill(uri)
            assert skill is not None
            assert skill["uri"] == uri
            assert "name" in skill

    def test_find_occupations_returns_results(self, repo):
        results = repo.find_occupations("software", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        first = results[0]
        assert "uri" in first
        assert "name" in first

    def test_get_occupation_by_uri(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            uri = results[0]["uri"]
            occ = repo.get_occupation(uri)
            assert occ is not None
            assert occ["uri"] == uri

    def test_get_occupation_skills(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            uri = results[0]["uri"]
            skills = repo.get_occupation_skills(uri, limit=20)
            assert isinstance(skills, list)
            if skills:
                first = skills[0]
                assert "skill_uri" in first
                assert "relation_type" in first
                assert "skill_name" in first

    def test_get_occupation_skills_filtered(self, repo):
        results = repo.find_occupations("software", limit=1)
        if results:
            uri = results[0]["uri"]
            essential = repo.get_occupation_skills(
                uri, relation_type="essential", limit=20
            )
            assert isinstance(essential, list)
            for s in essential:
                assert s["relation_type"] == "essential"

    def test_get_skill_relations(self, repo):
        results = repo.find_skills("python", limit=1)
        if results:
            uri = results[0]["uri"]
            relations = repo.get_skill_relations(uri, limit=10)
            assert isinstance(relations, list)
