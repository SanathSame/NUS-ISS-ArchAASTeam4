from tools import singapore_time, singapore_news
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils import debug


def coordinator(state):
    """
    Select next speaker based on conversation context.
    Manages volley control and updates state accordingly.

    Updates state with:
    - next_speaker: Selected agent ID or "human"
    - volley_msg_left: Decremented counter

    Returns: Updated state
    """

    debug(state)
    volley_left = state.get("volley_msg_left", 0)
    debug(f"Volley messages left: {volley_left}", "COORDINATOR")

    if volley_left <= 0:
        debug("No volleys left, returning to human", "COORDINATOR")
        return {
            "next_speaker": "human",
            "volley_msg_left": 0
        }

    messages = state.get("messages", [])

    conversation_text = ""
    for msg in messages:
        conversation_text += f"{msg.get('content', '')}\n"

    system_prompt = """You are managing a serious ethics board discussion about capital punishment.

    Available participants:
    - victim_mother: Sarah Chen, mother of a murder victim, supports capital punishment
    - police_officer: Officer James Rodriguez, 20-year veteran police officer, believes in deterrence
    - activist: Maya Singh, human rights activist, opposes death penalty
    - criminal_mother: Lisa Thompson, mother of death row inmate, advocates for rehabilitation

    Based on the discussion flow, select who should speak next to maintain a balanced and meaningful debate.
    Consider:
    - Who hasn't spoken recently
    - Who has relevant perspective for the current point
    - Who would add depth to the ethical discussion
    - Natural flow of debate
    - Emotional dynamics and personal experiences

    Respond with ONLY the speaker ID (victim_mother, police_officer, activist, or criminal_mother).
    """

    user_prompt = f"""Recent discussion:
{conversation_text}

Who should speak next to advance this ethical discussion?"""

    debug("Analyzing discussion context...", "COORDINATOR")

    # Call LLM
    try:
        llm = ChatOpenAI(model="gpt-5-nano", temperature=1)

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        # Extract speaker from response
        if isinstance(response.content, list):
            selected_speaker = " ".join(str(item) for item in response.content).strip().lower()
        else:
            selected_speaker = str(response.content).strip().lower()
        debug(f"LLM selected: {selected_speaker}", "COORDINATOR")

        # Validate speaker
        valid_speakers = ["victim_mother", "police_officer", "activist", "criminal_mother"]
        if selected_speaker not in valid_speakers:
            # Fallback to round-robin if invalid
            import random
            selected_speaker = random.choice(valid_speakers)
            debug(f"Invalid speaker, fallback to: {selected_speaker}", "COORDINATOR")

    except Exception as e:
        # Fallback selection if LLM fails
        import random
        valid_speakers = ["victim_mother", "police_officer", "activist", "criminal_mother"]
        selected_speaker = random.choice(valid_speakers)
        debug(f"LLM error, random selection: {selected_speaker}", "COORDINATOR")

    debug(f"Final selection: {selected_speaker} (volley {volley_left} -> {volley_left - 1})", "COORDINATOR")

    return {
        "next_speaker": selected_speaker,
        "volley_msg_left": volley_left - 1
    }