"""
MCP Tool: NotionTaskManager - Creates and manages tasks in Notion
"""

from agency_swarm import BaseTool
from pydantic import Field
from typing import Optional, Dict, Any
import json
import os
from notion_client import Client
from datetime import datetime
import asyncio


class NotionTaskManager(BaseTool):
    """
    Creates and updates tasks in Notion database.
    Manages the entire lifecycle of content creation tasks.
    """
    
    action: str = Field(
        ...,
        description="Action to perform: 'create', 'update', or 'get'"
    )
    
    task_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Task data for create/update operations"
    )
    
    task_id: Optional[str] = Field(
        default=None,
        description="Notion page ID for update/get operations"
    )

    def run(self) -> str:
        """
        Execute Notion operation.
        
        Returns:
            JSON string with operation result
        """
        try:
            # Initialize Notion client
            notion = Client(auth=os.getenv("NOTION_TOKEN"))
            database_id = os.getenv("NOTION_DATABASE_ID")
            
            if self.action == "create":
                return self._create_task(notion, database_id)
            elif self.action == "update":
                return self._update_task(notion)
            elif self.action == "get":
                return self._get_task(notion)
            else:
                return json.dumps({
                    "error": f"Invalid action: {self.action}",
                    "status": "error"
                })
                
        except Exception as e:
            return json.dumps({
                "error": f"Notion operation failed: {str(e)}",
                "status": "error"
            })
    
    def _create_task(self, notion: Client, database_id: str) -> str:
        """Create a new task in Notion."""
        if not self.task_data:
            return json.dumps({
                "error": "Task data required for create action",
                "status": "error"
            })
        
        # Build properties
        properties = {
            "Name": {
                "title": [{
                    "text": {"content": self.task_data.get("title", "New Content Post")}
                }]
            },
            "Status": {
                "select": {"name": "Waiting"}
            },
            "Command Used": {
                "rich_text": [{
                    "text": {"content": self.task_data.get("command", "/create-content-post")}
                }]
            },
            "Execution Mode": {
                "select": {"name": self.task_data.get("execution_mode", "Instant")}
            }
        }
        
        # Add optional fields
        if "parameters" in self.task_data:
            properties["Parameters"] = {
                "rich_text": [{
                    "text": {"content": json.dumps(self.task_data["parameters"])}
                }]
            }
        
        if "description" in self.task_data:
            properties["Task Description"] = {
                "rich_text": [{
                    "text": {"content": self.task_data["description"][:2000]}
                }]
            }
        
        if "webhook_url" in self.task_data:
            properties["Webhook URL"] = {
                "url": self.task_data["webhook_url"]
            }
        
        # Create the page
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        return json.dumps({
            "status": "success",
            "task_id": response["id"],
            "url": response.get("url", ""),
            "created_time": response.get("created_time", "")
        })
    
    def _update_task(self, notion: Client) -> str:
        """Update an existing task."""
        if not self.task_id or not self.task_data:
            return json.dumps({
                "error": "Task ID and data required for update",
                "status": "error"
            })
        
        # Build update properties
        properties = {}
        
        if "status" in self.task_data:
            properties["Status"] = {
                "select": {"name": self.task_data["status"]}
            }
        
        if "content" in self.task_data:
            properties["Content"] = {
                "rich_text": [{
                    "text": {"content": self.task_data["content"][:2000]}
                }]
            }
        
        if "research_data" in self.task_data:
            properties["Research Data"] = {
                "rich_text": [{
                    "text": {"content": json.dumps(self.task_data["research_data"])[:2000]}
                }]
            }
        
        if "error" in self.task_data:
            properties["Error"] = {
                "rich_text": [{
                    "text": {"content": self.task_data["error"][:2000]}
                }]
            }
        
        # Update the page
        response = notion.pages.update(
            page_id=self.task_id,
            properties=properties
        )
        
        return json.dumps({
            "status": "success",
            "task_id": response["id"],
            "last_edited_time": response.get("last_edited_time", "")
        })
    
    def _get_task(self, notion: Client) -> str:
        """Get task details."""
        if not self.task_id:
            return json.dumps({
                "error": "Task ID required for get action",
                "status": "error"
            })
        
        response = notion.pages.retrieve(page_id=self.task_id)
        
        # Extract properties
        props = response.get("properties", {})
        
        task_info = {
            "status": "success",
            "task_id": response["id"],
            "created_time": response.get("created_time", ""),
            "last_edited_time": response.get("last_edited_time", ""),
            "data": {
                "status": self._extract_select(props.get("Status")),
                "title": self._extract_title(props.get("Name")),
                "command": self._extract_text(props.get("Command Used")),
                "parameters": self._extract_text(props.get("Parameters")),
                "content": self._extract_text(props.get("Content")),
                "error": self._extract_text(props.get("Error"))
            }
        }
        
        return json.dumps(task_info)
    
    def _extract_title(self, prop):
        """Extract title property."""
        if prop and prop.get("title"):
            return prop["title"][0]["text"]["content"] if prop["title"] else ""
        return ""
    
    def _extract_text(self, prop):
        """Extract rich text property."""
        if prop and prop.get("rich_text"):
            return prop["rich_text"][0]["text"]["content"] if prop["rich_text"] else ""
        return ""
    
    def _extract_select(self, prop):
        """Extract select property."""
        if prop and prop.get("select"):
            return prop["select"]["name"] if prop["select"] else ""
        return ""