"""
Database package for verified benchmark datasets.

Provides in-memory DataService abstraction for career calibration,
course syllabi, target roles, and opportunities.
"""

from database.data_service import DataService

__all__ = [
    "DataService",
]
