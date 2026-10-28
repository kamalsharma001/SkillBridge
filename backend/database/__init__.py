"""
Database package for SAP HANA Cloud connectivity.

Provides connection management, repository classes for ONET/ESCO/SKILLBRIDGE schemas,
and a unified DataService abstraction that toggles between JSON test fixtures
and SAP HANA Cloud production data.
"""

from database.connection import get_hana_connection, test_connection

__all__ = [
    "get_hana_connection",
    "test_connection",
]
