"""Typed MCP tools for Keycloak authentication operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import CONFIRMATION_REQUIRED, drop_none


def register_authentication_tools(mcp: FastMCP):
    """Register Keycloak authentication tools."""

    @mcp.tool(
        tags={"authentication"},
        annotations={"readOnlyHint": False, "destructiveHint": False},
    )
    async def keycloak_agent_authentication_create_authentication_flows(
        representation: dict[str, Any] = Field(
            description="The JSON representation to send as the request body."
        ),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Create a new authentication flow

        Calls POST /admin/realms/{realm}/authentication/flows.
        """
        return client.create_authentication_flows(
            **drop_none(representation=representation, realm=realm)
        )

    @mcp.tool(
        tags={"authentication"},
        annotations={"readOnlyHint": False, "destructiveHint": True},
    )
    async def keycloak_agent_authentication_delete_authentication_flows_by_id(
        id: str = Field(description="The id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        confirm: bool = Field(
            default=False, description="Must be true; set only after the person agrees."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Delete an authentication flow

        Calls DELETE /admin/realms/{realm}/authentication/flows/{id}.
        """
        if not confirm:
            return CONFIRMATION_REQUIRED
        return client.delete_authentication_flows_by_id(**drop_none(id=id, realm=realm))

    @mcp.tool(
        tags={"authentication"},
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    async def keycloak_agent_authentication_get_authentication_flows_by_id(
        id: str = Field(description="The id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get authentication flow for id

        Calls GET /admin/realms/{realm}/authentication/flows/{id}.
        """
        return client.get_authentication_flows_by_id(**drop_none(id=id, realm=realm))

    @mcp.tool(
        tags={"authentication"},
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    async def keycloak_agent_authentication_list_authentication_authenticator_providers(
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get authenticator providers Returns a stream of authenticator providers.

        Calls GET /admin/realms/{realm}/authentication/authenticator-providers.
        """
        return client.list_authentication_authenticator_providers(
            **drop_none(realm=realm)
        )

    @mcp.tool(
        tags={"authentication"},
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    async def keycloak_agent_authentication_list_authentication_flows(
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get authentication flows Returns a stream of authentication flows.

        Calls GET /admin/realms/{realm}/authentication/flows.
        """
        return client.list_authentication_flows(**drop_none(realm=realm))
