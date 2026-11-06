"""Typed MCP tools for Keycloak components operations (one tool per operation)."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.mcp._guard import CONFIRMATION_REQUIRED, drop_none


def register_components_tools(mcp: FastMCP):
    """Register Keycloak components tools."""

    @mcp.tool(
        tags={"components"},
        annotations={"readOnlyHint": False, "destructiveHint": False},
    )
    async def keycloak_agent_components_create_components(
        representation: dict[str, Any] = Field(
            description="The JSON representation to send as the request body."
        ),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Create components

        Calls POST /admin/realms/{realm}/components.
        """
        return client.create_components(
            **drop_none(representation=representation, realm=realm)
        )

    @mcp.tool(
        tags={"components"},
        annotations={"readOnlyHint": False, "destructiveHint": True},
    )
    async def keycloak_agent_components_delete_components_by_id(
        id: str = Field(description="The id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        confirm: bool = Field(
            default=False, description="Must be true; set only after the person agrees."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Delete components by id

        Calls DELETE /admin/realms/{realm}/components/{id}.
        """
        if not confirm:
            return CONFIRMATION_REQUIRED
        return client.delete_components_by_id(**drop_none(id=id, realm=realm))

    @mcp.tool(
        tags={"components"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_components_get_components_by_id(
        id: str = Field(description="The id in the path."),
        realm: str = Field(default="master", description="Realm name."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Get components by id

        Calls GET /admin/realms/{realm}/components/{id}.
        """
        return client.get_components_by_id(**drop_none(id=id, realm=realm))

    @mcp.tool(
        tags={"components"}, annotations={"readOnlyHint": True, "idempotentHint": True}
    )
    async def keycloak_agent_components_list_components(
        realm: str = Field(default="master", description="Realm name."),
        name: str | None = Field(default=None, description="Query filter: name."),
        parent: str | None = Field(default=None, description="Query filter: parent."),
        providerId: str | None = Field(
            default=None, description="Query filter: providerId."
        ),
        type: str | None = Field(default=None, description="Query filter: type."),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """List components

        Calls GET /admin/realms/{realm}/components.
        """
        return client.list_components(
            **drop_none(
                realm=realm, name=name, parent=parent, providerId=providerId, type=type
            )
        )
