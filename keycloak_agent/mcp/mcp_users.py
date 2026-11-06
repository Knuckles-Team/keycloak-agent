"""Typed MCP tools for Keycloak users operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import drop_none


def register_users_tools(mcp: FastMCP):
    """Register Keycloak users tools."""

    @mcp.tool(
        tags={"users"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_users_list_users_by_user_id_groups(
        user_id: str = Field(description="The user id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        briefRepresentation: bool | None = Field(
            default=None, description="Query filter: briefRepresentation."
        ),
        first: int | None = Field(default=None, description="Query filter: first."),
        max: int | None = Field(default=None, description="Query filter: max."),
        search: str | None = Field(default=None, description="Query filter: search."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """List users by user id groups

        Calls GET /admin/realms/{realm}/users/{user-id}/groups.
        """
        return client.list_users_by_user_id_groups(
            **drop_none(
                user_id=user_id,
                realm=realm,
                briefRepresentation=briefRepresentation,
                first=first,
                max=max,
                search=search,
            )
        )
