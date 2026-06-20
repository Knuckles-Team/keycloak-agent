"""Main FastMCP server and tool registration."""

import sys
from typing import Any

from agent_utilities.mcp_utilities import (
    create_mcp_server,
    load_config,
    register_tool_surface,
)
from fastmcp.utilities.logging import get_logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from keycloak_agent.api_client import Api
from keycloak_agent.auth import get_client
from keycloak_agent.mcp import (
    register_attack_detection_tools,
    register_authentication_tools,
    register_clients_tools,
    register_components_tools,
    register_groups_tools,
    register_idps_tools,
    register_info_tools,
    register_organizations_tools,
    register_realms_tools,
    register_roles_tools,
    register_users_tools,
)

__version__ = "0.15.0"
logger = get_logger(name="keycloak_agent")

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
    "register_organizations_tools",
    "register_realms_tools",
    "register_roles_tools",
    "register_users_tools",
]


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

    registered_tags = register_tool_surface(
        mcp,
        client_cls=Api,
        get_client=get_client,
        service="keycloak-agent",
        tools_module=sys.modules[__name__],
    )
    logger.info("Registered condensed tool tags", extra={"tags": registered_tags})

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
