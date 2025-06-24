from pydantic import BaseModel

class PlannerResponse(BaseModel):
    workflow_type: str
    goal: str
    context: dict
    memory: dict
    messages: list

class VideoConfig(BaseModel):
    aspect_ratio: str
    number_of_videos: int
    duration_seconds: int
    negative_prompt: str
    
