"""
Simple HTTP server for MCP tools
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import subprocess
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PORT = int(os.environ.get("PORT", 8080))

class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "healthy", "service": "kea-mcp-server"}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "name": "Kea MCP Server",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "sse": "/sse"
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/sse":
            # SSE endpoint for MCP
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            # Start Python MCP subprocess
            env = os.environ.copy()
            process = subprocess.Popen(
                ["python", "start_mcp.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output as SSE
            try:
                for line in process.stdout:
                    self.wfile.write(f"data: {line}\n\n".encode())
                    self.wfile.flush()
            except:
                process.kill()
                
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"{self.address_string()} - {format%args}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), MCPHandler)
    print(f"MCP Server running on port {PORT}")
    print(f"Health check: http://localhost:{PORT}/health")
    print(f"SSE endpoint: http://localhost:{PORT}/sse")
    server.serve_forever()