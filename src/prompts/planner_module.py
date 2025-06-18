from pydantic import BaseModel

class PlannerResponse(BaseModel):
    workflow_type: str
    goal: str
    context: dict
    memory: dict
    messages: list

