"""Typed MCP tools for Keycloak attack detection operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import CONFIRMATION_REQUIRED, drop_none


def register_attack_detection_tools(mcp: FastMCP):
    """Register Keycloak attack detection tools."""

    @mcp.tool(
        tags={"attack_detection"},
        annotations={"readOnlyHint": False, "destructiveHint": True},
    )
    async def keycloak_agent_attack_detection_delete_attack_detection_brute_force_users(
        realm: str = Field(default="master", description="Realm name."),
        confirm: bool = Field(
            default=False, description="Must be true; set only after the person agrees."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Clear any user login failures for all users This can release temporary disabled users

        Calls DELETE /admin/realms/{realm}/attack-detection/brute-force/users.
        """
        if not confirm:
            return CONFIRMATION_REQUIRED
        return client.delete_attack_detection_brute_force_users(
            **drop_none(realm=realm)
        )
