"""
MCP Server for Kea Social Media Agent
Uses agency-swarm CLI to run tools as MCP endpoints
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8081))
AUTH_TOKEN = os.getenv("APP_TOKEN", "")

# Get absolute path to tools directory
TOOLS_DIR = Path(__file__).parent.parent / "tools"

if __name__ == "__main__":
    print(f"Starting MCP Server on {HOST}:{PORT}")
    print(f"Loading tools from: {TOOLS_DIR}")
    
    # Build command
    cmd = [
        sys.executable, "-m", "agency_swarm", "mcp-server",
        "--folder", str(TOOLS_DIR),
        "--host", HOST,
        "--port", str(PORT)
    ]
    
    if AUTH_TOKEN:
        cmd.extend(["--token", AUTH_TOKEN])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run the MCP server using agency-swarm CLI
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running MCP server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)