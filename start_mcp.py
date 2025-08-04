"""
MCP Server for Social Media Agent System
Simple stdio interface for MCP tools
"""

import sys
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.CommandProcessor import CommandProcessor
from tools.NotionTaskManager import NotionTaskManager
from tools.ResearchAgentProxy import ResearchAgentProxy
from tools.CopywriterAgentProxy import CopywriterAgentProxy

def handle_request(request):
    """Handle incoming MCP request"""
    method = request.get("method")
    params = request.get("params", {})
    
    # Tool mapping
    tools = {
        "CommandProcessor": CommandProcessor(),
        "NotionTaskManager": NotionTaskManager(),
        "ResearchAgentProxy": ResearchAgentProxy(),
        "CopywriterAgentProxy": CopywriterAgentProxy()
    }
    
    # List available tools
    if method == "list_tools":
        tool_list = []
        for name, tool in tools.items():
            tool_list.append({
                "name": name,
                "description": tool.__class__.__doc__ or "",
                "parameters": tool.model_json_schema() if hasattr(tool, 'model_json_schema') else {}
            })
        return {"tools": tool_list}
    
    # Execute tool
    elif method == "execute_tool":
        tool_name = params.get("tool")
        tool_params = params.get("parameters", {})
        
        if tool_name in tools:
            tool = tools[tool_name]
            try:
                result = tool.run(**tool_params)
                return {"result": result}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    return {"error": f"Unknown method: {method}"}

if __name__ == "__main__":
    # Simple stdio interface
    print("MCP Server Started", file=sys.stderr)
    
    while True:
        try:
            # Read line from stdin
            line = sys.stdin.readline()
            if not line:
                break
                
            # Parse JSON request
            request = json.loads(line)
            
            # Handle request
            response = handle_request(request)
            
            # Send response
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()