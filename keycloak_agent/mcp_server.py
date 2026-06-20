"""Main FastMCP server and tool registration."""

import os
import sys
from typing import Any

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server, load_config
from fastmcp.utilities.logging import get_logger
from starlette.requests import Request
from starlette.responses import JSONResponse

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

__version__ = "0.15.0"
logger = get_logger(name="keycloak_agent")


def get_mcp_instance() -> tuple[Any, ...]:
    load_config()
    args, mcp, middlewares = create_mcp_server(
        name="Keycloak Agent MCP",
        version=__version__,
        instructions="Keycloak Agent MCP Server - Managed dynamic operations.",
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    # Always register info tool
    register_info_tools(mcp)

    DEFAULT_REALMSTOOL = to_boolean(os.getenv("REALMSTOOL", "True"))
    if DEFAULT_REALMSTOOL:
        register_realms_tools(mcp)

    DEFAULT_USERSTOOL = to_boolean(os.getenv("USERSTOOL", "True"))
    if DEFAULT_USERSTOOL:
        register_users_tools(mcp)

    DEFAULT_CLIENTSTOOL = to_boolean(os.getenv("CLIENTSTOOL", "True"))
    if DEFAULT_CLIENTSTOOL:
        register_clients_tools(mcp)

    DEFAULT_ROLESTOOL = to_boolean(os.getenv("ROLESTOOL", "True"))
    if DEFAULT_ROLESTOOL:
        register_roles_tools(mcp)

    DEFAULT_GROUPSTOOL = to_boolean(os.getenv("GROUPSTOOL", "True"))
    if DEFAULT_GROUPSTOOL:
        register_groups_tools(mcp)

    DEFAULT_IDPSTOOL = to_boolean(os.getenv("IDPSTOOL", "True"))
    if DEFAULT_IDPSTOOL:
        register_idps_tools(mcp)

    DEFAULT_AUTHTOOL = to_boolean(os.getenv("AUTHTOOL", "True"))
    if DEFAULT_AUTHTOOL:
        register_authentication_tools(mcp)

    DEFAULT_COMPONENTSTOOL = to_boolean(os.getenv("COMPONENTSTOOL", "True"))
    if DEFAULT_COMPONENTSTOOL:
        register_components_tools(mcp)

    DEFAULT_ATTACKTOOL = to_boolean(os.getenv("ATTACKTOOL", "True"))
    if DEFAULT_ATTACKTOOL:
        register_attack_detection_tools(mcp)

    DEFAULT_ORGANIZATIONSTOOL = to_boolean(os.getenv("ORGANIZATIONSTOOL", "True"))
    if DEFAULT_ORGANIZATIONSTOOL:
        register_organizations_tools(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)
    return mcp, args, middlewares


def mcp_server() -> None:
    mcp, args, middlewares = get_mcp_instance()
    print(f"Keycloak Agent MCP v{__version__}", file=sys.stderr)
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    mcp_server()
