"""
User Context Module
Provides a way to pass user information to skills and tools.
"""
from dataclasses import dataclass
from typing import Optional
import streamlit as st

@dataclass
class UserContext:
    """Holds the current user's context for skill execution."""
    user_id: int
    username: str
    email: Optional[str] = None
    
    @classmethod
    def from_session(cls) -> Optional["UserContext"]:
        """
        Creates a UserContext from Streamlit session state.
        Returns None if user is not logged in.
        """
        if "user" in st.session_state:
            user = st.session_state["user"]
            return cls(
                user_id=user.get("id"),
                username=user.get("username"),
                email=user.get("email")
            )
        return None

# Global context holder (set before invoking agent)
_current_user_context: Optional[UserContext] = None

def set_user_context(ctx: Optional[UserContext]):
    """Set the current user context globally."""
    global _current_user_context
    _current_user_context = ctx

def get_user_context() -> Optional[UserContext]:
    """Get the current user context."""
    return _current_user_context

def get_current_user_id() -> Optional[int]:
    """Convenience function to get current user ID."""
    ctx = get_user_context()
    return ctx.user_id if ctx else None
