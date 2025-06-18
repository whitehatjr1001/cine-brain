from langgraph.graph import MessagesState


class CineBrainState(MessagesState):
    """State class for the AI Companion workflow.

    Extends MessagesState to track conversation history and maintains the last message received.

    Attributes:
        last_message (AnyMessage): The most recent message in the conversation, can be any valid
            LangChain message type (HumanMessage, AIMessage, etc.)
        workflow (str): The current workflow the AI Companion is in. Can be "conversation", "image", or "audio".
        video_path (str): The path to the video file to be used for speech-to-text conversion.
        image_path (str): The path to the image file to be used for speech-to-text conversion.
        memory_context (str): The context of the memories to be injected into the character card.
    """

    summary: str
    workflow: str
    video_path: str
    image_path: str
    memory_context: str
