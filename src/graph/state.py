from typing import List, TypedDict, Optional
from langchain_core.messages import BaseMessage
from src.prompts.planner_module import Plan  # Updated import for the new Plan model

class CineBrainState(TypedDict):
    """
    State object for CineBrain agent workflow, tracking all major creative and research steps.
    """
    messages: List[BaseMessage]
    user_query: str
    locale: str

    # Memory Extraction
    extracted_memories: Optional[str]  # Relevant past interactions/knowledge

    # Background Investigation
    background_investigation_results: Optional[str]  # Initial search results

    # Planning
    current_plan: Optional[Plan]  # The detailed plan generated by the Planner

    # Execution Results (accumulated by RCET)
    research_findings: List[dict]  # Structured research/creative data (from web, story DB, box office)
    validation_report: Optional[str]  # Structured feedback on ideas/scripts
    creative_output: Optional[str]  # Generated script segments, brainstorms, etc.
    generated_dialogue_text: Optional[str]
    generated_dialogue_audio_path: Optional[str]

    # Human Feedback
    user_feedback_log: Optional[List[str]]  # Log of user approvals, comments, or feedback
    human_feedback_status: Optional[str]    # Current feedback status (e.g., 'pending', 'approved', 'needs_changes')

    # Future extensibility for production/post-production
    production_output: Optional[str]        # For production phase outputs (e.g., shot lists, schedules)
    post_production_output: Optional[str]   # For post-production outputs (e.g., edit notes, final cut info)

    # Workflow Control
    human_feedback_needed: bool
    human_feedback_input: Optional[str]
    error_message: Optional[str]