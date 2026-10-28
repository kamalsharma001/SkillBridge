"""Tests for SkillBridge repository — SAP HANA Cloud."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.connection import is_hana_available
from database.repositories.skillbridge_repository import SkillBridgeRepository

SKIP_REASON = "HANA credentials not configured (set HANA_HOST, HANA_USER, HANA_PASSWORD)"


@pytest.mark.skipif(not is_hana_available(), reason=SKIP_REASON)
class TestSkillBridgeRepository:
    """Tests that require a live SAP HANA Cloud connection with SYNTHETIC data."""

    @pytest.fixture
    def repo(self):
        return SkillBridgeRepository()

    # -- Candidates --

    def test_find_candidates(self, repo):
        results = repo.find_candidates(limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        first = results[0]
        assert "candidate_id" in first
        assert "name" in first

    def test_get_candidate_by_id(self, repo):
        candidates = repo.find_candidates(limit=1)
        if candidates:
            cid = candidates[0]["candidate_id"]
            candidate = repo.get_candidate(cid)
            assert candidate is not None
            assert candidate["candidate_id"] == cid

    def test_get_candidate_skills(self, repo):
        candidates = repo.find_candidates(limit=1)
        if candidates:
            cid = candidates[0]["candidate_id"]
            skills = repo.get_candidate_skills(cid)
            assert isinstance(skills, list)
            if skills:
                first = skills[0]
                assert "name" in first
                assert "normalized_name" in first
                assert "proficiency" in first
                assert 0.0 <= first["proficiency"] <= 1.0

    # -- Jobs --

    def test_get_jobs(self, repo):
        jobs = repo.get_jobs(limit=5)
        assert isinstance(jobs, list)
        assert len(jobs) > 0
        first = jobs[0]
        assert "job_id" in first
        assert "title" in first
        assert "required_skills" in first
        assert isinstance(first["required_skills"], list)

    def test_get_job_by_id(self, repo):
        jobs = repo.get_jobs(limit=1)
        if jobs:
            jid = jobs[0]["job_id"]
            job = repo.get_job(jid)
            assert job is not None
            assert job["job_id"] == jid

    def test_get_job_skills(self, repo):
        jobs = repo.get_jobs(limit=1)
        if jobs:
            jid = jobs[0]["job_id"]
            skills = repo.get_job_skills(jid)
            assert isinstance(skills, list)

    # -- Courses --

    def test_get_courses(self, repo):
        courses = repo.get_courses(limit=5)
        assert isinstance(courses, list)
        assert len(courses) > 0
        first = courses[0]
        assert "title" in first
        assert "platform" in first
        assert "skills" in first
        assert isinstance(first["skills"], list)

    def test_get_courses_by_skill(self, repo):
        courses = repo.get_courses(skill_name="python", limit=5)
        assert isinstance(courses, list)

    def test_get_courses_for_skills(self, repo):
        courses = repo.get_courses_for_skills(
            skill_names=["python", "sql"], limit=5
        )
        assert isinstance(courses, list)
