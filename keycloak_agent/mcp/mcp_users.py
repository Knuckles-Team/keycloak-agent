"""MCP tools for users operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_users_tools(mcp: FastMCP):
    """Register Keycloak Agent users tools."""

    @mcp.tool(tags=["users"])
    async def keycloak_agent_users(
        action: str = Field(
            description="Action to perform. e.g. 'list_users', 'get_user', 'create_user', 'delete_user', 'reset_password', 'list_users_by_user_id_groups', etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent users operations (Users, Role Mappings, Client Role Mappings)."""
        if ctx:
            await ctx.info(f"Executing users operation: {action}...")
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
            return {"error": f"Unknown action '{action}' on Users client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute users operation {action}: {e}"}
