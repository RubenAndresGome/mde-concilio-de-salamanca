import logging
from typing import Dict, Any, List

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    HAS_MCP = True
except ImportError:
    HAS_MCP = False

logger = logging.getLogger(__name__)


class MCPClientManager:
    def __init__(self, command: str = "npx", args: List[str] = None):
        self.command = command
        self.args = args or ["-y", "@modelcontextprotocol/server-everything"]
        self.session = None
        self._ctx = None

    async def connect(self):
        if not HAS_MCP:
            logger.warning(
                "MCP client no está instalado (pip install mcp). MCP deshabilitado."
            )
            return

        try:
            server_params = StdioServerParameters(command=self.command, args=self.args)
            self._ctx = stdio_client(server_params)
            read, write = await self._ctx.__aenter__()
            self.session = ClientSession(read, write)
            await self.session.__aenter__()
            await self.session.initialize()
            logger.info("Conectado al servidor MCP.")
        except Exception as e:
            logger.error(f"Fallo al conectar MCP: {e}")
            self.session = None

    async def disconnect(self):
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self._ctx:
            await self._ctx.__aexit__(None, None, None)

    async def list_tools(self) -> List[Dict[str, Any]]:
        if not self.session:
            return []
        try:
            tools = await self.session.list_tools()
            return [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema,
                }
                for t in tools.tools
            ]
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            return []

    async def call_tool(self, name: str, args: Dict[str, Any]) -> str:
        if not self.session:
            return "MCP Server no disponible."
        try:
            result = await self.session.call_tool(name, args)
            return str(result)
        except Exception as e:
            return f"Error ejecutando herramienta {name}: {e}"
