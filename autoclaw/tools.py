"""
AutoClaw - Autonomous AI Agent Platform
Tool Manager

Manages all available tools and provides a unified interface for tool execution.
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path


class ToolManager:
    """
    Central manager for all tools/skills.
    
    Provides:
    - Tool registration
    - Tool execution
    - Tool discovery
    - Parameter validation
    """
    
    def __init__(self):
        self.tools = {}
        self.tool_metadata = {}
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register all built-in tools."""
        # Import tool implementations
        from skills.browser_automation import BrowserAutomation
        from skills.file_manager import FileManager
        from skills.content_creator import ContentCreator
        from skills.system_control import SystemControl
        from skills.data_analyzer import DataAnalyzer
        from skills.messenger import Messenger
        from skills.search import WebSearch
        
        # Instantiate and register each tool
        self.register_tool("browser", BrowserAutomation(), {
            "name": "Browser Automation",
            "description": "Control web browser using Chromium CDP (AutoGLM equivalent)",
            "capabilities": [
                "Navigate to URLs",
                "Fill forms and click buttons",
                "Extract structured data",
                "Login with saved credentials",
                "Take screenshots"
            ]
        })
        
        self.register_tool("file", FileManager(), {
            "name": "File Manager",
            "description": "Read, write, organize, and monitor files",
            "capabilities": [
                "Read/write files",
                "Create/delete directories",
                "Search files by content",
                "Monitor file changes",
                "Archive/compress files"
            ]
        })
        
        self.register_tool("content", ContentCreator(), {
            "name": "Content Creator",
            "description": "Generate reports, images, social media posts",
            "capabilities": [
                "Write articles and reports",
                "Generate social media content",
                "Create presentations",
                "Generate images (with DALL-E integration)",
                "Format documents"
            ]
        })
        
        self.register_tool("system", SystemControl(), {
            "name": "System Control",
            "description": "Launch apps, execute commands, take screenshots",
            "capabilities": [
                "Launch applications",
                "Execute system commands",
                "Take screenshots",
                "Monitor system resources",
                "Control keyboard/mouse"
            ]
        })
        
        self.register_tool("data", DataAnalyzer(), {
            "name": "Data Analyzer",
            "description": "Read and analyze CSV, JSON, create visualizations",
            "capabilities": [
                "Parse CSV/JSON/Excel files",
                "Statistical analysis",
                "Create charts and graphs",
                "Data transformation",
                "Export analysis results"
            ]
        })
        
        self.register_tool("messenger", Messenger(), {
            "name": "Messenger",
            "description": "Send messages via Feishu, Slack, Telegram, Webhooks",
            "capabilities": [
                "Send Feishu messages",
                "Send Slack messages",
                "Send Telegram messages",
                "Post to webhooks",
                "Receive incoming messages"
            ]
        })
        
        self.register_tool("search", WebSearch(), {
            "name": "Web Search",
            "description": "Search the web using Google, Bing, or custom APIs",
            "capabilities": [
                "Google search",
                "Bing search",
                "Custom search API",
                "Extract search results",
                "Filter by date/type"
            ]
        })
    
    def register_tool(self, name: str, tool_instance: Any, metadata: Dict):
        """
        Register a new tool.
        
        Args:
            name: Tool identifier
            tool_instance: Tool object with async methods
            metadata: Tool description and capabilities
        """
        self.tools[name] = tool_instance
        self.tool_metadata[name] = metadata
    
    def get_tool_descriptions(self) -> List[Dict]:
        """Get descriptions of all available tools."""
        descriptions = []
        for name, metadata in self.tool_metadata.items():
            descriptions.append({
                "name": name,
                "metadata": metadata
            })
        return descriptions
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    async def execute_tool(self, tool_name: str, parameters: Dict) -> Any:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Result of tool execution
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools[tool_name]
        
        # Determine the action from parameters
        action = parameters.pop("action", "execute")
        
        # Execute the appropriate method
        method_name = f"{action}"
        if hasattr(tool, method_name):
            method = getattr(tool, method_name)
            if asyncio.iscoroutinefunction(method):
                return await method(**parameters)
            else:
                return method(**parameters)
        
        # Fallback: try generic execute
        if hasattr(tool, "execute"):
            if asyncio.iscoroutinefunction(tool.execute):
                return await tool.execute(action, **parameters)
            else:
                return tool.execute(action, **parameters)
        
        raise ValueError(f"Tool {tool_name} has no method '{method_name}'")
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get detailed information about a tool."""
        if tool_name not in self.tool_metadata:
            return None
        
        info = self.tool_metadata[tool_name].copy()
        tool = self.tools.get(tool_name)
        
        # Get available methods
        if tool:
            methods = [m for m in dir(tool) if not m.startswith("_") and callable(getattr(tool, m))]
            info["methods"] = methods
        
        return info
