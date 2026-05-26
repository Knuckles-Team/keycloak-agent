"""MCP tools for attack detection operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_attack_detection_tools(mcp: FastMCP):
    """Register Keycloak Agent attack detection tools."""

    @mcp.tool(tags=["attack_detection"])
    async def keycloak_agent_attack_detection(
        action: str = Field(
            description="Action to perform. e.g. 'get_attack_detection_brute_force_users_by_userId', 'delete_attack_detection_brute_force_users', 'delete_attack_detection_brute_force_users_by_userId', etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent brute force and attack detection operations."""
        if ctx:
            await ctx.info(f"Executing attack detection operation: {action}...")
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
            return {"error": f"Unknown action '{action}' on Attack Detection client."}

        try:
            return method(**kwargs)
        except Exception as e:
            return {
                "error": f"Failed to execute attack detection operation {action}: {e}"
            }
