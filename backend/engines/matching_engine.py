from __future__ import annotations
import re
from typing import Dict, List, Any
from engines.skill_engine import SkillEngine


def calculate_effective_experience(experience_years: float, career_gaps: List[Dict[str, Any]]) -> float:
    """Calculates effective experience by restoring time spent on protected career gaps."""
    protected_months = sum(
        g.get("duration_months", 0) for g in (career_gaps or []) if g.get("protected", True)
    )
    return round(experience_years + (protected_months / 12.0), 2)


def _normalize_location(loc: str) -> List[str]:
    """Normalize location string into a list of location tokens for accurate matching."""
    if not loc:
        return []
    # Split by common delimiters and clean
    parts = re.split(r'[,;/|]', loc.lower())
    normalized = []
    for part in parts:
        part = part.strip()
        # Remove common prefixes/suffixes
        part = re.sub(r'^(location|city|state|country|remote)[:\s]*', '', part)
        part = part.strip()
        if part and len(part) > 1:
            normalized.append(part)
    return normalized


def _location_match(cand_loc: str, opp_loc: str, work_mode: str = "") -> float:
    """Determine location match score with proper token-based matching."""
    if not opp_loc or "remote" in opp_loc.lower() or "hybrid" in work_mode.lower():
        return 1.0
    
    cand_tokens = _normalize_location(cand_loc)
    opp_tokens = _normalize_location(opp_loc)
    
    if not cand_tokens or not opp_tokens:
        return 0.85  # Unknown location - moderate score
    
    # Check for exact token matches
    for c_token in cand_tokens:
        for o_token in opp_tokens:
            if c_token == o_token:
                return 1.0
            # Check if one is contained in the other (but only for longer tokens to avoid "York" matching "New York")
            if len(c_token) > 3 and len(o_token) > 3:
                if c_token in o_token or o_token in c_token:
                    return 0.95
    
    return 0.85


def _education_match(cand_edu: List[str], req_edu: List[str]) -> float:
    """Determine education match score with proper degree-level matching."""
    if not req_edu:
        return 1.0
    
    cand_edu_lower = [e.lower().strip() for e in cand_edu]
    req_edu_lower = [e.lower().strip() for e in req_edu]
    
    # Define degree hierarchy for partial matching
    degree_hierarchy = {
        "phd": 5, "doctorate": 5, "doctoral": 5,
        "master": 4, "msc": 4, "ms": 4, "ma": 4, "mba": 4, "mtech": 4, "m.tech": 4,
        "bachelor": 3, "bsc": 3, "bs": 3, "ba": 3, "btech": 3, "b.tech": 3, "be": 3, "b.e.": 3,
        "associate": 2, "diploma": 2, "certificate": 1,
    }
    
    def get_degree_level(edu_str: str) -> int:
        for degree, level in degree_hierarchy.items():
            if degree in edu_str:
                return level
        return 0
    
    # Check if candidate meets or exceeds any required education level
    max_cand_level = max((get_degree_level(e) for e in cand_edu_lower), default=0)
    
    for req in req_edu_lower:
        req_level = get_degree_level(req)
        if req_level == 0:
            # Non-standard requirement - check substring match
            if any(req in e for e in cand_edu_lower):
                return 1.0
        elif max_cand_level >= req_level:
            return 1.0
    
    # Candidate has some education but doesn't meet requirement
    if max_cand_level > 0:
        return 0.60  # Partial credit for having some degree
    
    return 0.30  # No relevant education


class MatchingEngine:
    """Deterministic engine to match candidate profile against job opportunities.
    Includes sub-scores (Skill, Experience, Education, Location), overall compatibility score,
    and transparent explainability (WHY MATCHED vs GAPS).
    Career gaps marked as protected NEVER reduce matching or readiness scores.
    """

    def __init__(self, skill_engine: SkillEngine = None):
        self.skill_engine = skill_engine or SkillEngine()

    def rank(
        self,
        candidate: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        skill_proficiency_threshold: float = 0.30,
        target_role_name: str = "",
    ) -> List[Dict[str, Any]]:
        """Ranks list of opportunity dicts against candidate profile."""
        cand_skills = set()
        raw_skills = candidate.get("skills", [])
        for s in raw_skills:
            if isinstance(s, dict):
                if float(s.get("proficiency", 0.0)) >= skill_proficiency_threshold:
                    norm = s.get("normalized_name") or self.skill_engine.normalize_skill_name(s.get("name", ""))
                    cand_skills.add(self.skill_engine.normalize_skill_name(norm))
            elif isinstance(s, str):
                cand_skills.add(self.skill_engine.normalize_skill_name(s))

        cand_exp = calculate_effective_experience(
            candidate.get("experience_years", 0.0),
            candidate.get("career_gaps", []),
        )
        cand_edu = candidate.get("education", [])
        cand_loc = candidate.get("location", "")

        ranked = []
        target_tokens = {
            token
            for token in re.split(r"[^a-z0-9]+", target_role_name.lower())
            if len(token) > 2 and token not in {"engineer", "developer", "analyst", "role"}
        }
        for opp in opportunities:
            opp_title = opp.get("title", "Unknown Role")
            opp_company = opp.get("company", "Company")
            req_skills = opp.get("required_skills", [])
            pref_skills = opp.get("preferred_skills", [])
            exp_requirements = opp.get("experience_requirements", {})
            try:
                if opp.get("experience_min") is not None:
                    req_exp = float(opp.get("experience_min"))
                elif opp.get("experience_required") is not None:
                    req_exp = float(opp.get("experience_required"))
                elif isinstance(exp_requirements, dict) and exp_requirements.get("min_years") is not None:
                    req_exp = float(exp_requirements.get("min_years"))
                else:
                    req_exp = 0.0
            except (ValueError, TypeError):
                req_exp = 0.0
            req_edu = opp.get("education_required", opp.get("education", []))
            opp_loc = opp.get("location", "")
            work_mode = opp.get("work_mode", "")

            # 1. Skill Match Calculation
            if not req_skills:
                skill_score = 1.0
                matched_skills = []
                missing_skills = []
            else:
                req_matched = [s for s in req_skills if self.skill_engine.normalize_skill_name(s) in cand_skills]
                req_missing = [s for s in req_skills if self.skill_engine.normalize_skill_name(s) not in cand_skills]
                req_score = len(req_matched) / len(req_skills)

                if req_score == 1.0:
                    skill_score = 1.0
                    matched_skills = req_matched + ([s for s in pref_skills if self.skill_engine.normalize_skill_name(s) in cand_skills])
                elif pref_skills:
                    pref_matched = [s for s in pref_skills if self.skill_engine.normalize_skill_name(s) in cand_skills]
                    pref_score = len(pref_matched) / len(pref_skills)
                    skill_score = (req_score * 0.85) + (pref_score * 0.15)
                    matched_skills = req_matched + pref_matched
                else:
                    skill_score = req_score
                    matched_skills = req_matched

                missing_skills = req_missing

            # 2. Experience Match Calculation (Using Effective Experience)
            if req_exp <= 0 or cand_exp >= req_exp:
                exp_score = 1.0
            else:
                exp_score = round(cand_exp / req_exp, 2)

            # 3. Education Match Calculation (Improved)
            edu_score = _education_match(cand_edu, req_edu)

            # 4. Location Match Calculation (Improved)
            loc_score = _location_match(cand_loc, opp_loc, work_mode)

            opp_title_tokens = set(re.split(r"[^a-z0-9]+", opp_title.lower()))
            if target_tokens:
                token_overlap = len(target_tokens.intersection(opp_title_tokens)) / len(target_tokens)
                role_score = 0.72 + (token_overlap * 0.23)
                if target_role_name.lower() in opp_title.lower():
                    role_score = 0.97
            else:
                role_score = 0.82

            # Calibrated confidence: strong matches land in the 80s, while
            # >90 is deliberately avoided for transparent recommendation UX.
            overall_score = (
                (skill_score * 0.45) +
                (exp_score * 0.20) +
                (role_score * 0.20) +
                (edu_score * 0.10) +
                (loc_score * 0.05)
            )
            display_score = int(round(overall_score * 100))
            cap = 89 if skill_score >= 0.85 and role_score >= 0.90 and exp_score >= 0.85 else 86
            display_score = max(35, min(display_score, cap))

            ranked.append({
                "title": opp_title,
                "company": opp_company,
                "compatibility_score": display_score,
                "breakdown": {
                    "skill_match": int(skill_score * 100),
                    "experience_match": int(exp_score * 100),
                    "education_match": int(edu_score * 100),
                    "location_match": int(loc_score * 100),
                    "role_alignment": int(role_score * 100),
                },
                "why_matched": matched_skills,
                "gaps": missing_skills,
            })

        # Sort by compatibility score descending
        ranked.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return ranked