"""Typed MCP tools for Keycloak organizations operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import CONFIRMATION_REQUIRED, drop_none


def register_organizations_tools(mcp: FastMCP):
    """Register Keycloak organizations tools."""

    @mcp.tool(
        tags={"organizations"},
        annotations={"readOnlyHint": False, "destructiveHint": False},
    )
    async def keycloak_agent_organizations_create_organizations(
        representation: dict[str, Any] = Field(
            description="The JSON representation to send as the request body."
        ),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Creates a new organization

        Calls POST /admin/realms/{realm}/organizations.
        """
        return client.create_organizations(
            **drop_none(representation=representation, realm=realm)
        )

    @mcp.tool(
        tags={"organizations"},
        annotations={"readOnlyHint": False, "destructiveHint": True},
    )
    async def keycloak_agent_organizations_delete_organizations_by_org_id(
        org_id: str = Field(description="The org id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        confirm: bool = Field(
            default=False, description="Must be true; set only after the person agrees."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Deletes the organization

        Calls DELETE /admin/realms/{realm}/organizations/{org-id}.
        """
        if not confirm:
            return CONFIRMATION_REQUIRED
        return client.delete_organizations_by_org_id(
            **drop_none(org_id=org_id, realm=realm)
        )

    @mcp.tool(
        tags={"organizations"},
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    async def keycloak_agent_organizations_get_organizations_by_org_id(
        org_id: str = Field(description="The org id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Returns the organization representation

        Calls GET /admin/realms/{realm}/organizations/{org-id}.
        """
        return client.get_organizations_by_org_id(
            **drop_none(org_id=org_id, realm=realm)
        )

    @mcp.tool(
        tags={"organizations"},
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    async def keycloak_agent_organizations_list_organizations(
        realm: str = Field(default="master", description="Realm name."),
        briefRepresentation: bool | None = Field(
            default=None, description="Query filter: briefRepresentation."
        ),
        exact: bool | None = Field(default=None, description="Query filter: exact."),
        first: int | None = Field(default=None, description="Query filter: first."),
        max: int | None = Field(default=None, description="Query filter: max."),
        q: str | None = Field(default=None, description="Query filter: q."),
        search: str | None = Field(default=None, description="Query filter: search."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Returns a paginated list of organizations filtered according to the specified parameters

        Calls GET /admin/realms/{realm}/organizations.
        """
        return client.list_organizations(
            **drop_none(
                realm=realm,
                briefRepresentation=briefRepresentation,
                exact=exact,
                first=first,
                max=max,
                q=q,
                search=search,
            )
        )
