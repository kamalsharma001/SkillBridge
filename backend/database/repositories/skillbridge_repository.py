from typing import List, Dict, Any, Optional
from database.connection import get_hana_connection

class SkillBridgeRepository:
    """Repository for SkillBridge synthetic data stored in SAP HANA Cloud."""

    # ------------------------------------------------------------------
    # Candidates
    # ------------------------------------------------------------------

    def find_candidates(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "candidate_id",
                    "name",
                    "current_role",
                    "target_role",
                    "career_level",
                    "experience_years",
                    "location",
                    "skill_proficiency"
                FROM "SKILLBRIDGE"."CANDIDATES"
            """
            cursor.execute(sql, (limit,))
            return [
                {
                    "candidate_id": row[0],
                    "name": row[1],
                    "current_role": row[2],
                    "target_role": {"name": row[3]} if row[3] else None,
                    "career_level": row[4],
                    "experience_years": row[5],
                    "location": row[6],
                    "skill_proficiency": row[7],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT
                    "candidate_id",
                    "name",
                    "current_role",
                    "target_role",
                    "career_level",
                    "experience_years",
                    "location",
                    "skill_proficiency",
                    "career_goal"
                FROM "SKILLBRIDGE"."CANDIDATES"
                WHERE "candidate_id" = ?
            """
            cursor.execute(sql, (candidate_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "candidate_id": row[0],
                "name": row[1],
                "current_role": row[2],
                "target_role": {"name": row[3]} if row[3] else None,
                "career_level": row[4],
                "experience_years": row[5],
                "location": row[6],
                "skill_proficiency": row[7],
                "career_goal": row[8],
                "skills": self.get_candidate_skills(candidate_id),
            }
        finally:
            conn.close()

    def get_candidate_skills(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Parses the denormalized skill_proficiency string into a list of skills."""
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT "skill_proficiency"
                FROM "SKILLBRIDGE"."CANDIDATES"
                WHERE "candidate_id" = ?
            """
            cursor.execute(sql, (candidate_id,))
            row = cursor.fetchone()
            if not row or not row[0]:
                return []
            
            skills = []
            skill_parts = [p.strip() for p in row[0].split(";") if p.strip()]
            for part in skill_parts:
                if ":" in part:
                    name, level = part.rsplit(":", 1)
                    try:
                        # Map 1-5 scale to 0.0-1.0 roughly
                        prof_val = float(level) / 5.0
                    except ValueError:
                        prof_val = 0.5
                else:
                    name = part
                    prof_val = 0.5
                
                skills.append({
                    "name": name.strip(),
                    "normalized_name": name.strip().lower(),
                    "proficiency": min(max(prof_val, 0.0), 1.0),
                })
            return skills
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------

    def get_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT TOP ?
                    "job_id",
                    "job_title",
                    "company_name",
                    "location",
                    "industry",
                    "experience_min",
                    "experience_max",
                    "salary_min",
                    "salary_max",
                    "job_description",
                    "required_skills"
                FROM "SKILLBRIDGE"."JOBS"
            """
            cursor.execute(sql, (limit,))
            jobs = []
            for row in cursor.fetchall():
                raw_skills = row[10]
                skills_list = [s.strip() for s in raw_skills.split(";")] if raw_skills else []
                jobs.append({
                    "job_id": row[0],
                    "title": row[1],
                    "company": row[2],
                    "location": row[3],
                    "industry": row[4],
                    "experience_requirements": {
                        "min_years": row[5],
                        "max_years": row[6],
                    },
                    "salary_range": {
                        "min": row[7],
                        "max": row[8],
                    },
                    "description": row[9],
                    "required_skills": skills_list,
                })
            return jobs
        finally:
            conn.close()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT
                    "job_id",
                    "job_title",
                    "company_name",
                    "location",
                    "industry",
                    "experience_min",
                    "experience_max",
                    "salary_min",
                    "salary_max",
                    "job_description",
                    "required_skills"
                FROM "SKILLBRIDGE"."JOBS"
                WHERE "job_id" = ?
            """
            cursor.execute(sql, (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            raw_skills = row[10]
            skills_list = [s.strip() for s in raw_skills.split(";")] if raw_skills else []
            return {
                "job_id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3],
                "industry": row[4],
                "experience_requirements": {
                    "min_years": row[5],
                    "max_years": row[6],
                },
                "salary_range": {
                    "min": row[7],
                    "max": row[8],
                },
                "description": row[9],
                "required_skills": skills_list,
            }
        finally:
            conn.close()

    def get_job_skills(self, job_id: str) -> List[Dict[str, Any]]:
        job = self.get_job(job_id)
        if not job:
            return []
        
        return [{"name": s, "importance": "high"} for s in job["required_skills"]]

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------

    def get_courses(
        self, skill_name: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        conn = get_hana_connection()
        try:
            cursor = conn.cursor()
            if skill_name:
                sql = """
                    SELECT TOP ?
                        "course_id",
                        "title",
                        "provider",
                        "level",
                        "duration_hours",
                        "skills_covered",
                        "url"
                    FROM "SKILLBRIDGE"."COURSES"
                    WHERE LOWER("skills_covered") LIKE LOWER(?)
                """
                cursor.execute(sql, (limit, f"%{skill_name}%"))
            else:
                sql = """
                    SELECT TOP ?
                        "course_id",
                        "title",
                        "provider",
                        "level",
                        "duration_hours",
                        "skills_covered",
                        "url"
                    FROM "SKILLBRIDGE"."COURSES"
                """
                cursor.execute(sql, (limit,))

            courses = []
            for row in cursor.fetchall():
                raw_skills = row[5]
                skills_list = [s.strip() for s in raw_skills.split(";")] if raw_skills else []
                courses.append({
                    "course_id": row[0],
                    "title": row[1],
                    "platform": row[2],
                    "level": row[3],
                    "duration_hours": row[4],
                    "skills": skills_list,
                    "url": row[6],
                })
            return courses
        finally:
            conn.close()

    def get_courses_for_skills(
        self, skill_names: List[str], limit: int = 50
    ) -> List[Dict[str, Any]]:
        # In a real denormalized DB, you'd use a better text search, 
        # but for this CSV import we just grab them all and filter in Python
        all_courses = self.get_courses(limit=1000)
        target_skills = {s.lower() for s in skill_names}
        
        matched_courses = []
        for c in all_courses:
            course_skills = {s.lower() for s in c["skills"]}
            if target_skills.intersection(course_skills):
                matched_courses.append(c)
                
        return matched_courses[:limit]
