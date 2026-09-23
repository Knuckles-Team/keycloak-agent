from typing import Literal

"""MCP tools for realms operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def register_realms_tools(mcp: FastMCP):
    """Register Keycloak Agent realms tools."""

    @mcp.tool(
        tags=["realms"],
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True,
        },
        meta={
            "eg.annotations": {"modalities_in": ["text"], "modalities_out": ["text"]}
        },
    )
    async def keycloak_agent_realms(
        action: Literal[
            "create_realm", "delete_realm", "get_realm", "list_realms"
        ] = Field(
            description="Action to perform. e.g. 'list_realms', 'get_realm', 'create_realm', 'delete_realm', etc."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Keycloak Agent realms operations."""
        if ctx:
            await ctx.info(f"Executing realms operation: {action}...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Dynamic dispatch
        method = getattr(client, action, None)
        if not method:
            alt_action = action.replace("-", "_").replace(" ", "_").lower()
            method = getattr(client, alt_action, None)

        if not method:
            return {"error": f"Unknown action '{action}' on Realms client."}

        try:
            return method(**kwargs)
        except Exception:
            return {"error": "Operation failed"}
