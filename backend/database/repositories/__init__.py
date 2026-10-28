"""
Repository classes for SAP HANA Cloud data access.

Each repository targets a specific HANA schema:
    - ONetRepository   → ONET schema
    - ESCORepository   → ESCO schema
    - SkillBridgeRepository → SYNTHETIC schema
"""

from database.repositories.onet_repository import ONetRepository
from database.repositories.esco_repository import ESCORepository
from database.repositories.skillbridge_repository import SkillBridgeRepository

__all__ = [
    "ONetRepository",
    "ESCORepository",
    "SkillBridgeRepository",
]
