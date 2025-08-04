#!/usr/bin/env python3
"""
Ultra-simple MCP server for Railway
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8080))

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "name": "Kea MCP Server",
                "endpoints": ["/health", "/sse"]
            }).encode())
        elif self.path == "/sse":
            # Check authorization
            auth_header = self.headers.get('Authorization')
            expected_token = os.environ.get('APP_TOKEN', 'test_token')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                if token != expected_token:
                    self.send_response(401)
                    self.end_headers()
                    return
            
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            # Send MCP tools list
            tools_response = {
                "tools": [
                    {
                        "name": "CommandProcessor",
                        "description": "Process social media content creation commands",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "raw_command": {
                                    "type": "string",
                                    "description": "The command to process"
                                }
                            },
                            "required": ["raw_command"]
                        }
                    },
                    {
                        "name": "NotionTaskManager",
                        "description": "Manage tasks in Notion database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["create_task", "update_task", "get_task_status"]
                                },
                                "title": {"type": "string"},
                                "status": {"type": "string"},
                                "task_id": {"type": "string"}
                            },
                            "required": ["action"]
                        }
                    }
                ]
            }
            
            # Send as SSE event
            self.wfile.write(f"data: {json.dumps(tools_response)}\n\n".encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format%args}")

if __name__ == "__main__":
    print(f"Starting server on port {PORT}")
    server = HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    print(f"Server ready at http://0.0.0.0:{PORT}")
    server.serve_forever()