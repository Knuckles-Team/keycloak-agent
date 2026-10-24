"""Main FastMCP server and tool registration."""

from keycloak_agent.mcp import (
    register_attack_detection_tools,
    register_authentication_tools,
    register_clients_tools,
    register_components_tools,
    register_groups_tools,
    register_idps_tools,
    register_info_tools,
    register_ingest_tools,
    register_organizations_tools,
    register_realms_tools,
    register_roles_tools,
    register_users_tools,
)

# Re-exported so register_tool_surface(tools_module=...) auto-discovers them as
# module attributes (and ruff treats the imports as used).
__all__ = [
    "register_attack_detection_tools",
    "register_authentication_tools",
    "register_clients_tools",
    "register_components_tools",
    "register_groups_tools",
    "register_idps_tools",
    "register_info_tools",
    "register_ingest_tools",
    "register_organizations_tools",
    "register_realms_tools",
    "register_roles_tools",
    "register_users_tools",
]
