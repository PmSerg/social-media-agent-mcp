"""
MCP Server for Social Media Agent System
Deploys all Orchestrator tools as MCP endpoints
"""

from agency_swarm import run_mcp
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8080))
AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN")

# Path to tools directory
TOOLS_DIR = "./tools"

if __name__ == "__main__":
    print(f"Starting MCP Server on {HOST}:{PORT}")
    print(f"Tools directory: {TOOLS_DIR}")
    
    # Run MCP server with all tools from directory
    # This automatically converts all BaseTool classes to MCP endpoints
    run_mcp(
        tools_folder=TOOLS_DIR,
        host=HOST,
        port=PORT,
        auth_token=AUTH_TOKEN
    )