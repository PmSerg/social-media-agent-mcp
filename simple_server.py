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
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            # Send test event
            self.wfile.write(b"data: {\"status\": \"connected\"}\n\n")
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