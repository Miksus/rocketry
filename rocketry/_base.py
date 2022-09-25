from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rocketry import Session

class RedBase:
    """Baseclass for all Rocketry classes"""
    session: 'Session' = None
