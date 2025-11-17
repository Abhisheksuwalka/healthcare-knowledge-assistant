import asyncio
import json
from typing import Any, Dict, Optional, List
from backend.tools.registry import tool_registry

class ToolExecutor:
    """Executes tools based on LLM requests"""

    def __init__(self):
        self.registry = tool_registry

    async def execute_from_llm_request(self, tool_name: str, 
                                       params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with given parameters"""
        result = await self.registry.execute_tool(tool_name, **params)
        return result

    def get_tool_schemas(self) -> List[Dict]:
        """Get schemas for binding to LLM"""
        return self.registry.get_all_schemas()

tool_executor = ToolExecutor()