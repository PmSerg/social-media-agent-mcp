"""
Base Tool implementation without agency_swarm dependency
"""

from pydantic import BaseModel
from typing import Any, Dict, Optional


class BaseTool(BaseModel):
    """Base class for all tools"""
    
    class Config:
        extra = "forbid"
    
    def run(self, **kwargs) -> Any:
        """Execute the tool - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement run method")
    
    @classmethod
    def get_description(cls) -> str:
        """Get tool description from docstring"""
        return cls.__doc__ or "No description available"
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get tool schema"""
        return cls.model_json_schema()