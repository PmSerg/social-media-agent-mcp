"""
MCP Tool: CommandProcessor - Parses and validates commands for social media content
"""

from .base_tool import BaseTool
from pydantic import Field
import json
import re
from typing import Dict, Any, Optional


class CommandProcessor(BaseTool):
    """
    Processes /create-content-post commands and extracts parameters.
    This tool parses commands, validates inputs, and prepares data for execution.
    """
    
    raw_command: str = Field(
        ...,
        description="The raw command string from user, e.g. '/create-content-post topic:\"AI trends\" platform:Twitter'"
    )

    def run(self) -> str:
        """
        Parse and validate the command.
        
        Returns:
            JSON string with parsed command data or error message
        """
        try:
            # Validate command starts with /create-content-post
            if not self.raw_command.strip().startswith("/create-content-post"):
                return json.dumps({
                    "error": "Invalid command. Only /create-content-post is supported",
                    "status": "error"
                })
            
            # Extract parameters
            params = self._parse_parameters(self.raw_command)
            
            # Validate required parameters
            if "topic" not in params:
                return json.dumps({
                    "error": "Missing required parameter: topic",
                    "status": "error"
                })
            
            # Set defaults
            params.setdefault("platform", "Twitter")
            params.setdefault("tone", "professional")
            params.setdefault("include_hashtags", True)
            
            # Validate platform
            valid_platforms = ["Twitter", "LinkedIn", "Instagram"]
            if params["platform"] not in valid_platforms:
                return json.dumps({
                    "error": f"Invalid platform. Must be one of: {', '.join(valid_platforms)}",
                    "status": "error"
                })
            
            # Validate tone
            valid_tones = ["professional", "casual", "humorous", "educational"]
            if params["tone"] not in valid_tones:
                return json.dumps({
                    "error": f"Invalid tone. Must be one of: {', '.join(valid_tones)}",
                    "status": "error"
                })
            
            # Return parsed command
            return json.dumps({
                "status": "success",
                "command": "/create-content-post",
                "parameters": params,
                "execution_mode": "instant"
            })
            
        except Exception as e:
            return json.dumps({
                "error": f"Failed to process command: {str(e)}",
                "status": "error"
            })
    
    def _parse_parameters(self, command: str) -> Dict[str, Any]:
        """Parse command parameters from string."""
        # Remove the command prefix
        params_str = command.replace("/create-content-post", "").strip()
        
        # Parse key:value pairs
        params = {}
        
        # Match patterns like key:"value" or key:value
        pattern = r'(\w+):(?:"([^"]+)"|(\S+))'
        matches = re.findall(pattern, params_str)
        
        for key, quoted_value, unquoted_value in matches:
            value = quoted_value if quoted_value else unquoted_value
            
            # Convert string booleans
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            
            params[key] = value
        
        return params