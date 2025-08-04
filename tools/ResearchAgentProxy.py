"""
MCP Tool: ResearchAgentProxy - Calls backend Research Agent via API
"""

from .base_tool import BaseTool
from pydantic import Field
from typing import Optional, Dict, Any
import json
import httpx
import os
import asyncio


class ResearchAgentProxy(BaseTool):
    """
    Proxy tool that calls the backend Research Agent API.
    Handles research requests for content creation.
    """
    
    topic: str = Field(
        ...,
        description="The topic to research for content creation"
    )
    
    platform: Optional[str] = Field(
        default="Twitter",
        description="Target platform to optimize research for (Twitter, LinkedIn, Instagram)"
    )
    
    additional_context: Optional[str] = Field(
        default=None,
        description="Additional context or requirements for research"
    )
    
    task_id: Optional[str] = Field(
        default=None,
        description="Notion task ID for tracking"
    )

    def run(self) -> str:
        """
        Call the Research Agent API and return results.
        
        Returns:
            JSON string with research data or error
        """
        try:
            # Get backend configuration
            backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
            api_key = os.getenv("BACKEND_API_KEY", "")
            
            # Prepare request
            endpoint = f"{backend_url}/api/v1/agents/research"
            
            payload = {
                "topic": self.topic,
                "platform": self.platform,
                "max_results": 10
            }
            
            if self.additional_context:
                payload["additional_context"] = self.additional_context
            
            if self.task_id:
                payload["task_id"] = self.task_id
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Make synchronous request (Agency Swarm doesn't support async in run())
            response = httpx.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=60.0  # 60 second timeout for research
            )
            
            if response.status_code == 200:
                research_data = response.json()
                
                # Format response
                return json.dumps({
                    "status": "success",
                    "research_data": {
                        "summary": research_data.get("summary", ""),
                        "key_findings": research_data.get("key_findings", []),
                        "sources": research_data.get("sources", []),
                        "trends": research_data.get("trends", []),
                        "platform_insights": research_data.get("platform_insights", {})
                    }
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"Research API error: {response.status_code}",
                    "details": response.text
                })
                
        except httpx.TimeoutException:
            return json.dumps({
                "status": "error",
                "error": "Research request timed out. Please try again."
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"Failed to call Research Agent: {str(e)}"
            })
    
    def _format_research_summary(self, research_data: Dict[str, Any]) -> str:
        """Format research data into a readable summary."""
        summary = f"**Research Summary: {self.topic}**\n\n"
        
        # Add main summary
        if research_data.get("summary"):
            summary += f"**Overview:**\n{research_data['summary']}\n\n"
        
        # Add key findings
        if research_data.get("key_findings"):
            summary += "**Key Findings:**\n"
            for finding in research_data["key_findings"][:5]:
                summary += f"• {finding}\n"
            summary += "\n"
        
        # Add trends
        if research_data.get("trends"):
            summary += "**Current Trends:**\n"
            for trend in research_data["trends"][:3]:
                summary += f"• {trend}\n"
            summary += "\n"
        
        # Add platform-specific insights
        if research_data.get("platform_insights"):
            insights = research_data["platform_insights"].get(self.platform, {})
            if insights:
                summary += f"**{self.platform} Insights:**\n"
                if insights.get("best_practices"):
                    for practice in insights["best_practices"][:3]:
                        summary += f"• {practice}\n"
        
        return summary