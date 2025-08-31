from pydantic import BaseModel, Field
from typing import Optional

class UserPreference(BaseModel):
    """User preferences for research configuration"""
    name: str = Field(default="Mehdi", description="The name of the user")
    max_urls: int = Field(default=1, description="The maximum number of urls to search for")

class UserQuestioning(BaseModel):
    """Model for requirements gathering questions"""
    question: str = Field(default="", description="The question to ask the user")
    question_number: int = Field(default=0, description="The number of the question")
    requirements_confirmed: bool = Field(default=False, description="If the user agrees to the requirements, set this to true")
    max_questions_reached: bool = Field(default=False, description="If the user has reached the maximum number of questions, set this to true")
    requirements_summary: str = Field(default="", description="A summary of the requirements")

class ResearchPlan(BaseModel):
    """Model for research planning output"""
    research_plan: str = Field(default="", description="The research plan")

class GuardrailOutput(BaseModel):
    """Model for guardrail validation output"""
    output_info: str
    tripwire_triggered: bool
