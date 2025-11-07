from tools import singapore_time, singapore_news
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils import debug
import re


# Persona configurations
PERSONAS = {
    "victim_mother": {
        "name": "Sarah Chen",
        "age": 45,
        "backstory": "Lost her daughter to a violent crime 3 years ago, advocates for justice through capital punishment",
        "personality": "Determined, emotional but composed, seeking closure",
        "speech_style": "Direct, personal, emotionally charged but controlled",
        "tools": ["time", "news"]
    },
    "police_officer": {
        "name": "Officer James Rodriguez",
        "age": 48,
        "backstory": "20-year veteran police officer, has witnessed both violent crimes and executions",
        "personality": "Professional, pragmatic, believes in law and order",
        "speech_style": "Authoritative, factual, draws from experience",
        "tools": ["time", "news"]
    },
    "activist": {
        "name": "Maya Singh",
        "age": 35,
        "backstory": "Human rights activist, has worked with death row inmates and their families",
        "personality": "Passionate, articulate, deeply committed to human rights",
        "speech_style": "Eloquent, uses statistics and research, appeals to morality",
        "tools": ["time", "news"]
    },
    "criminal_mother": {
        "name": "Lisa Thompson",
        "age": 52,
        "backstory": "Mother of a death row inmate, advocates for rehabilitation over punishment",
        "personality": "Grief-stricken but hopeful, seeking understanding",
        "speech_style": "Emotional, personal, focuses on redemption and second chances",
        "tools": ["time", "news"]
    }
}


def execute_tool(tool_name):
    """
    Execute a specific tool and return its output.
    Returns Tool output as string
    """
    tool_name = tool_name.lower().strip()

    if tool_name == "time":
        return singapore_time()
    elif tool_name == "news":
        return singapore_news()
    else:
        return f"Unknown tool: {tool_name}"


def participant(persona_id, state) -> dict:
    """
    Generate speech for a persona using ReAct workflow with real tool calling.

    Args:
        persona_id: One of "victim_mother", "police_officer", "activist", "criminal_mother"
        state: Current conversation state

    Returns:
        Dict with message updates for state
    """
    if persona_id not in PERSONAS:
        return {"messages": [{"role": "assistant", "content": f"Unknown participant: {persona_id}"}]}

    persona = PERSONAS[persona_id]
    debug(f"\n=== {persona['name']} is considering... ===")

    # Get recent conversation for context
    messages = state.get("messages", [])
    conversation_text = ""
    for msg in messages:
        conversation_text += f"{msg.get('content', '')}\n"

    # Tool descriptions mapping
    tool_descriptions = {
        "time": "Returns current time in Singapore",
        "news": "Returns latest news about crime and justice in Singapore"
    }

    # Build available actions list based on persona's tools
    available_actions = ""
    for tool in persona['tools']:
        available_actions += f"\n\n{tool}:\n{tool_descriptions[tool]}"

    # System prompt for ReAct
    system_prompt = f"""You are {persona['name']}, {persona['age']} years old.
Background: {persona['backstory']}
Personality: {persona['personality']}
Speech Style: {persona['speech_style']}

You are participating in a serious ethics board discussion about capital punishment.
Consider your background and experiences when contributing to the discussion.
Stay true to your perspective while remaining respectful of others.

Available tools:{available_actions}

Approach:
1. Consider the conversation context and your role
2. Decide if you need any tools
3. Form a thoughtful response incorporating your perspective
4. IMPORTANT: Stay in character and maintain your unique viewpoint

Format your THOUGHTS, ACTIONS, and RESPONSE as:
THOUGHTS: Analyze the situation, plan your response
ACTION: [Use a tool if needed - optional]
RESPONSE: Your actual spoken contribution

Remember that this is a serious ethical discussion with real human impact."""

    user_prompt = f"""Current discussion context:
{conversation_text}

How do you contribute to this discussion about capital punishment, considering your background and perspective?"""

    try:
        llm = ChatOpenAI(model="gpt-5-nano", temperature=1)
        
        completion = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        # Parse ReAct format
        response_text = completion.content
        
        # Execute any ACTION if present
        action_match = re.search(r"ACTION: \[(.*?)\]", response_text)
        if action_match:
            tool_call = action_match.group(1).strip()
            if tool_call:
                tool_result = execute_tool(tool_call)
                response_text = response_text.replace(
                    action_match.group(0),
                    f"ACTION: [{tool_call}]\nTool result: {tool_result}"
                )

        # Extract final RESPONSE
        response_match = re.search(r"RESPONSE: (.*?)(?=\n|$)", response_text, re.DOTALL)
        if response_match:
            final_response = response_match.group(1).strip()
        else:
            final_response = f"{persona['name']}: I apologize, but I need to collect my thoughts before continuing."

        return {
            "messages": [{"role": "assistant", "content": f"{persona['name']}: {final_response}"}]
        }

    except Exception as e:
        debug(f"Error: {str(e)}", "PARTICIPANT")
        return {
            "messages": [{"role": "assistant", "content": f"{persona['name']}: I apologize, but I need a moment to gather my thoughts."}]
        }