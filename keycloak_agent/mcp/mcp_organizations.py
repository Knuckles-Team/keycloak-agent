"""MCP tools for organizations operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_organizations_tools(mcp: FastMCP):
    """Register Keycloak Agent organizations tools."""

    @mcp.tool(tags=["organizations"])
    async def keycloak_agent_organizations(
        action: str = Field(
            description="Action to perform. e.g. 'list_organizations', 'get_organization_by_id', 'create_organization', 'delete_organization_by_id', etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent organizations operations."""
        if ctx:
            await ctx.info(f"Executing organizations operation: {action}...")
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
            return {"error": f"Unknown action '{action}' on Organizations client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute organizations operation {action}: {e}"}
