"""MCP tools for users operations."""
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field
from keycloak_agent.auth import get_client

def register_users_tools(mcp: FastMCP):
    """Register Keycloak Agent users tools.
    CONCEPT:KEY-001
    """
    @mcp.tool(tags={"users"})
    async def keycloak_agent_users(
        action: str = Field(description="Action to perform. Must be one of: 'list_users', 'get_user', 'create_user', 'delete_user', 'reset_password'"),
        params_json: str = Field(default="{}", description="JSON string of parameters."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent users operations."""
        if ctx:
            await ctx.info("Executing users operations...")
        import json
        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        if action == "list_users":
            return client.list_users(**kwargs)
        if action == "get_user":
            return client.get_user(**kwargs)
        if action == "create_user":
            return client.create_user(**kwargs)
        if action == "delete_user":
            return client.delete_user(**kwargs)
        if action == "reset_password":
            return client.reset_password(**kwargs)

        raise ValueError(f"Unknown action: {action}")
