"""Tests for DataService in-memory benchmark mode."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.data_service import DataService


class TestDataServiceJsonMode:
    """Tests for DataService in in-memory benchmark mode."""

    @pytest.fixture
    def ds(self):
        return DataService(data_source="json")

    def test_json_mode_configuration(self, ds):
        assert ds.data_source == "json"

    def test_json_mode_returns_empty_for_unknown_candidate(self, ds):
        result = ds.get_candidate("NONEXISTENT_ID")
        assert result is None

    def test_json_mode_get_jobs(self, ds):
        jobs = ds.get_jobs(limit=5)
        assert isinstance(jobs, list)

    def test_json_mode_get_courses(self, ds):
        courses = ds.get_courses(limit=5)
        assert isinstance(courses, list)

    def test_json_mode_find_occupations(self, ds):
        results = ds.find_occupations("software", limit=5)
        assert isinstance(results, list)
