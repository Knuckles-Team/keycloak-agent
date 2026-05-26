"""MCP tools for identity providers operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_idps_tools(mcp: FastMCP):
    """Register Keycloak Agent identity providers tools."""

    @mcp.tool(tags=["idps"])
    async def keycloak_agent_idps(
        action: str = Field(
            description="Action to perform. e.g. 'list_identity_providers', 'get_identity_provider', 'create_identity_provider', 'delete_identity_provider', etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent identity providers operations."""
        if ctx:
            await ctx.info(f"Executing idps operation: {action}...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Dynamic dispatch
        method = getattr(client, action, None)
        if not method:
            alt_action = action.replace("-", "_").replace(" ", "_").lower()
            method = getattr(client, alt_action, None)

        if not method:
            return {"error": f"Unknown action '{action}' on IDPs client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute idps operation {action}: {e}"}
