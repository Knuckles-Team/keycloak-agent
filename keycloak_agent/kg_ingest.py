"""Native epistemic-graph ingestion for Keycloak records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The keycloak-agent connector
natively pushes its identity data into the ONE epistemic-graph knowledge graph as
**typed OWL nodes** (`:Realm`, `:User`, `:Client`, `:Group`, `:Role`) + links, using
the lightweight engine client (``GraphComputeEngine()._client`` + ``txn``) — the same
fast client the blob ``MediaStore`` uses, NOT the heavy in-process ingestion engine.

Everything is dependency-/engine-guarded: with no agent-utilities KG stack or no
reachable engine, every entry point **no-ops** (returns ``None``), so the connector
keeps working with zero KG infrastructure. Nodes carry the shared provenance
(``domain``/``source``) and their ``type`` matches the classes federated by
``keycloak_agent.ontology`` (``keycloak.ttl``). Node ids follow
``keycloak:<class>:<externalId>``.

This is a thin mapper: it prefers the shared primitive
``agent_utilities.knowledge_graph.memory.native_ingest`` when available, and falls
back to a self-contained txn write (the primitive is not yet in every installed
agent_utilities) so the seam is testable and works standalone.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("keycloak_agent.kg")

_SOURCE = "keycloak-agent"
_DOMAIN = "keycloak"
_DEFAULT_GRAPH = "__commons__"


def _shared_ingest_entities() -> Any | None:
    """Return the shared ``native_ingest.ingest_entities`` if importable, else ``None``."""
    try:
        from agent_utilities.knowledge_graph.memory.native_ingest import (
            ingest_entities as _shared,
        )
    except Exception as e:  # noqa: BLE001 — primitive absent; use local fallback
        logger.debug("native_ingest primitive unavailable: %s", e)
        return None
    return _shared


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        graph = getattr(engine, "graph_name", None) or _DEFAULT_GRAPH
        return client, graph
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed nodes (+ edges) into epistemic-graph via the fast engine client.

    ``entities``: ``[{"id":..., "type":<owl:Class>, ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "type":rel}]``.
    Returns ``{"nodes":n, "edges":m}`` or ``None`` (no engine / failure; never raises).
    ``client``/``graph`` may be injected (tests); otherwise resolved on demand.
    """
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None

    # Prefer the shared primitive when a client isn't injected (real runtime path).
    if client is None:
        shared = _shared_ingest_entities()
        if shared is not None:
            try:
                return shared(entities, relationships, source=source, domain=domain)
            except Exception as e:  # noqa: BLE001 — fall through to local path
                logger.debug("shared native_ingest failed, using fallback: %s", e)
        client, graph = _client()
    if client is None:
        return None
    graph = graph or _DEFAULT_GRAPH

    try:
        txn = client.txn.begin(graph=graph)
        for ent in entities:
            props = {k: v for k, v in ent.items() if k != "id" and v is not None}
            props.setdefault("source", source)
            props.setdefault("domain", domain)
            client.txn.add_node(txn, ent["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)

    logger.info("KG ingest: wrote %d nodes, %d edges", len(entities), edges)
    return {"nodes": len(entities), "edges": edges}


def _realm_of(record: dict[str, Any], realm: str | None) -> str | None:
    """Resolve the owning realm name from an explicit arg or the record itself."""
    return realm or record.get("realm") or record.get("realmName")


def ingest_realms(
    realms: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map Keycloak realm reps → ``:Realm`` nodes and ingest."""
    entities: list[dict[str, Any]] = []
    for realm in realms or []:
        name = realm.get("realm") or realm.get("id")
        if not name:
            continue
        entities.append(
            {
                "id": f"keycloak:realm:{name}",
                "type": "Realm",
                "realmName": name,
                "displayName": realm.get("displayName"),
                "enabled": realm.get("enabled"),
                "externalToolId": str(name),
            }
        )
    return ingest_entities(entities, client=client, graph=graph)


def ingest_users(
    users: list[dict[str, Any]],
    *,
    realm: str | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map Keycloak user reps → ``:User`` nodes (+ ``:inRealm`` links) and ingest."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for user in users or []:
        uid = user.get("id")
        if not uid:
            continue
        entities.append(
            {
                "id": f"keycloak:user:{uid}",
                "type": "User",
                "username": user.get("username"),
                "email": user.get("email"),
                "firstName": user.get("firstName"),
                "lastName": user.get("lastName"),
                "enabled": user.get("enabled"),
                "emailVerified": user.get("emailVerified"),
                "externalToolId": str(uid),
            }
        )
        rname = _realm_of(user, realm)
        if rname:
            entities.append(
                {"id": f"keycloak:realm:{rname}", "type": "Realm", "realmName": rname}
            )
            relationships.append(
                {
                    "source": f"keycloak:user:{uid}",
                    "target": f"keycloak:realm:{rname}",
                    "type": "inRealm",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_clients(
    clients: list[dict[str, Any]],
    *,
    realm: str | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map Keycloak client reps → ``:Client`` nodes (+ ``:inRealm`` links) and ingest."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for rec in clients or []:
        cuuid = rec.get("id")
        if not cuuid:
            continue
        entities.append(
            {
                "id": f"keycloak:client:{cuuid}",
                "type": "Client",
                "clientId": rec.get("clientId"),
                "name": rec.get("name"),
                "description": rec.get("description"),
                "protocol": rec.get("protocol"),
                "enabled": rec.get("enabled"),
                "publicClient": rec.get("publicClient"),
                "externalToolId": str(cuuid),
            }
        )
        rname = _realm_of(rec, realm)
        if rname:
            entities.append(
                {"id": f"keycloak:realm:{rname}", "type": "Realm", "realmName": rname}
            )
            relationships.append(
                {
                    "source": f"keycloak:client:{cuuid}",
                    "target": f"keycloak:realm:{rname}",
                    "type": "inRealm",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_groups(
    groups: list[dict[str, Any]],
    *,
    realm: str | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map Keycloak group reps → ``:Group`` nodes (+ ``:inRealm`` / ``:hasSubGroup``)."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    seen_realms: set[str] = set()

    def _walk(rec: dict[str, Any], parent_id: str | None) -> None:
        gid = rec.get("id")
        if not gid:
            return
        node_id = f"keycloak:group:{gid}"
        entities.append(
            {
                "id": node_id,
                "type": "Group",
                "name": rec.get("name"),
                "groupPath": rec.get("path"),
                "externalToolId": str(gid),
            }
        )
        rname = _realm_of(rec, realm)
        if rname:
            if rname not in seen_realms:
                seen_realms.add(rname)
                entities.append(
                    {
                        "id": f"keycloak:realm:{rname}",
                        "type": "Realm",
                        "realmName": rname,
                    }
                )
            relationships.append(
                {
                    "source": node_id,
                    "target": f"keycloak:realm:{rname}",
                    "type": "inRealm",
                }
            )
        if parent_id:
            relationships.append(
                {"source": parent_id, "target": node_id, "type": "hasSubGroup"}
            )
        for sub in rec.get("subGroups") or []:
            _walk(sub, node_id)

    for grp in groups or []:
        _walk(grp, None)
    return ingest_entities(entities, relationships, client=client, graph=graph)
