import aiohttp
from typing import Any, Dict, List, Optional
from .base_tool import BaseTool, ToolSchema, ToolCategory

class SearchInternalDocsTool(BaseTool):
    """Search internal hospital documents/knowledge base"""
    
    def _setup_schema(self) -> None:
        self.schema = ToolSchema(
            name="search_internal_docs",
            display_name="Search Internal Documents",
            description="Search hospital knowledge base, policies, and procedures",
            category=ToolCategory.SEARCH,
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'visiting hours', 'admission process')"
                },
                "doc_type": {
                    "type": "string",
                    "description": "Document type filter: all, policy, procedure, guideline"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)"
                }
            },
            required_params=["query"],
            return_type="array",
            examples=[
                {
                    "input": {"query": "visiting hours", "limit": 3},
                    "output": {
                        "results": [
                            {"title": "Visitor Policy", "excerpt": "Visiting hours are..."},
                            {"title": "ICU Visiting Rules", "excerpt": "ICU visitors..."}
                        ]
                    }
                }
            ]
        )
    
    async def execute(self, query: str, doc_type: str = "all", 
                     limit: int = 5, **kwargs) -> Dict[str, Any]:
        try:
            self.validate_params(query=query)
            
            # This would normally use your RAGEngine to search
            # For now, return mock data
            mock_results = [
                {
                    "id": "doc_001",
                    "title": "Visitor Policy",
                    "type": "policy",
                    "excerpt": "Visiting hours: 10:00-12:00, 16:00-18:00 daily",
                    "relevance_score": 0.95
                },
                {
                    "id": "doc_002",
                    "title": "ICU Visiting Guidelines",
                    "type": "procedure",
                    "excerpt": "ICU visitors limited to 1 per patient per visit",
                    "relevance_score": 0.87
                },
                {
                    "id": "doc_003",
                    "title": "Admission Procedures",
                    "type": "policy",
                    "excerpt": "New admissions: Check-in at Reception, complete forms...",
                    "relevance_score": 0.72
                }
            ]
            
            # Filter by doc_type if specified
            if doc_type != "all":
                mock_results = [r for r in mock_results if r["type"] == doc_type]
            
            # Limit results
            mock_results = mock_results[:limit]
            
            data = {
                "query": query,
                "results_count": len(mock_results),
                "results": mock_results,
                "search_time_ms": 125
            }
            
            return self.format_result(success=True, data=data)
        
        except Exception as e:
            return self.format_result(
                success=False,
                error=f"Search failed: {str(e)}"
            )

class WebSearchTool(BaseTool):
    """Search external web for health information"""
    
    def _setup_schema(self) -> None:
        self.schema = ToolSchema(
            name="web_search",
            display_name="Web Search",
            description="Search external web for health/medical information",
            category=ToolCategory.SEARCH,
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "source_filter": {
                    "type": "string",
                    "description": "Filter: all, medical, news, research"
                }
            },
            required_params=["query"],
            return_type="array"
        )
    
    async def execute(self, query: str, source_filter: str = "all", 
                     **kwargs) -> Dict[str, Any]:
        try:
            self.validate_params(query=query)
            
            # Mock web search results
            mock_results = [
                {
                    "title": "Health Topic Overview",
                    "url": "https://health-resource.com/info",
                    "snippet": "General information about the health topic...",
                    "source": "Medical Database",
                    "date": "2025-11-15"
                },
                {
                    "title": "Latest Medical Research",
                    "url": "https://research.journal.com/article",
                    "snippet": "Recent findings show...",
                    "source": "Medical Journal",
                    "date": "2025-11-10"
                }
            ]
            
            data = {
                "query": query,
                "results": mock_results,
                "total_results": len(mock_results)
            }
            
            return self.format_result(success=True, data=data)
        
        except Exception as e:
            return self.format_result(
                success=False,
                error=f"Web search failed: {str(e)}"
            )
