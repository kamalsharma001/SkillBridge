from typing import Any, Dict, List
from pydantic import BaseModel, Field

class SkillAgentContext(BaseModel):
    candidate: Dict[str, Any] = Field(default_factory=dict)
    target_role: Dict[str, Any] = Field(default_factory=dict)

class CareerAgentContext(BaseModel):
    candidate: Dict[str, Any] = Field(default_factory=dict)
    target_role: Dict[str, Any] = Field(default_factory=dict)
    jobs: List[Dict[str, Any]] = Field(default_factory=list)

class IndustryAgentContext(BaseModel):
    jobs: List[Dict[str, Any]] = Field(default_factory=list)

class LearningAgentContext(BaseModel):
    skill_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    courses: List[Dict[str, Any]] = Field(default_factory=list)
    target_role: Dict[str, Any] = Field(default_factory=dict)

class OpportunityAgentContext(BaseModel):
    candidate: Dict[str, Any] = Field(default_factory=dict)
    opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    target_role: Dict[str, Any] = Field(default_factory=dict)

class ProfileAgentContext(BaseModel):
    candidate: Dict[str, Any] = Field(default_factory=dict)
    target_role: Dict[str, Any] = Field(default_factory=dict)
    skill_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_courses: List[Dict[str, Any]] = Field(default_factory=list)
