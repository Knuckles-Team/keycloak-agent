"""Typed MCP tools for Keycloak roles operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import CONFIRMATION_REQUIRED, drop_none


def register_roles_tools(mcp: FastMCP):
    """Register Keycloak roles tools."""

    @mcp.tool(
        tags={"roles"}, annotations={"readOnlyHint": False, "destructiveHint": False}
    )
    async def keycloak_agent_roles_create_roles(
        representation: dict[str, Any] = Field(
            description="The JSON representation to send as the request body."
        ),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Create a new role for the realm or client

        Calls POST /admin/realms/{realm}/roles.
        """
        return client.create_roles(
            **drop_none(representation=representation, realm=realm)
        )

    @mcp.tool(
        tags={"roles"}, annotations={"readOnlyHint": False, "destructiveHint": True}
    )
    async def keycloak_agent_roles_delete_roles_by_role_name(
        role_name: str = Field(description="The role name in the path."),
        realm: str = Field(default="master", description="Realm name."),
        confirm: bool = Field(
            default=False, description="Must be true; set only after the person agrees."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Delete a role by name

        Calls DELETE /admin/realms/{realm}/roles/{role-name}.
        """
        if not confirm:
            return CONFIRMATION_REQUIRED
        return client.delete_roles_by_role_name(
            **drop_none(role_name=role_name, realm=realm)
        )

    @mcp.tool(
        tags={"roles"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_roles_get_roles_by_id_by_role_id(
        role_id: str = Field(description="The role id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get a specific role's representation

        Calls GET /admin/realms/{realm}/roles-by-id/{role-id}.
        """
        return client.get_roles_by_id_by_role_id(
            **drop_none(role_id=role_id, realm=realm)
        )

    @mcp.tool(
        tags={"roles"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_roles_get_roles_by_role_name(
        role_name: str = Field(description="The role name in the path."),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get a role by name

        Calls GET /admin/realms/{realm}/roles/{role-name}.
        """
        return client.get_roles_by_role_name(
            **drop_none(role_name=role_name, realm=realm)
        )

    @mcp.tool(
        tags={"roles"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_roles_list_roles(
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
        """Get all roles for the realm or client

        Calls GET /admin/realms/{realm}/roles.
        """
        return client.list_roles(
            **drop_none(
                realm=realm,
                briefRepresentation=briefRepresentation,
                first=first,
                max=max,
                search=search,
            )
        )
