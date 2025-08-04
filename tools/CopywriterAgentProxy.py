"""
MCP Tool: CopywriterAgentProxy - Calls backend Copywriter Agent via API
"""

from .base_tool import BaseTool
from pydantic import Field
from typing import Optional, Dict, Any, List
import json
import httpx
import os


class CopywriterAgentProxy(BaseTool):
    """
    Proxy tool that calls the backend Copywriter Agent API.
    Generates optimized content based on research data.
    """
    
    research_data: Dict[str, Any] = Field(
        ...,
        description="Research data containing summary, key findings, and trends"
    )
    
    platform: str = Field(
        default="Twitter",
        description="Target platform: Twitter, LinkedIn, or Instagram"
    )
    
    tone: str = Field(
        default="professional",
        description="Content tone: professional, casual, humorous, or educational"
    )
    
    include_hashtags: bool = Field(
        default=True,
        description="Whether to include relevant hashtags"
    )
    
    additional_requirements: Optional[str] = Field(
        default=None,
        description="Any additional requirements for content generation"
    )
    
    task_id: Optional[str] = Field(
        default=None,
        description="Notion task ID for tracking"
    )

    def run(self) -> str:
        """
        Call the Copywriter Agent API and return generated content.
        
        Returns:
            JSON string with generated content or error
        """
        try:
            # Get backend configuration
            backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
            api_key = os.getenv("BACKEND_API_KEY", "")
            
            # Prepare request
            endpoint = f"{backend_url}/api/v1/agents/copywriter"
            
            payload = {
                "research_data": self.research_data,
                "platform": self.platform,
                "tone": self.tone,
                "include_hashtags": self.include_hashtags
            }
            
            if self.additional_requirements:
                payload["additional_requirements"] = self.additional_requirements
            
            if self.task_id:
                payload["task_id"] = self.task_id
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Make synchronous request
            response = httpx.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=45.0  # 45 second timeout
            )
            
            if response.status_code == 200:
                content_data = response.json()
                
                # Format response
                formatted_response = {
                    "status": "success",
                    "content": content_data.get("content", ""),
                    "hashtags": content_data.get("hashtags", []),
                    "character_count": content_data.get("character_count", 0),
                    "platform": content_data.get("platform", self.platform),
                    "metadata": {
                        "tone": content_data.get("tone", self.tone),
                        "optimized_for": content_data.get("optimized_for", self.platform),
                        "includes_cta": content_data.get("includes_cta", False)
                    }
                }
                
                # Add alternatives if available
                if content_data.get("alternatives"):
                    formatted_response["alternatives"] = content_data["alternatives"]
                
                # Add platform-specific formatting
                formatted_response["formatted_content"] = self._format_for_platform(
                    content_data.get("content", ""),
                    content_data.get("hashtags", [])
                )
                
                return json.dumps(formatted_response)
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"Copywriter API error: {response.status_code}",
                    "details": response.text
                })
                
        except httpx.TimeoutException:
            return json.dumps({
                "status": "error",
                "error": "Content generation timed out. Please try again."
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"Failed to call Copywriter Agent: {str(e)}"
            })
    
    def _format_for_platform(self, content: str, hashtags: List[str]) -> str:
        """Format content appropriately for the platform."""
        if self.platform == "Twitter":
            # Ensure content + hashtags fit in 280 characters
            hashtag_text = " ".join(f"#{tag}" for tag in hashtags) if self.include_hashtags else ""
            
            if hashtag_text:
                available_chars = 280 - len(hashtag_text) - 2  # 2 for spacing
                if len(content) > available_chars:
                    content = content[:available_chars-3] + "..."
                return f"{content}\n\n{hashtag_text}"
            else:
                if len(content) > 280:
                    content = content[:277] + "..."
                return content
        
        elif self.platform == "LinkedIn":
            # LinkedIn allows up to 1300 characters
            hashtag_text = " ".join(f"#{tag}" for tag in hashtags) if self.include_hashtags else ""
            
            if hashtag_text:
                formatted = f"{content}\n\n{hashtag_text}"
                if len(formatted) > 1300:
                    # Trim content to fit
                    available = 1300 - len(hashtag_text) - 2
                    content = content[:available-3] + "..."
                    formatted = f"{content}\n\n{hashtag_text}"
                return formatted
            else:
                if len(content) > 1300:
                    content = content[:1297] + "..."
                return content
        
        elif self.platform == "Instagram":
            # Instagram allows up to 2200 characters
            hashtag_text = " ".join(f"#{tag}" for tag in hashtags) if self.include_hashtags else ""
            
            if hashtag_text:
                formatted = f"{content}\n.\n.\n.\n{hashtag_text}"
                if len(formatted) > 2200:
                    available = 2200 - len(hashtag_text) - 8  # 8 for dots and spacing
                    content = content[:available-3] + "..."
                    formatted = f"{content}\n.\n.\n.\n{hashtag_text}"
                return formatted
            else:
                if len(content) > 2200:
                    content = content[:2197] + "..."
                return content
        
        return content