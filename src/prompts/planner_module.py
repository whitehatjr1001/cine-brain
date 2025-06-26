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
    

class ImageConfig(BaseModel):
    prompt : str
    negative_prompt : str
    
