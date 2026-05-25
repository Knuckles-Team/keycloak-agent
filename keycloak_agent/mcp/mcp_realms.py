"""MCP tools for realms operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_realms_tools(mcp: FastMCP):
    """Register Keycloak Agent realms tools.
    CONCEPT:KEY-001
    """

    @mcp.tool(tags={"realms"})
    async def keycloak_agent_realms(
        action: str = Field(
            description="Action to perform. Must be one of: 'list_realms', 'get_realm', 'create_realm', 'delete_realm'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent realms operations."""
        if ctx:
            await ctx.info("Executing realms operations...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "list_realms":
            return client.list_realms(**kwargs)
        if action == "get_realm":
            return client.get_realm(**kwargs)
        if action == "create_realm":
            return client.create_realm(**kwargs)
        if action == "delete_realm":
            return client.delete_realm(**kwargs)

        raise ValueError(f"Unknown action: {action}")
