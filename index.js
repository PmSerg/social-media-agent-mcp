const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Read mcp.json configuration
const mcpConfig = JSON.parse(fs.readFileSync(path.join(__dirname, 'mcp.json'), 'utf8'));

// Port from environment or default
const PORT = process.env.PORT || 8080;

// Create HTTP server
const server = http.createServer((req, res) => {
  // Health check endpoint
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy', service: 'kea-mcp-server' }));
    return;
  }

  // SSE endpoint for MCP tools
  if (req.url === '/sse') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });

    // Get the orchestrator tools configuration
    const serverConfig = mcpConfig.mcpServers['orchestrator-tools'];
    
    // Set up environment variables
    const env = {
      ...process.env,
      ...serverConfig.env,
      BACKEND_API_URL: process.env.BACKEND_API_URL,
      BACKEND_API_KEY: process.env.BACKEND_API_KEY,
      NOTION_TOKEN: process.env.NOTION_TOKEN,
      NOTION_DATABASE_ID: process.env.NOTION_DATABASE_ID
    };

    // Spawn Python MCP server
    const mcpProcess = spawn(serverConfig.command, serverConfig.args, {
      env: env,
      cwd: __dirname
    });

    // Forward stdout as SSE
    mcpProcess.stdout.on('data', (data) => {
      res.write(`data: ${data.toString()}\n\n`);
    });

    // Forward stderr for debugging
    mcpProcess.stderr.on('data', (data) => {
      console.error('MCP Error:', data.toString());
    });

    // Handle client disconnect
    req.on('close', () => {
      mcpProcess.kill();
    });

    // Handle process exit
    mcpProcess.on('exit', (code) => {
      res.end();
    });

    return;
  }

  // Root endpoint
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: 'Kea MCP Server',
      version: '1.0.0',
      endpoints: {
        health: '/health',
        sse: '/sse'
      }
    }));
    return;
  }

  // 404 for other endpoints
  res.writeHead(404);
  res.end('Not Found');
});

server.listen(PORT, () => {
  console.log(`MCP Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`SSE endpoint: http://localhost:${PORT}/sse`);
});