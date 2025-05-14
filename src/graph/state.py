from langgraph.graph import MessagesState
from typing import Optional, Any

class CineBrainState(MessagesState):
    """
    State class for CineBrain's workflow orchestration.

    Extends MessagesState to track conversation history and maintains the last message received.

    Attributes:
        last_message (Any): The most recent message in the conversation, can be any valid LangChain message type (HumanMessage, AIMessage, etc.)
        workflow (str): The current workflow CineBrain is in. Can be "conversation", "image", "audio", etc.
        audio_buffer (Optional[bytes]): The audio buffer for speech-to-text conversion.
        image_path (Optional[str]): Path to the current image asset (if any).
        current_activity (Optional[str]): The current activity or scene context.
        apply_activity (bool): Whether to apply the current activity context to the workflow.
        memory_context (Optional[str]): Contextual memory to inject into agent prompts or character cards.
    """
    last_message: Optional[Any] = None
    workflow: str 
    audio_buffer: Optional[bytes] = None
    image_path: Optional[str] = None
    current_activity: Optional[str] = None
    apply_activity: bool = False
    memory_context: Optional[str] = None