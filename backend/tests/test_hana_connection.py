"""Tests for SAP HANA Cloud connectivity."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.connection import is_hana_available
from database.connection import test_connection as _hana_test_connection

SKIP_REASON = "HANA credentials not configured (set HANA_HOST, HANA_USER, HANA_PASSWORD)"


@pytest.mark.skipif(not is_hana_available(), reason=SKIP_REASON)
class TestHanaConnection:
    """Tests that require a live SAP HANA Cloud connection."""

    def test_connection_succeeds(self):
        result = _hana_test_connection()
        assert result["status"] == "connected"
        assert "current_user" in result
        assert "current_schema" in result

    def test_connection_returns_version(self):
        result = _hana_test_connection()
        assert result.get("hana_version") is not None
        assert result["hana_version"] != "unknown"
