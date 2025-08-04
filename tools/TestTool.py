"""
Test Tool for MCP Server
"""

from agency_swarm import BaseTool
from pydantic import Field


class TestTool(BaseTool):
    """
    A simple test tool to verify MCP server is working
    """
    
    message: str = Field(
        ...,
        description="Test message to echo back"
    )
    
    def run(self) -> str:
        """
        Echo the message back with confirmation
        """
        return f"Test successful! You said: {self.message}"