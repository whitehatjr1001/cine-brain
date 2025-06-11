import logging
from typing import Literal, Optional, Union, List
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage,ToolMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command, interrupt

from src.tool_simulator_service.agents.chat_agent.agent_factory.agent import (
    create_agent, get_llm_for_agent
)
from src.tool_simulator_service.agents.chat_agent.config.planner_module import (
    Step, Plan, StepType
)
from src.tool_simulator_service.agents.chat_agent.config.prompts import (
    apply_prompt_template
)
from src.tool_simulator_service.agents.chat_agent.tools.tools import (
    TOOLS as agent_tools
)
from src.tool_simulator_service.agents.chat_agent.config.agent_settings import (
    ChatAgentConfiguration
)
from src.tool_simulator_service.agents.chat_agent.graph.state import ChatAgentState

logger = logging.getLogger(__name__)

def get_state_attr(state: Union[dict, object], attr: str, default=None):
    """Safely extract an attribute from state or dict."""
    if isinstance(state, dict):
        return state.get(attr, default)
    return getattr(state, attr, default)


@tool
def handoff_to_planner() -> str:
    """Signal to route into planning."""
    return "handoff"


def coordinator_node(
    state: ChatAgentState | dict,
    config: RunnableConfig
) -> Command[Literal["planner", "__end__"]]:
    """
    Decide whether to handle the user query directly or hand off to the planner.
    """
    # Build prompt and invoke LLM with handoff tool
    messages: List[HumanMessage] = get_state_attr(state, 'messages', []) or []
    prompt = apply_prompt_template("coordinator", state)
    llm = get_llm_for_agent('coordinator')
    response = llm.bind_tools([handoff_to_planner]).invoke(prompt)
    logger.debug(f"Coordinator response: {response}")

    updated_messages = messages + [response]

    # Check for tool calls in the LLM response
    calls = getattr(response, 'tool_calls', []) or response.additional_kwargs.get('tool_calls', [])
    if calls:
        call = calls[0]
        if call.get('name') == 'handoff_to_planner':
            # Create proper ToolMessage instead of AIMessage with tool_call_id
            tool_response = ToolMessage(
                content=handoff_to_planner.invoke({}),
                tool_call_id=call['id']
            )
            updated_messages.append(tool_response)
            updated_messages.append(AIMessage(content="[Handing off to planner]"))
            return Command(
                update={
                    'messages': updated_messages,
                    'step': 'planner'
                },
                goto='planner'
            )

    # No handoff: respond directly
    return Command(
        update={
            'messages': updated_messages,
            'step': 'coordinator'
        },
        goto='__end__'
    )

def planner_node(
    state: ChatAgentState | dict,
    config: RunnableConfig
) -> Command[Literal["human_feedback", "team_router", "__end__"]]:
    """
    Generate a structured Plan, then request human approval.
    """
    # Load iteration count and history
    iterations = get_state_attr(state, 'plan_iterations', 0) or 0
    observations = get_state_attr(state, 'observations', []) or []

    # Load configuration
    settings = ChatAgentConfiguration.from_runnable_config(config)
    if iterations >= settings.max_plan_iterations:
        return Command(
            update={'plan_iterations': iterations},
            goto='team_router'
        )

    # Invoke planner LLM
    prompt = apply_prompt_template('planner', state)
    llm = get_llm_for_agent('planner')
    try:
        planner = llm.with_structured_output(Plan, method='json_mode')
        plan = planner.invoke(prompt)
    except Exception:
        logger.exception("Planner failed, using fallback plan")
        plan = Plan(
            incident_title='Fallback Plan',
            goal='Manual review required',
            steps=[
                Step(
                    title='Review incident',
                    description='Please review the incident and create a plan',
                    step_type=StepType.INVESTIGATION
                )
            ]
        )

    # Truncate steps if needed
    if len(plan.steps) > settings.max_step_num:
        plan.steps = plan.steps[:settings.max_step_num]

    # Update state and route to feedback
    return Command(
        update={
            'current_plan': plan,
            'plan_iterations': iterations + 1,
            'observations': observations + [f"Planned: {plan.incident_title}"],
            'step': 'human_feedback'
        },
        goto='human_feedback'
    )

def human_feedback_node(
    state: ChatAgentState | dict,
    config: RunnableConfig
) -> Command[Literal["planner", "team_router", "__end__"]]:
    """
    Pause for user to accept or edit the generated plan.
    """
    current_plan = get_state_attr(state, 'current_plan')
    if not current_plan:
        logger.error("No plan found for feedback")
        return Command(goto='__end__')

    # Get the latest messages to check for user input
    messages = get_state_attr(state, 'messages', [])
    
    # Check if we have a recent user message (after the plan was created)
    user_input = None
    if messages:
        # Look for the most recent HumanMessage
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_input = msg.content.strip().upper()
                break
    
    # If no user input yet, interrupt and wait
    if not user_input:
        # Display the current plan to the user
        plan_summary = f"""
Current Plan: {current_plan.incident_title}
Goal: {current_plan.goal}
Steps:
"""
        for i, step in enumerate(current_plan.steps, 1):
            plan_summary += f"{i}. {step.title}: {step.description}\n"
        
        plan_summary += "\nPlease review the plan. Reply with [EDIT_PLAN] or [ACCEPTED]."
        
        interrupt(plan_summary)
        return Command(
            update={'step': 'human_feedback'},
            goto='human_feedback'
        )
    
    # Process the user input
    if user_input.startswith('[EDIT_PLAN]'):
        # Extract feedback if provided after [EDIT_PLAN]
        feedback_text = user_input.replace('[EDIT_PLAN]', '').strip()
        if not feedback_text:
            feedback_text = 'Plan needs revision'
            
        return Command(
            update={
                'step': 'planner',
                'plan_approved': False,
                'plan_approval_ts': None,
                'plan_feedback': feedback_text
            },
            goto='planner'
        )
    
    elif user_input.startswith('[ACCEPTED]'):
        # Ensure the plan has an assigned team
        if not hasattr(current_plan, 'assigned_team') or not current_plan.assigned_team:
            current_plan.assigned_team = 'research'
            
        observations = get_state_attr(state, 'observations', []) or []
        
        return Command(
            update={
                'current_plan': current_plan,
                'plan_approved': True,
                'plan_approval_ts': datetime.utcnow().isoformat(),
                'plan_feedback': 'Plan approved',
                'step': 'team_router',
                'observations': observations + ['Plan approved by user']
            },
            goto='team_router'
        )
    
    else:
        # Invalid input - ask again
        interrupt("Invalid response. Please respond with [EDIT_PLAN] or [ACCEPTED].")
        return Command(
            update={
                'step': 'human_feedback',
                'plan_feedback': 'Please respond with [EDIT_PLAN] or [ACCEPTED]'
            },
            goto='human_feedback'
        )
    

def team_router_node(
    state: ChatAgentState | dict,
    config: RunnableConfig
) -> Command[Literal["research_team", "resolution_team"]]:
    """
    Route to the correct team based on current_plan.assigned_team.
    """
    plan = get_state_attr(state, 'current_plan')
    if plan is None:
        logger.error("No plan found for routing")
        return Command(
            update={
                'error': 'No plan found for routing',
                'step': '__end__'
            },
            goto='__end__'
        )

    # Get the assigned team, defaulting to 'research' if not set
    team_key = getattr(plan, 'assigned_team', 'research')
    if not team_key:
        team_key = 'research'
        logger.warning("No team assigned in plan, defaulting to research team")
    
    team_key = str(team_key).lower().strip()
    
    # Determine the target team
    if team_key == 'resolution':
        target = 'resolution_team'
    else:
        target = 'research_team'
    
    logger.info(f"Routing to {target} for team: {team_key}")
    
    return Command(
        update={
            'current_plan': plan,
            'step': target,
            'observations': get_state_attr(state, 'observations', []) + 
                         [f"Routing to {target} for plan execution"]
        },
        goto=target
    )


async def execute_team_plan_steps(
    state: ChatAgentState | dict,
    agent_name: str,
    tools: list,
    config: RunnableConfig
) -> Command[Literal["reporter"]]:
    """
    Have the research or resolver agent execute each step in current_plan.
    """
    plan = get_state_attr(state, 'current_plan', None)
    observations = get_state_attr(state, 'observations', []) or []
    if not plan or not getattr(plan, 'steps', []):
        return Command(goto='reporter')

    # Create agent once with the base prompt template
    agent = create_agent(agent_name, agent_name, tools, agent_name)
    
    # Get the first unexecuted step
    current_step = next((s for s in plan.steps if not s.execution_res), None)
    
    if not current_step:
        logger.info("All steps already executed")
        return Command(goto='reporter')
    
    try:
        logger.info(f"Executing step: {current_step.title}")
        
        # Prepare the input for the agent with completed steps info
        completed_steps = [s for s in plan.steps if s.execution_res]
        completed_steps_info = ""
        if completed_steps:
            completed_steps_info = "# Existing Research Findings\n\n"
            for i, s in enumerate(completed_steps):
                completed_steps_info += f"## Existing Finding {i + 1}: {s.title}\n\n"
                completed_steps_info += f"<finding>\n{s.execution_res}\n</finding>\n\n"
        
        # Create the input message with the current step and context
        msg = HumanMessage(
            content=f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}"
        )
        
        # Execute the agent with recursion limit
        result = await agent.ainvoke(
            {'messages': [msg]},
            config={"recursion_limit": 10}  # Set a reasonable recursion limit
        )
        
        out = result['messages'][-1].content
        current_step.execution_res = out
        observations.append(out)
        
        # Mark step as completed
        current_step.status = "completed"
        
    except Exception as e:
        logger.error(f"Error executing step {current_step.title}: {str(e)}")
        current_step.status = "failed"
        current_step.execution_res = f"Error: {str(e)}"
        observations.append(f"Failed to execute step '{current_step.title}': {str(e)}")

    return Command(
        update={'observations': observations, 'step': 'reporter'},
        goto='reporter'
    )

async def research_team_node(
    state: ChatAgentState | dict,
    config: RunnableConfig
) -> Command[Literal["reporter"]]:
    return await execute_team_plan_steps(state, 'researcher', agent_tools, config)

async def resolution_team_node(
    state: ChatAgentState | dict,
    config: RunnableConfig
) -> Command[Literal["reporter"]]:
    return await execute_team_plan_steps(state, 'resolver', agent_tools, config)


def reporter_node(
    state: ChatAgentState | dict,
    config: RunnableConfig
) -> Command[Literal["__end__"]]:
    """
    Summarize all observations into a final report.
    """
    prompt = apply_prompt_template('reporter', state)
    llm = get_llm_for_agent('reporter')
    response = llm.invoke(prompt)
    final = response.content
    return Command(update={'final_report': final}, goto='__end__')