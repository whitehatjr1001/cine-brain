from datetime import datetime
from typing import Any, List, Dict

# ==============================================================================
# --- CINEBRAIN LANGGRAPH NODE PROMPTS ---                                   #
# ==============================================================================

# 1. Memory Extraction Node
MEMORY_EXTRACTION_PROMPT = """
You are the Memory Specialist. Your task is to analyze the user's query and determine if it requires access to long-term memory or project context.

- User Query: "{user_query}"

Based on the user's query, decide whether long-term memory is relevant.

If the query is a follow-up, references a previous topic, or implies prior context, set `is_important` to `true` and provide a concise summary or key phrase for memory search in `formatted_memory`. **Ensure `formatted_memory` is a non-empty string if `is_important` is `true`.**

If the query is self-contained, starts a new topic, or doesn't require memory access, set `is_important` to `false` and `formatted_memory` to `null`.

Your output MUST be a JSON object with the following schema:
{{
  "is_important": boolean,
  "formatted_memory": string | null
}}
"""

# 2. Router Node
ROUTER_PROMPT = """
You are the Workflow Router. Your job is to classify the user's query into the correct workflow.

- User Query: "{messages[-1].content}"
- Memory Context: {memory_context}

Analyze the user's intent and choose one of the following workflows:
- `conversation`: For general chat, questions, or text-based creative tasks.
- `video`: For requests related to creating or generating video content.
- `audio`: For requests related to creating or generating audio content.

Respond with only the name of the chosen workflow (e.g., `video`).
"""

# 3. Context Injection Nodes
CONTEXT_INJECTION_PROMPT = """
You are the Context Injection specialist. Your role is to prepare the ground for the execution agent by summarizing all relevant information.

- Workflow: {workflow}
- User Query: "{messages[-1].content}"
- Extracted Memory: {memory_context}

Synthesize the user query and the extracted memory into a clear, actionable instruction for the `{workflow}` execution agent. Focus on the core task.
"""

# 4. Task Execution Nodes
TASK_EXECUTION_CONVERSATION_PROMPT = """
You are the CineBrain Creative Assistant. Your goal is to provide a helpful and engaging response to the user's query.

- Task: {context_injection_output} 

Fulfill the user's request based on the provided task description. Be creative, clear, and concise.
"""

TASK_EXECUTION_VIDEO_PROMPT = """
You are an expert cinematic prompt writer for a powerful text-to-video AI model. Your task is to take a user's idea and expand it into a rich, detailed, and vivid prompt that will generate a visually stunning video.

**The key elements of a great video prompt are:**
- **Subject:** The main character or object, with descriptive details (e.g., "a grizzled old sailor," not just "a man").
- **Action:** What the subject is doing, described with evocative verbs (e.g., "navigating a churning sea," not "on a boat").
- **Environment:** The setting, including foreground, background, and weather (e.g., "during a violent thunderstorm at midnight, massive waves crashing").
- **Cinematography:** Specify camera shots, angles, and movement (e.g., `wide shot`, `low-angle`, `slow dolly zoom`).
- **Lighting:** The mood and time of day (e.g., `golden hour`, `dramatic backlighting`, `moody neon glow`).
- **Overall Style:** The final aesthetic (e.g., `photorealistic`, `cinematic`, `hyper-detailed`, `4K`, `35mm film look`).

**Your Task:**
Take the user's core idea below and weave these elements together into a single, powerful paragraph. Do not write a story, just the final, enhanced prompt.

**User's Idea:** "{context_injection_output}"
"""

TASK_EXECUTION_AUDIO_PROMPT = """
You are an expert sound designer. Your task is to take a user's request and generate a detailed description for an audio generation model.

**Key elements for a great audio prompt are:**
- **Core Sound:** The main sound to generate (e.g., 'a cat purring', 'a futuristic car engine').
- **Environment:** Where the sound is located (e.g., 'in a small, quiet room', 'in a vast, echoing cave').
- **Qualities:** Adjectives describing the sound (e.g., 'low and rumbling', 'sharp and metallic', 'distant and faint').
- **Technical Style:** (e.g., 'high-fidelity', '8-bit chiptune', 'lo-fi recording').

**Your Task:**
Take the user's core idea below and expand it into a detailed prompt for the audio model.

**User's Idea:** "{context_injection_output}"
"""

# 5. Summary Node
SUMMARY_PROMPT = """
You are the Summarization Specialist. Your task is to create a concise, one-sentence summary of the latest user interaction for memory storage.

- Workflow: {workflow}
- User Query: "{messages[-1].content}"
- AI Response: "{messages[-1].content}"

Based on the query and response, create a neutral, third-person summary of the event.
Example: "The user asked for a video of a dragon, and the AI generated a cinematic prompt for it."
"""

# 6. Complexity Assessment Prompt
COMPLEXITY_ASSESSMENT_PROMPT = """
You are a query complexity assessor. Your task is to determine if a user's query is simple enough for a direct LLM response or if it requires a more complex agent (like a ReAct agent) that can utilize tools.

Consider a query complex if it:
- Requires external information (e.g., current events, specific data not in your training data).
- Involves multiple steps or sub-tasks.
- Demands logical reasoning or problem-solving beyond simple factual recall.
- Implies the use of tools (e.g., search, calculator, API calls).

Consider a query simple if it:
- Is a direct question answerable from general knowledge.
- Is a conversational utterance (greetings, small talk).
- Requires simple text generation or rephrasing.

User Query: "{user_query}"

Based on the analysis, provide a JSON object with the following schema:
{{
  "is_complex": boolean,
  "reason": string
}}
"""

# 7. Agent Summary Prompt
AGENT_SUMMARY_PROMPT = """
You are a concise summarizer. Your task is to take a detailed agent response and condense it into a brief, human-readable summary that can be presented to the user.

Agent Response: "{agent_response}"

Provide a summary that captures the main point or outcome of the agent's actions. If the agent's response is already concise, return it as is.
"""

# 8. Context Injection for Generation Prompt
CONTEXT_INJECTION_GENERATION_PROMPT = """
You are the Generation Context Creator. Your role is to analyze the user's query and any relevant memory to formulate precise instructions for video or audio generation.

User Query: "{user_query}"
Memory Context: "{memory_context}"
Selected Workflow: {workflow}

Based on the `Selected Workflow` and the provided context, generate a JSON object with the following structure:

If `Selected Workflow` is 'video', provide:
{{
  "video_prompt": "Your detailed video generation prompt here",
  "negative_prompt": "Optional negative prompt here (e.g., 'blurry, low quality')"
}}

If `Selected Workflow` is 'audio', provide:
{{
  "audio_dialogue": "The exact dialogue or sound description for audio generation"
}}

If `Selected Workflow` is 'conversation' or other, provide:
{{
  "general_instruction": "A clear, actionable instruction for the next LLM or agent"
}}

Ensure your prompts are highly descriptive, including visual or auditory details, styles, and any other relevant parameters. If no specific video/audio prompt or general instruction can be derived, provide an empty string for that field, but the overall structure must be maintained. DO NOT include any additional text outside the JSON.
"""

# 9. Memory Storage Decision Prompt
MEMORY_STORAGE_DECISION_PROMPT = """
You are the Memory Decision Maker. Your task is to analyze the conversation summary and determine if it contains important information that should be stored in long-term memory for future reference.

Conversation Summary: "{summary}"

Consider the summary important if it contains:
- Key user preferences or facts about the user.
- Important decisions or outcomes from the interaction.
- Information that could significantly influence future interactions.
- Details about generated media (e.g., video path, audio path).

If the summary should be stored, set `should_store` to `true` and provide a brief `reason`. Otherwise, set `should_store` to `false` and provide a `reason`.

Your output MUST be a JSON object with the following schema:
{{
  "should_store": boolean,
  "reason": string
}}
"""

# ==============================================================================
# --- PROMPT REGISTRY & LOADER ---                                           #
# ==============================================================================

PROMPT_REGISTRY: Dict[str, str] = {
    # Graph Nodes
    "memory_extraction": MEMORY_EXTRACTION_PROMPT,
    "router": ROUTER_PROMPT,
    "context_injection": CONTEXT_INJECTION_PROMPT,
    "summary": SUMMARY_PROMPT,

    # Task Execution Workflows
    "conversation": TASK_EXECUTION_CONVERSATION_PROMPT,
    "video": TASK_EXECUTION_VIDEO_PROMPT,
    "audio": TASK_EXECUTION_AUDIO_PROMPT,
    "complexity_assessment": COMPLEXITY_ASSESSMENT_PROMPT,
    "agent_summary": AGENT_SUMMARY_PROMPT,
    "context_injection_generation": CONTEXT_INJECTION_GENERATION_PROMPT,
    "memory_storage_decision": MEMORY_STORAGE_DECISION_PROMPT,
}

def get_prompt_template(prompt_name: str) -> str:
    """
    Retrieve a prompt template by its registered name.

    Args:
        prompt_name: The key of the prompt in PROMPT_REGISTRY.

    Returns:
        The raw prompt template string.

    Raises:
        ValueError: If the prompt_name is not found in the registry.
    """
    template = PROMPT_REGISTRY.get(prompt_name)
    if template is None:
        raise ValueError(f"Prompt '{prompt_name}' not found in PROMPT_REGISTRY.")
    return template

def apply_prompt_template(
    prompt_name: str,
    state: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    Format the selected prompt template with variables from the current state.

    Args:
        prompt_name: Name of the prompt to use (e.g., "router").
        state: Dictionary representing the current agent state.

    Returns:
        A list of message dicts, starting with the formatted system prompt.

    Raises:
        ValueError: If a required variable is missing for formatting.
    """
    template = get_prompt_template(prompt_name)
    
    # Prepare a dictionary for formatting, including the full state
    format_dict = dict(state)
    format_dict["CURRENT_TIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Use .format_map() to avoid errors on missing keys if the prompt doesn't need them
        system_prompt = template.format_map(format_dict)
    except KeyError as e:
        # This will catch genuine missing keys required by the prompt string itself
        raise ValueError(f"Missing variable {e} for prompt '{prompt_name}' formatting.")

    # The new structure assumes the prompt is the system message.
    # The state's 'messages' will be handled by the LangGraph runtime.
    return [{"role": "system", "content": system_prompt}]