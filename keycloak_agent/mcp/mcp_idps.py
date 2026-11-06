"""Typed MCP tools for Keycloak idps operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import CONFIRMATION_REQUIRED, drop_none


def register_idps_tools(mcp: FastMCP):
    """Register Keycloak idps tools."""

    @mcp.tool(
        tags={"idps"}, annotations={"readOnlyHint": False, "destructiveHint": False}
    )
    async def keycloak_agent_idps_create_identity_provider_instances(
        representation: dict[str, Any] = Field(
            description="The JSON representation to send as the request body."
        ),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Create a new identity provider

        Calls POST /admin/realms/{realm}/identity-provider/instances.
        """
        return client.create_identity_provider_instances(
            **drop_none(representation=representation, realm=realm)
        )

    @mcp.tool(
        tags={"idps"}, annotations={"readOnlyHint": False, "destructiveHint": True}
    )
    async def keycloak_agent_idps_delete_identity_provider_instances_by_alias(
        alias: str = Field(description="The alias in the path."),
        realm: str = Field(default="master", description="Realm name."),
        confirm: bool = Field(
            default=False, description="Must be true; set only after the person agrees."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Delete the identity provider

        Calls DELETE /admin/realms/{realm}/identity-provider/instances/{alias}.
        """
        if not confirm:
            return CONFIRMATION_REQUIRED
        return client.delete_identity_provider_instances_by_alias(
            **drop_none(alias=alias, realm=realm)
        )

    @mcp.tool(tags={"idps"}, annotations={"readOnlyHint": True, "idempotentHint": True})
    async def keycloak_agent_idps_get_identity_provider_instances_by_alias(
        alias: str = Field(description="The alias in the path."),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get the identity provider

        Calls GET /admin/realms/{realm}/identity-provider/instances/{alias}.
        """
        return client.get_identity_provider_instances_by_alias(
            **drop_none(alias=alias, realm=realm)
        )

    @mcp.tool(tags={"idps"}, annotations={"readOnlyHint": True, "idempotentHint": True})
    async def keycloak_agent_idps_list_identity_provider_instances(
        realm: str = Field(default="master", description="Realm name."),
        briefRepresentation: bool | None = Field(
            default=None, description="Query filter: briefRepresentation."
        ),
        capability: str | None = Field(
            default=None, description="Query filter: capability."
        ),
        first: int | None = Field(default=None, description="Query filter: first."),
        max: int | None = Field(default=None, description="Query filter: max."),
        realmOnly: bool | None = Field(
            default=None, description="Query filter: realmOnly."
        ),
        search: str | None = Field(default=None, description="Query filter: search."),
        type: str | None = Field(default=None, description="Query filter: type."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """List identity providers

        Calls GET /admin/realms/{realm}/identity-provider/instances.
        """
        return client.list_identity_provider_instances(
            **drop_none(
                realm=realm,
                briefRepresentation=briefRepresentation,
                capability=capability,
                first=first,
                max=max,
                realmOnly=realmOnly,
                search=search,
                type=type,
            )
        )
