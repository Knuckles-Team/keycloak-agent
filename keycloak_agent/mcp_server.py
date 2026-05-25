import warnings
import logging
import os
import sys
from typing import Any
from fastmcp import Context, FastMCP
from fastmcp.utilities.logging import get_logger
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server
from dotenv import find_dotenv, load_dotenv

from keycloak_agent.mcp.mcp_realms import register_realms_tools
from keycloak_agent.mcp.mcp_users import register_users_tools
from keycloak_agent.mcp.mcp_clients import register_clients_tools

__version__ = "0.15.0"
logger = get_logger(name="keycloak_agent")

def get_mcp_instance() -> tuple[Any, ...]:
    load_dotenv(find_dotenv())
    args, mcp, middlewares = create_mcp_server(
        name="Keycloak Agent MCP",
        version=__version__,
        instructions="Keycloak Agent MCP Server - Managed dynamic operations.",
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    
    DEFAULT_REALMSTOOL = to_boolean(os.getenv("REALMSTOOL", "True"))
    if DEFAULT_REALMSTOOL:
        register_realms_tools(mcp)
    
    DEFAULT_USERSTOOL = to_boolean(os.getenv("USERSTOOL", "True"))
    if DEFAULT_USERSTOOL:
        register_users_tools(mcp)
    
    DEFAULT_CLIENTSTOOL = to_boolean(os.getenv("CLIENTSTOOL", "True"))
    if DEFAULT_CLIENTSTOOL:
        register_clients_tools(mcp)

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
