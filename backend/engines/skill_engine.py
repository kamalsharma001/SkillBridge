from __future__ import annotations
from typing import Dict, List, Any
from models.schemas import Skill


class SkillEngine:
    """Deterministic engine to normalize skill names and compute effective skill proficiencies."""

    @staticmethod
    def normalize_skill_name(name: str) -> str:
        """Converts skill names to standard normalized form (lowercased, whitespace trimmed)."""
        if not name:
            return ""
        name = name.strip().lower()
        # Common aliases
        aliases = {
            # Python variants
            "py": "python",
            "python3": "python",
            "python 3": "python",
            
            # Database variants
            "postgres": "postgresql",
            "postgre": "postgresql",
            "psql": "postgresql",
            "mysql": "mysql",
            "mariadb": "mariadb",
            
            # ML/AI variants
            "ml": "machine learning",
            "machine_learning": "machine learning",
            "machine-learning": "machine learning",
            "deep learning": "deep learning",
            "deep_learning": "deep learning",
            "dl": "deep learning",
            "nlp": "natural language processing",
            "natural language processing": "natural language processing",
            "computer vision": "computer vision",
            "cv": "computer vision",
            "reinforcement learning": "reinforcement learning",
            "rl": "reinforcement learning",
            
            # Framework variants
            "tf": "tensorflow",
            "torch": "pytorch",
            "sklearn": "scikit-learn",
            "scikit learn": "scikit-learn",
            "sk-learn": "scikit-learn",
            
            # Cloud/DevOps variants
            "k8s": "kubernetes",
            "kube": "kubernetes",
            "aws cloud": "aws",
            "amazon web services": "aws",
            "azure cloud": "azure",
            "gcp": "google cloud platform",
            "google cloud": "google cloud platform",
            
            # BI/Analytics variants
            "power_bi": "power bi",
            "powerbi": "power bi",
            "power bi desktop": "power bi",
            
            # JavaScript/Node variants
            "node": "node.js",
            "nodejs": "node.js",
            "express.js": "express",
            "next": "next.js",
            "nextjs": "next.js",
            "reactjs": "react",
            "vuejs": "vue",
            
            # Java variants
            "spring_boot": "spring boot",
            "springboot": "spring boot",
            "spring framework": "spring",
            
            # Data Engineering variants
            "ci/cd": "ci_cd",
            "ci-cd": "ci_cd",
            "cicd": "ci_cd",
            "continuous integration": "ci_cd",
            
            # Language variants
            "js": "javascript",
            "ts": "typescript",
            "c#": "csharp",
            "csharp": "csharp",
            "cpp": "c++",
            "c plus plus": "c++",
            
            # Data formats
            "json": "json",
            "xml": "xml",
            "yaml": "yaml",
            "yml": "yaml",
        }
        return aliases.get(name, name)

    def process_candidate_skills(self, skills: List[Dict[str, Any]]) -> List[Skill]:
        """Normalizes and computes overall proficiency for candidate skills."""
        processed: List[Skill] = []
        for s in skills:
            if isinstance(s, dict):
                skill_obj = Skill.model_validate(s)
            else:
                skill_obj = s
            skill_obj.normalized_name = self.normalize_skill_name(skill_obj.name)

            # Recency & project evidence adjustment
            base_prof = skill_obj.proficiency
            if skill_obj.project_evidence > 0:
                base_prof = min(1.0, base_prof + (0.05 * skill_obj.project_evidence))
            if skill_obj.course_completion > 0:
                base_prof = min(1.0, base_prof + (0.05 * skill_obj.course_completion))
            
            effective_prof = round(base_prof * skill_obj.recency_score, 2)
            skill_obj.proficiency = min(1.0, max(0.0, effective_prof))
            processed.append(skill_obj)
        return processed