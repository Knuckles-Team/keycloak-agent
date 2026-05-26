"""MCP tools for groups operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_groups_tools(mcp: FastMCP):
    """Register Keycloak Agent groups tools."""

    @mcp.tool(tags=["groups"])
    async def keycloak_agent_groups(
        action: str = Field(
            description="Action to perform. e.g. 'list_groups', 'get_group', 'create_group', 'delete_group', etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent groups operations."""
        if ctx:
            await ctx.info(f"Executing groups operation: {action}...")
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
            return {"error": f"Unknown action '{action}' on Groups client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute groups operation {action}: {e}"}
