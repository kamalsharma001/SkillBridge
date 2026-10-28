"""
O*NET data repository — read-only access to the ONET schema in SAP HANA Cloud.

Tables accessed:
    ONET.OCCUPATION_DATA
    ONET.ESSENTIAL_SKILLS
    ONET.TRANSFERABLE_SKILLS
    ONET.KNOWLEDGE
    ONET.ABILITIES
    ONET.WORK_ACTIVITIES

All queries use parameterized SQL. No user input is ever interpolated into SQL strings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from database.connection import get_hana_connection


class ONetRepository:
    """Repository for O*NET occupational data stored in SAP HANA Cloud."""

    # ------------------------------------------------------------------
    # Occupations
    # ------------------------------------------------------------------

    def find_occupations(
        self, search_term: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "O*NET-SOC Code",
                    "Title",
                    "Description"
                FROM "ONET"."ONET_OCCUPATIONS"
                WHERE LOWER("Title") LIKE LOWER(?)
                ORDER BY "Title"
            """
            cursor.execute(sql, (limit, f"%{search_term}%"))
            return [
                {
                    "onetsoc_code": row[0],
                    "title": row[1],
                    "description": row[2],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_occupation(self, onetsoc_code: str) -> Optional[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT "O*NET-SOC Code", "Title", "Description"
                FROM "ONET"."ONET_OCCUPATIONS"
                WHERE "O*NET-SOC Code" = ?
            """
            cursor.execute(sql, (onetsoc_code,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "onetsoc_code": row[0],
                "title": row[1],
                "description": row[2],
            }
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Essential Skills
    # ------------------------------------------------------------------

    def get_essential_skills(
        self,
        onetsoc_code: str,
        scale_id: str = "IM",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "ONET_SOC_CODE",
                    "ELEMENT_ID",
                    "ELEMENT_NAME",
                    "SCALE_ID",
                    "DATA_VALUE",
                    "N",
                    "STANDARD_ERROR",
                    "LOWER_CI_BOUND",
                    "UPPER_CI_BOUND",
                    "RECOMMEND_SUPPRESS",
                    "NOT_RELEVANT",
                    "DATA_DATE",
                    "DOMAIN_SOURCE"
                FROM "ONET"."SKILLS"
                WHERE "ONET_SOC_CODE" = ?
                  AND "SCALE_ID" = ?
                ORDER BY "DATA_VALUE" DESC
            """
            cursor.execute(sql, (limit, onetsoc_code, scale_id))
            return [
                {
                    "onetsoc_code": row[0],
                    "element_id": row[1],
                    "element_name": row[2],
                    "scale_id": row[3],
                    "data_value": float(row[4]) if row[4] is not None else 0.0,
                    "n": row[5],
                    "standard_error": float(row[6]) if row[6] is not None else None,
                    "lower_ci_bound": float(row[7]) if row[7] is not None else None,
                    "upper_ci_bound": float(row[8]) if row[8] is not None else None,
                    "recommend_suppress": row[9],
                    "not_relevant": row[10],
                    "date_updated": row[11],
                    "domain_source": row[12],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Transferable Skills
    # ------------------------------------------------------------------

    def get_transferable_skills(
        self,
        onetsoc_code: str,
        scale_id: str = "IM",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "O*NET-SOC Code",
                    "Element ID",
                    "Element Name",
                    "Scale ID",
                    "Data Value",
                    "Recommend Suppress",
                    "Not Relevant"
                FROM "ONET"."ONET_TRANSFERABLE_SKILLS"
                WHERE "O*NET-SOC Code" = ?
                  AND "Scale ID" = ?
                ORDER BY "Data Value" DESC
            """
            cursor.execute(sql, (limit, onetsoc_code, scale_id))
            return [
                {
                    "onetsoc_code": row[0],
                    "element_id": row[1],
                    "element_name": row[2],
                    "scale_id": row[3],
                    "data_value": float(row[4]) if row[4] is not None else 0.0,
                    "recommend_suppress": row[5],
                    "not_relevant": row[6],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Knowledge
    # ------------------------------------------------------------------

    def get_knowledge(
        self, onetsoc_code: str, scale_id: str = "IM", limit: int = 50
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "O*NET-SOC Code",
                    "Element ID",
                    "Element Name",
                    "Scale ID",
                    "Data Value"
                FROM "ONET"."ONET_KNOWLEDGE"
                WHERE "O*NET-SOC Code" = ?
                  AND "Scale ID" = ?
                ORDER BY "Data Value" DESC
            """
            cursor.execute(sql, (limit, onetsoc_code, scale_id))
            return [
                {
                    "onetsoc_code": row[0],
                    "element_id": row[1],
                    "element_name": row[2],
                    "scale_id": row[3],
                    "data_value": float(row[4]) if row[4] is not None else 0.0,
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Abilities
    # ------------------------------------------------------------------

    def get_abilities(
        self, onetsoc_code: str, scale_id: str = "IM", limit: int = 50
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "O*NET-SOC Code",
                    "Element ID",
                    "Element Name",
                    "Scale ID",
                    "Data Value"
                FROM "ONET"."ONET_ABILITIES"
                WHERE "O*NET-SOC Code" = ?
                  AND "Scale ID" = ?
                ORDER BY "Data Value" DESC
            """
            cursor.execute(sql, (limit, onetsoc_code, scale_id))
            return [
                {
                    "onetsoc_code": row[0],
                    "element_id": row[1],
                    "element_name": row[2],
                    "scale_id": row[3],
                    "data_value": float(row[4]) if row[4] is not None else 0.0,
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Work Activities
    # ------------------------------------------------------------------

    def get_work_activities(
        self, onetsoc_code: str, scale_id: str = "IM", limit: int = 50
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "O*NET-SOC Code",
                    "Element ID",
                    "Element Name",
                    "Scale ID",
                    "Data Value"
                FROM "ONET"."ONET_WORK_ACTIVITIES"
                WHERE "O*NET-SOC Code" = ?
                  AND "Scale ID" = ?
                ORDER BY "Data Value" DESC
            """
            cursor.execute(sql, (limit, onetsoc_code, scale_id))
            return [
                {
                    "onetsoc_code": row[0],
                    "element_id": row[1],
                    "element_name": row[2],
                    "scale_id": row[3],
                    "data_value": float(row[4]) if row[4] is not None else 0.0,
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

