from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import json

class ToolCategory(str, Enum):
    """Categories of tools"""
    TIME = "time"
    SEARCH = "search"
    VALIDATION = "validation"
    HOSPITAL = "hospital"
    NOTIFICATION = "notification"
    MEDICAL = "medical"

class ToolSchema(BaseModel):
    """Schema definition for LLM to understand tool"""
    name: str = Field(..., description="Tool name (snake_case)")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What this tool does")
    category: ToolCategory = Field(..., description="Tool category")
    parameters: Dict[str, Any] = Field(..., description="Parameters schema")
    required_params: List[str] = Field(default_factory=list, description="Required parameters")
    return_type: str = Field(..., description="What this tool returns")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")

class BaseTool(ABC):
    """Base class for all MCP tools"""
    
    def __init__(self):
        self.schema: Optional[ToolSchema] = None
        self._setup_schema()
    
    @abstractmethod
    def _setup_schema(self) -> None:
        """Override this to define tool schema"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Override this to implement tool logic"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get schema in OpenAI function format"""
        if not self.schema:
            raise NotImplementedError("Schema not defined")
        
        return {
            "type": "function",
            "function": {
                "name": self.schema.name,
                "description": self.schema.description,
                "parameters": {
                    "type": "object",
                    "properties": self.schema.parameters,
                    "required": self.schema.required_params
                }
            }
        }
    
    def validate_params(self, **kwargs) -> bool:
        """Validate input parameters"""
        if not self.schema:
            return False
        
        for required in self.schema.required_params:
            if required not in kwargs:
                raise ValueError(f"Missing required parameter: {required}")
        return True
    
    def format_result(self, success: bool, data: Any = None, 
                     error: str = None) -> Dict[str, Any]:
        """Format tool result for LLM"""
        return {
            "success": success,
            "data": data,
            "error": error,
            "tool_name": self.schema.name if self.schema else "unknown"
        }
