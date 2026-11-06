"""Typed MCP tools for Keycloak groups operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import CONFIRMATION_REQUIRED, drop_none


def register_groups_tools(mcp: FastMCP):
    """Register Keycloak groups tools."""

    @mcp.tool(
        tags={"groups"}, annotations={"readOnlyHint": False, "destructiveHint": False}
    )
    async def keycloak_agent_groups_create_groups(
        representation: dict[str, Any] = Field(
            description="The JSON representation to send as the request body."
        ),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """create or add a top level realm groupSet or create child.

        Calls POST /admin/realms/{realm}/groups.
        """
        return client.create_groups(
            **drop_none(representation=representation, realm=realm)
        )

    @mcp.tool(
        tags={"groups"}, annotations={"readOnlyHint": False, "destructiveHint": True}
    )
    async def keycloak_agent_groups_delete_groups_by_group_id(
        group_id: str = Field(description="The group id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        confirm: bool = Field(
            default=False, description="Must be true; set only after the person agrees."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Delete groups by group id

        Calls DELETE /admin/realms/{realm}/groups/{group-id}.
        """
        if not confirm:
            return CONFIRMATION_REQUIRED
        return client.delete_groups_by_group_id(
            **drop_none(group_id=group_id, realm=realm)
        )

    @mcp.tool(
        tags={"groups"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_groups_get_groups_by_group_id(
        group_id: str = Field(description="The group id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get groups by group id

        Calls GET /admin/realms/{realm}/groups/{group-id}.
        """
        return client.get_groups_by_group_id(
            **drop_none(group_id=group_id, realm=realm)
        )

    @mcp.tool(
        tags={"groups"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_groups_list_groups(
        realm: str = Field(default="master", description="Realm name."),
        briefRepresentation: bool | None = Field(
            default=None, description="Query filter: briefRepresentation."
        ),
        exact: bool | None = Field(default=None, description="Query filter: exact."),
        first: int | None = Field(default=None, description="Query filter: first."),
        max: int | None = Field(default=None, description="Query filter: max."),
        populateHierarchy: bool | None = Field(
            default=None, description="Query filter: populateHierarchy."
        ),
        q: str | None = Field(default=None, description="Query filter: q."),
        search: str | None = Field(default=None, description="Query filter: search."),
        subGroupsCount: bool | None = Field(
            default=None, description="Query filter: subGroupsCount."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get group hierarchy.  Only `name` and `id` are returned.  `subGroups` are only returned when using the `search` or `q` parameter. If none of these parameters is provided, the top-level groups are returned without `subGroups` being filled.

        Calls GET /admin/realms/{realm}/groups.
        """
        return client.list_groups(
            **drop_none(
                realm=realm,
                briefRepresentation=briefRepresentation,
                exact=exact,
                first=first,
                max=max,
                populateHierarchy=populateHierarchy,
                q=q,
                search=search,
                subGroupsCount=subGroupsCount,
            )
        )
