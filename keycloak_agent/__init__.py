"""CONCEPT:AU-ECO.messaging.native-backend-abstraction Unified ecosystem initialization dynamic check."""

from scion_sdk.connector import Connector

from keycloak_agent.api_client import Api
from keycloak_agent.auth import get_client

connector = Connector(
    api=Api,
    get_client=get_client,
    tools="keycloak_agent.mcp_server",
    instructions="Keycloak Agent MCP Server - Managed dynamic operations.",
    transports=(
        "stdio",
        "streamable-http",
    ),
)
