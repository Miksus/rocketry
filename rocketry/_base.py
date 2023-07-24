from typing import TYPE_CHECKING, Any, ClassVar
from pydantic.dataclasses import dataclass, Field
from pydantic import BaseModel

if TYPE_CHECKING:
    from rocketry import Session

class RedBase:
    """Baseclass for all Rocketry classes"""
    
    # Commented this out for now as it was causing issues with the new pydantic implementation
    session: 'Session'
