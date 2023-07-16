from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rocketry import Session

class RedBase:
    """Baseclass for all Rocketry classes"""
    
    # Commented this out for now as it was causing issues with the new pydantic implementation
    # session: 'Session' = None
