"""MCP tools for clients operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_clients_tools(mcp: FastMCP):
    """Register Keycloak Agent clients tools."""

    @mcp.tool(tags=["clients"])
    async def keycloak_agent_clients(
        action: str = Field(
            description="Action to perform. e.g. 'list_clients', 'get_client', 'create_client', 'delete_client', 'get_client_secret', 'regenerate_client_secret' (by client_uuid), 'regenerate_client_secret_by_client_id' (by clientId), etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent clients operations."""
        if ctx:
            await ctx.info(f"Executing clients operation: {action}...")
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
            return {"error": f"Unknown action '{action}' on Clients client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": f"Failed to execute clients operation {action}: {e}"}
