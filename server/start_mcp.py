"""
MCP Server for Kea Social Media Agent
Uses agency-swarm to run tools as MCP endpoints
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agency_swarm.integrations.mcp_server import run_mcp

# Configuration
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8081))
AUTH_TOKEN = os.getenv("APP_TOKEN")

# Tool directories - can have multiple
TOOL_DIRECTORIES = [
    "../tools",  # Main tools directory
]

if __name__ == "__main__":
    print(f"Starting MCP Server on {HOST}:{PORT}")
    print(f"Loading tools from: {TOOL_DIRECTORIES}")
    
    try:
        # Run MCP server with all tools from directories
        run_mcp(
            tools_folder=TOOL_DIRECTORIES,
            host=HOST,
            port=PORT,
            auth_token=AUTH_TOKEN,
            transport="sse"  # Use SSE transport for Agencii
        )
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        sys.exit(1)