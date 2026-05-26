"""MCP tools for authentication management operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_authentication_tools(mcp: FastMCP):
    """Register Keycloak Agent authentication tools."""

    @mcp.tool(tags=["authentication"])
    async def keycloak_agent_authentication(
        action: str = Field(
            description="Action to perform. e.g. 'list_authentication_flows', 'get_authentication_flow', 'create_authentication_flow', 'delete_authentication_flow', 'list_authenticator_providers', etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent authentication and authenticator flow operations."""
        if ctx:
            await ctx.info(f"Executing authentication operation: {action}...")
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
            return {"error": f"Unknown action '{action}' on Authentication client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {
                "error": f"Failed to execute authentication operation {action}: {e}"
            }
