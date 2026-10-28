from typing import List, Dict, Any, Optional
from database.connection import get_hana_connection

class ESCORepository:
    """Repository for ESCO taxonomy data stored in SAP HANA Cloud."""

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def find_skills(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "conceptUri",
                    "preferredLabel",
                    "skillType"
                FROM "ESCO"."ESCO_SKILLS_EN"
                WHERE LOWER("preferredLabel") LIKE LOWER(?)
                ORDER BY "preferredLabel"
            """
            cursor.execute(sql, (limit, f"%{search_term}%"))
            return [
                {"uri": row[0], "name": row[1], "type": row[2]}
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_skill(self, uri: str) -> Optional[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT "conceptUri", "preferredLabel", "skillType"
                FROM "ESCO"."ESCO_SKILLS_EN"
                WHERE "conceptUri" = ?
            """
            cursor.execute(sql, (uri,))
            row = cursor.fetchone()
            if not row:
                return None
            return {"uri": row[0], "name": row[1], "type": row[2]}
        finally:
            conn.close()

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
                    "conceptUri",
                    "preferredLabel"
                FROM "ESCO"."ESCO_OCCUPATIONS_EN"
                WHERE LOWER("preferredLabel") LIKE LOWER(?)
                ORDER BY "preferredLabel"
            """
            cursor.execute(sql, (limit, f"%{search_term}%"))
            return [{"uri": row[0], "name": row[1]} for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_occupation(self, uri: str) -> Optional[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT "conceptUri", "preferredLabel"
                FROM "ESCO"."ESCO_OCCUPATIONS_EN"
                WHERE "conceptUri" = ?
            """
            cursor.execute(sql, (uri,))
            row = cursor.fetchone()
            if not row:
                return None
            return {"uri": row[0], "name": row[1]}
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Relations (Occupation -> Skills)
    # ------------------------------------------------------------------

    def get_occupation_skills(
        self,
        occupation_uri: str,
        relation_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            if relation_type:
                sql = """
                    SELECT TOP ?
                        "skillUri",
                        "relationType",
                        "skillLabel"
                    FROM "ESCO"."ESCO_OCCUPATIONSKILLRELATIONS_EN"
                    WHERE "occupationUri" = ?
                      AND "relationType" = ?
                """
                cursor.execute(sql, (limit, occupation_uri, relation_type))
            else:
                sql = """
                    SELECT TOP ?
                        "skillUri",
                        "relationType",
                        "skillLabel"
                    FROM "ESCO"."ESCO_OCCUPATIONSKILLRELATIONS_EN"
                    WHERE "occupationUri" = ?
                """
                cursor.execute(sql, (limit, occupation_uri))

            return [
                {
                    "skill_uri": row[0],
                    "relation_type": row[1],
                    "skill_name": row[2],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Relations (Skill -> Skill)
    # ------------------------------------------------------------------

    def get_skill_relations(self, skill_uri: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "relatedSkillUri",
                    "relationType"
                FROM "ESCO"."ESCO_SKILLSKILLRELATIONS_EN"
                WHERE "originalSkillUri" = ?
            """
            cursor.execute(sql, (limit, skill_uri))
            return [
                {
                    "related_skill_uri": row[0],
                    "relation_type": row[1],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
