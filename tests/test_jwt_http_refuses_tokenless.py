"""A network request without a token is refused when the server runs in JWT mode.

An unbound in-process call is the SYSTEM actor by design (scion-sdk 0.6.2+); the
served transport is what refuses an anonymous caller.
"""

from __future__ import annotations

import threading
from unittest.mock import AsyncMock

import pytest
import uvicorn
from fastmcp import Client
from fastmcp.server.auth.providers.jwt import RSAKeyPair
from scion_sdk.mcp.server import create_mcp_server

ISSUER = "https://idp.example.invalid/realms/demo"
AUDIENCE = "keycloak-agent"


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002")
async def test_http_request_without_token_is_refused_in_jwt_mode() -> None:
    keys = RSAKeyPair.generate()
    _args, mcp, _mw = create_mcp_server(
        "keycloak-agent",
        version="0",
        command_args=[
            "--transport",
            "streamable-http",
            "--auth-type",
            "jwt",
            "--token-issuer",
            ISSUER,
            "--token-audience",
            AUDIENCE,
            "--token-public-key",
            keys.public_key,
        ],
    )

    @mcp.tool
    def ping() -> str:
        return "pong"

    ready = threading.Event()
    server = uvicorn.Server(
        uvicorn.Config(
            mcp.http_app(),
            host="127.0.0.1",
            port=0,
            log_level="error",
            lifespan="on",
            callback_notify=AsyncMock(side_effect=ready.set),
            timeout_notify=1,
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        assert ready.wait(30) and server.started
        port = server.servers[0].sockets[0].getsockname()[1]
        url = f"http://127.0.0.1:{port}/mcp"
        with pytest.raises(Exception):  # noqa: B017 - 401 surfaces as a client error
            async with Client(url) as client:
                await client.call_tool("ping", {})
        token = keys.create_token(subject="op", issuer=ISSUER, audience=AUDIENCE)
        async with Client(url, auth=token) as client:
            assert (await client.call_tool("ping", {})).data == "pong"
    finally:
        server.should_exit = True
        thread.join(10)
