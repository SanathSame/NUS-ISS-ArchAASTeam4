from typing import Union
from state import State
from utils import debug


def human_node(state: State) -> State:
    """
    Get input from human user.
    Set next_speaker and volley_msg_left for the response chain.
    """
    try:
        # Get user input
        user_input = input("\nYour contribution to the discussion: ")
        
        # Check for exit
        if user_input.lower().strip() == "exit":
            return state

        # Add message to state
        state.messages.append({"role": "user", "content": user_input})
        
        # Set up response chain
        state.volley_msg_left = 3  # Allow 3 responses before returning to human
        state.next_speaker = None  # Let coordinator choose first speaker
        
        return state

    except Exception as e:
        debug(f"Error in human node: {str(e)}")
        return state


def check_exit_condition(state: State) -> Union[str, None]:
    """
    Check if we should exit or continue the conversation.
    Returns 'summarizer' or 'coordinator'
    """
    messages = state.get("messages", [])
    
    if not messages:
        return "coordinator"
        
    last_message = messages[-1].get("content", "").lower().strip()
    
    if last_message == "exit":
        return "summarizer"
    
    return "coordinator"


def coordinator_routing(state: State) -> str:
    """Route to next node based on coordinator output."""
    next_speaker = state.get("next_speaker")
    
    if next_speaker == "human":
        return "human"
    
    return "participant"


def participant_node(state: State) -> State:
    """
    Run the participant agent for the selected speaker.
    """
    from agents.participant import participant
    
    try:
        next_speaker = state.get("next_speaker")
        if not next_speaker:
            debug("No next speaker selected!")
            return state
            
        # Get participant response
        updates = participant(next_speaker, state)
        
        # Update messages
        if "messages" in updates:
            state.messages.extend(updates["messages"])
            
        return state
        
    except Exception as e:
        debug(f"Error in participant node: {str(e)}")
        return state


def summarizer_node(state: State) -> State:
    """
    Summarize the discussion when exiting.
    """
    try:
        print("\n=== Discussion Summary ===")
        print("A thoughtful ethics board discussion on capital punishment was held.")
        print("Key participants included:")
        print("- Sarah Chen (victim's mother)")
        print("- Officer James Rodriguez (police veteran)")
        print("- Maya Singh (human rights activist)") 
        print("- Lisa Thompson (mother of death row inmate)")
        print("\nThe discussion explored various perspectives on justice,")
        print("deterrence, human rights, and the impact on families.")
        print("\nThank you for participating in this important dialogue.")
        
        return state
        
    except Exception as e:
        debug(f"Error in summarizer: {str(e)}")
        return state