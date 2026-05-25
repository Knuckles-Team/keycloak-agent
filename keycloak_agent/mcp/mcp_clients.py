"""MCP tools for clients operations."""
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field
from keycloak_agent.auth import get_client

def register_clients_tools(mcp: FastMCP):
    """Register Keycloak Agent clients tools.
    CONCEPT:KEY-001
    """
    @mcp.tool(tags={"clients"})
    async def keycloak_agent_clients(
        action: str = Field(description="Action to perform. Must be one of: 'list_clients', 'get_client', 'create_client', 'delete_client'"),
        params_json: str = Field(default="{}", description="JSON string of parameters."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent clients operations."""
        if ctx:
            await ctx.info("Executing clients operations...")
        import json
        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        if action == "list_clients":
            return client.list_clients(**kwargs)
        if action == "get_client":
            return client.get_client(**kwargs)
        if action == "create_client":
            return client.create_client(**kwargs)
        if action == "delete_client":
            return client.delete_client(**kwargs)

        raise ValueError(f"Unknown action: {action}")
