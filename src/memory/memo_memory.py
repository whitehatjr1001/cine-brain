from pydantic import BaseModel
from typing import List

class Shotermemory(BaseModel):
    """
    Short-term memory class
    """
    memory: List[str] = []


class ShortTermMemory:
    def __init__(self):
        self.memory = []

    def add_memory(self, memory):
        self.memory.append(memory)
    
    def get_memory(self):
        return Shotermemory(memory=self.memory)
    
        