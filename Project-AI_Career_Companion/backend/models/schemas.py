from pydantic import BaseModel
from typing import List, Optional

class SkillGapRequest(BaseModel):
    current_role: str
    target_role: str
    skills: List[str]
    desired_skills: List[str]

class CareerPlanRequest(BaseModel):
    current_role: str
    target_role: str
    available_trainings: List[str]

class ReviewRequest(BaseModel):
    employee_name: str
    achievements: List[str]
    challenges: List[str]
    goals: Optional[List[str]] = []

class MentorRequest(BaseModel):
    role: str
    scenario: str
