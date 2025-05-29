"""Creative Project Planner Model.

Defines structured models for Research/Script Development, Pre-Production, Production, and Post-Production.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Types of steps in the CineBrain creative/research plan."""
    RESEARCH = "research"              # Fact-finding, market/genre data, inspiration
    CREATIVE = "creative"              # Brainstorming, ideation, writing, plot/dialogue
    ANALYSIS = "analysis"              # Structure, market fit, genre conventions
    VALIDATION = "validation"          # Review, critique, refinement
    DOCUMENTATION = "documentation"    # Recording decisions, findings, recommendations


class Step(BaseModel):
    """A single actionable step in the plan."""
    title: str = Field(..., description="Short title of the step.")
    description: str = Field(..., description="Detailed action or analysis required.")
    step_type: StepType = Field(..., description="Type of step (e.g. RESEARCH, SCRIPT_DEVELOPMENT, etc.)")
    suggested_tool: Optional[str] = Field(None, description="Name of the tool/agent best suited for this step.")
    execution_res: Optional[str] = Field(None, description="Result/output after executing this step.")
    status: Optional[str] = Field("pending", description="Execution status: pending, in_progress, done, skipped.")

class Plan(BaseModel):
    """A structured creative/research plan for CineBrain."""
    project_title: str = Field(..., description="Brief summary/title of the creative project or research task.")
    context_summary: Optional[str] = Field(None, description="Key context, creative background, or prior decisions.")
    goal: str = Field(..., description="Main creative or research goal for the plan.")
    has_enough_context: bool = Field(False, description="If True, no further steps needed.")
    steps: List[Step] = Field(default_factory=list, description="List of plan steps.")
    creative_insights: Optional[str] = None
    final_output: Optional[str] = None
    notes: Optional[List[str]] = Field(default_factory=list)
    assigned_team: Optional[str] = Field(None, description="Team or individual responsible for executing the plan.")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "project_title": "Short Film Script Development",
                    "context_summary": "Client wants a 10-minute drama set in a single location, with two main characters. Previous brainstorming sessions yielded a basic premise about reconciliation.",
                    "goal": "Develop a compelling short film script with strong dialogue and emotional arc.",
                    "has_enough_context": False,
                    "steps": [
                        {
                            "title": "Genre & Market Research",
                            "description": "Research trends in short film drama and festival preferences.",
                            "step_type": "research",
                            "suggested_tool": "web_search",
                            "execution_res": None,
                            "status": "pending"
                        },
                        {
                            "title": "Brainstorm Character Backstories",
                            "description": "Develop detailed backgrounds for the two main characters.",
                            "step_type": "creative",
                            "suggested_tool": null,
                            "execution_res": None,
                            "status": "pending"
                        },
                        {
                            "title": "Scene Structure Analysis",
                            "description": "Outline the three-act structure and key emotional beats.",
                            "step_type": "analysis",
                            "suggested_tool": null,
                            "execution_res": None,
                            "status": "pending"
                        },
                        {
                            "title": "Dialogue Drafting",
                            "description": "Write sample dialogue for the confrontation scene.",
                            "step_type": "creative",
                            "suggested_tool": "dialogue_generator",
                            "execution_res": None,
                            "status": "pending"
                        },
                        {
                            "title": "Script Review",
                            "description": "Review draft for pacing, tone, and clarity.",
                            "step_type": "validation",
                            "suggested_tool": null,
                            "execution_res": None,
                            "status": "pending"
                        },
                        {
                            "title": "Project Documentation",
                            "description": "Summarize key creative decisions and next steps.",
                            "step_type": "documentation",
                            "suggested_tool": null,
                            "execution_res": None,
                            "status": "pending"
                        }
                    ],
                    "creative_insights": None,
                    "final_output": None,
                    "notes": []
                }
            ]
        }