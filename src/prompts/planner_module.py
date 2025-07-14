from pydantic import BaseModel

class VideoConfig(BaseModel):
    aspect_ratio: str
    number_of_videos: int
    duration_seconds: int
    negative_prompt: str
    
class RouterResponse(BaseModel):
    conversation : bool 
    video : bool
    image : bool
    
class ComplexityAnalysis(BaseModel):
    is_complex: bool
    reason: str

class ContextForGeneration(BaseModel):
    video_prompt: str | None = None
    negative_prompt: str | None = None
    audio_dialogue: str | None = None
    general_instruction: str | None = None

class MemoryStorageDecision(BaseModel):
    should_store: bool
    reason: str

class ImageConfig(BaseModel):
    prompt : str
    negative_prompt : str
    
