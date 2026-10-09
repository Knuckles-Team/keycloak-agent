"""Wire-First MCP tools that natively ingest Keycloak records into epistemic-graph.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Each tool lists real records via the
Keycloak Admin client and pushes them into the knowledge graph as typed OWL nodes
(``:Realm`` / ``:User`` / ``:Client`` / ``:Group``) via ``keycloak_agent.kg_ingest``.
Native-ingest failures propagate to the caller.
"""

from __future__ import annotations

import json

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client
from keycloak_agent.kg_ingest import (
    ingest_clients,
    ingest_groups,
    ingest_realms,
    ingest_users,
)


def _as_list(resp) -> list:
    """Normalise a client response into a list of dict records."""
    data = getattr(resp, "data", resp)
    if isinstance(data, list):
        records = data
    elif data is None:
        records = []
    else:
        records = [data]
    return [
        r.model_dump() if hasattr(r, "model_dump") else r
        for r in records
        if r is not None
    ]


def register_ingest_tools(mcp: FastMCP):
    """Register Keycloak native KG-ingestion tools."""

    @mcp.tool(tags={"kg", "realms"})
    async def keycloak_ingest_realms(
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """List all realms and ingest them into epistemic-graph as ``:Realm`` nodes."""
        if ctx:
            await ctx.info("Ingesting Keycloak realms into the knowledge graph...")
        realms = _as_list(client.list_realms())
        result = await ingest_realms(realms)
        return {"listed": len(realms), "ingested": result}

    @mcp.tool(tags={"kg", "users"})
    async def keycloak_ingest_users(
        params_json: str = Field(
            default="{}",
            description="JSON string with 'realm' (required) and optional 'search'.",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """List users in a realm and ingest them as ``:User`` nodes (+ ``:inRealm`` links)."""
        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception:  # noqa: BLE001
            return {"error": "Operation failed"}
        realm = kwargs.get("realm")
        if not realm:
            return {"error": "Missing required 'realm' in params_json."}
        if ctx:
            await ctx.info(f"Ingesting users from realm '{realm}'...")
        users = _as_list(client.list_users(realm=realm, search=kwargs.get("search")))
        result = await ingest_users(users, realm=realm)
        return {"listed": len(users), "ingested": result}

    @mcp.tool(tags={"kg", "clients"})
    async def keycloak_ingest_clients(
        params_json: str = Field(
            default="{}", description="JSON string with 'realm' (required)."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """List clients in a realm and ingest them as ``:Client`` nodes (+ ``:inRealm``)."""
        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception:  # noqa: BLE001
            return {"error": "Operation failed"}
        realm = kwargs.get("realm")
        if not realm:
            return {"error": "Missing required 'realm' in params_json."}
        if ctx:
            await ctx.info(f"Ingesting clients from realm '{realm}'...")
        clients = _as_list(client.list_clients(realm=realm))
        result = await ingest_clients(clients, realm=realm)
        return {"listed": len(clients), "ingested": result}

    @mcp.tool(tags={"kg", "groups"})
    async def keycloak_ingest_groups(
        params_json: str = Field(
            default="{}", description="JSON string with 'realm' (required)."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """List groups in a realm and ingest them as ``:Group`` nodes (+ ``:hasSubGroup``)."""
        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception:  # noqa: BLE001
            return {"error": "Operation failed"}
        realm = kwargs.get("realm")
        if not realm:
            return {"error": "Missing required 'realm' in params_json."}
        if ctx:
            await ctx.info(f"Ingesting groups from realm '{realm}'...")
        lister = getattr(client, "list_groups", None) or getattr(
            client, "get_groups", None
        )
        if lister is None:
            return {"error": "Client has no list_groups/get_groups method."}
        groups = _as_list(lister(realm=realm))
        result = await ingest_groups(groups, realm=realm)
        return {"listed": len(groups), "ingested": result}
