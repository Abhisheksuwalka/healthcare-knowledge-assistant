from typing import Dict, List, Optional
from .base_tool import BaseTool
from .time_tools import GetCurrentDateTimeTool, CalculateAgeTool, GetWorkingHoursTool
from .search_tools import SearchInternalDocsTool, WebSearchTool

class ToolRegistry:
    """Registry and management of all available tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_tools()
    
    def _initialize_tools(self) -> None:
        """Initialize all available tools"""
        self.register_tool(GetCurrentDateTimeTool())
        self.register_tool(CalculateAgeTool())
        self.register_tool(GetWorkingHoursTool())
        self.register_tool(SearchInternalDocsTool())
        self.register_tool(WebSearchTool())
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool"""
        if tool.schema:
            self.tools[tool.schema.name] = tool
            print(f"✓ Registered tool: {tool.schema.display_name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self.tools.get(tool_name)
    
    def get_all_schemas(self) -> List[Dict]:
        """Get all tool schemas for LLM"""
        return [tool.get_schema() for tool in self.tools.values()]
    
    def get_tool_names(self) -> List[str]:
        """Get list of all tool names"""
        return list(self.tools.keys())
    
    async def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        return await tool.execute(**kwargs)

# Global registry instance
tool_registry = ToolRegistry()
