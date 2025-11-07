from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class State:
    """
    Represents the conversation state.
    """
    # List of conversation messages
    messages: List[Dict[str, str]] = field(default_factory=list)
    
    # Number of volleys (exchanges) left before returning to human
    volley_msg_left: int = 0
    
    # Next speaker to take turn
    next_speaker: Optional[str] = None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get state attribute by key name.
        Supports dot notation for nested access.
        """
        if hasattr(self, key):
            return getattr(self, key)
        return default