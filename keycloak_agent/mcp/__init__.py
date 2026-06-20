from keycloak_agent.mcp.mcp_attack_detection import register_attack_detection_tools
from keycloak_agent.mcp.mcp_authentication import register_authentication_tools
from keycloak_agent.mcp.mcp_clients import register_clients_tools
from keycloak_agent.mcp.mcp_components import register_components_tools
from keycloak_agent.mcp.mcp_groups import register_groups_tools
from keycloak_agent.mcp.mcp_idps import register_idps_tools
from keycloak_agent.mcp.mcp_info import register_info_tools
from keycloak_agent.mcp.mcp_organizations import register_organizations_tools
from keycloak_agent.mcp.mcp_realms import register_realms_tools
from keycloak_agent.mcp.mcp_roles import register_roles_tools
from keycloak_agent.mcp.mcp_users import register_users_tools

__all__ = [
    "register_attack_detection_tools",
    "register_authentication_tools",
    "register_clients_tools",
    "register_components_tools",
    "register_groups_tools",
    "register_idps_tools",
    "register_info_tools",
    "register_organizations_tools",
    "register_realms_tools",
    "register_roles_tools",
    "register_users_tools",
]
