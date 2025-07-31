# MCP Server for Social Media Agent System

This MCP (Model Context Protocol) server provides tools for the Orchestrator agent in Agencii platform.

## Tools

1. **CommandProcessor** - Parses and validates /create-content-post commands
2. **NotionTaskManager** - Creates and manages tasks in Notion
3. **ResearchAgentProxy** - Calls backend Research Agent API
4. **CopywriterAgentProxy** - Calls backend Copywriter Agent API

## Deployment

This server is designed to run on Railway and connect to:
- Backend API for agent processing
- Notion for task management
- Agencii platform as MCP tools

## Environment Variables

- `BACKEND_API_URL` - URL of the backend API
- `BACKEND_API_KEY` - API key for backend authentication
- `NOTION_TOKEN` - Notion integration token
- `NOTION_DATABASE_ID` - Notion database ID
- `MCP_AUTH_TOKEN` - Bearer token for MCP authentication
- `PORT` - Server port (default: 8080)