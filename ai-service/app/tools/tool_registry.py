from app.tools.base_tool import BaseTool


class ToolRegistry:
    def __init__(self, tools: list[BaseTool]):
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> BaseTool:
        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools
