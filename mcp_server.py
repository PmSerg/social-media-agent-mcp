#!/usr/bin/env python3
"""
MCP Server implementation for Agencii platform
Handles SSE protocol for tool discovery and execution
"""

import os
import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import queue
import time

PORT = int(os.environ.get("PORT", 8080))

class MCPHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
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
                "version": "1.0.0",
                "endpoints": {
                    "sse": "/sse",
                    "health": "/health"
                }
            }).encode())
            
        elif self.path.startswith("/sse"):
            self.handle_sse()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_sse(self):
        """Handle Server-Sent Events for MCP protocol"""
        # Check authorization
        auth_header = self.headers.get('Authorization')
        expected_token = os.environ.get('APP_TOKEN', 'test_token')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if token != expected_token:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
        
        # Send SSE headers
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        # Send initial connection event
        self.send_sse_event("connection", {"status": "connected"})
        
        # Send tools manifest
        tools_manifest = {
            "tools": [
                {
                    "name": "CommandProcessor",
                    "description": "Process and parse social media content creation commands",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "raw_command": {
                                "type": "string",
                                "description": "The raw command string to process"
                            }
                        },
                        "required": ["raw_command"]
                    }
                },
                {
                    "name": "NotionTaskManager",
                    "description": "Create and manage tasks in Notion database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The action to perform",
                                "enum": ["create_task", "update_task", "get_task_status"]
                            },
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            },
                            "status": {
                                "type": "string",
                                "description": "Task status"
                            },
                            "task_id": {
                                "type": "string",
                                "description": "Task ID for updates"
                            }
                        },
                        "required": ["action"]
                    }
                },
                {
                    "name": "ResearchAgentProxy",
                    "description": "Perform research on topics using the Research Agent",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The topic to research"
                            },
                            "task_id": {
                                "type": "string",
                                "description": "Associated task ID"
                            }
                        },
                        "required": ["topic"]
                    }
                },
                {
                    "name": "CopywriterAgentProxy",
                    "description": "Create content using the Copywriter Agent",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Content topic"
                            },
                            "platform": {
                                "type": "string",
                                "description": "Target platform",
                                "enum": ["linkedin", "twitter"]
                            },
                            "task_id": {
                                "type": "string",
                                "description": "Associated task ID"
                            }
                        },
                        "required": ["topic", "platform"]
                    }
                }
            ]
        }
        
        # Send tools manifest
        self.send_sse_event("tools", tools_manifest)
        
        # Keep connection alive
        try:
            while True:
                # Send heartbeat every 30 seconds
                time.sleep(30)
                self.send_sse_event("heartbeat", {"timestamp": int(time.time())})
        except:
            pass
    
    def send_sse_event(self, event_type, data):
        """Send an SSE event"""
        try:
            event_data = f"event: {event_type}\n"
            event_data += f"data: {json.dumps(data)}\n\n"
            self.wfile.write(event_data.encode())
            self.wfile.flush()
        except:
            pass
    
    def do_POST(self):
        """Handle POST requests for tool execution"""
        if self.path == "/execute":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request = json.loads(post_data)
                tool_name = request.get("tool")
                params = request.get("parameters", {})
                
                # Mock responses for testing
                if tool_name == "CommandProcessor":
                    result = {
                        "success": True,
                        "parsed": {
                            "command": "create-content-post",
                            "topic": params.get("raw_command", "").split("topic=")[1].split()[0] if "topic=" in params.get("raw_command", "") else "AI trends",
                            "platform": "linkedin"
                        }
                    }
                else:
                    result = {"success": True, "message": f"Executed {tool_name}"}
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"{self.address_string()} - {format%args}")

if __name__ == "__main__":
    print(f"Starting MCP Server on port {PORT}")
    server = HTTPServer(("0.0.0.0", PORT), MCPHandler)
    print(f"MCP Server ready at http://0.0.0.0:{PORT}")
    print(f"SSE endpoint: http://0.0.0.0:{PORT}/sse")
    server.serve_forever()