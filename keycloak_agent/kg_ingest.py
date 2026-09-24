"""Native epistemic-graph ingestion for Keycloak records.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Connector-specific mappers emit
canonical node_type nodes and relationship edges. The required agent-utilities
native-ingest primitive owns the transaction and raises NativeIngestError when the
authoritative engine cannot commit.
"""

from __future__ import annotations

from typing import Any


_SOURCE = "keycloak-agent"
_DOMAIN = "keycloak"


def ingest_entities(*args: object, **kwargs: object) -> object:
    """Write canonical typed nodes and relationships through agent-utilities.

    SDK-GAP: Always raises now; see KnowledgeGraphIngestUnavailable.
    """
    _kg_unavailable("ingest_entities")


def _realm_of(record: dict[str, Any], realm: str | None) -> str | None:
    """Resolve the owning realm name from an explicit arg or the record itself."""
    return realm or record.get("realm") or record.get("realmName")


def ingest_realms(
    realms: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Map Keycloak realm reps → ``:Realm`` nodes and ingest."""
    entities: list[dict[str, Any]] = []
    for realm in realms or []:
        name = realm.get("realm") or realm.get("id")
        if not name:
            continue
        entities.append(
            {
                "id": f"keycloak:realm:{name}",
                "node_type": "Realm",
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
) -> dict[str, int]:
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
                "node_type": "User",
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
                {
                    "id": f"keycloak:realm:{rname}",
                    "node_type": "Realm",
                    "realmName": rname,
                }
            )
            relationships.append(
                {
                    "source": f"keycloak:user:{uid}",
                    "target": f"keycloak:realm:{rname}",
                    "relationship": "inRealm",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_clients(
    clients: list[dict[str, Any]],
    *,
    realm: str | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
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
                "node_type": "Client",
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
                {
                    "id": f"keycloak:realm:{rname}",
                    "node_type": "Realm",
                    "realmName": rname,
                }
            )
            relationships.append(
                {
                    "source": f"keycloak:client:{cuuid}",
                    "target": f"keycloak:realm:{rname}",
                    "relationship": "inRealm",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_groups(
    groups: list[dict[str, Any]],
    *,
    realm: str | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
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
                "node_type": "Group",
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
                        "node_type": "Realm",
                        "realmName": rname,
                    }
                )
            relationships.append(
                {
                    "source": node_id,
                    "target": f"keycloak:realm:{rname}",
                    "relationship": "inRealm",
                }
            )
        if parent_id:
            relationships.append(
                {"source": parent_id, "target": node_id, "relationship": "hasSubGroup"}
            )
        for sub in rec.get("subGroups") or []:
            _walk(sub, node_id)

    for grp in groups or []:
        _walk(grp, None)
    return ingest_entities(entities, relationships, client=client, graph=graph)


class KnowledgeGraphIngestUnavailable(RuntimeError):
    """Direct-to-graph ingestion is unavailable from this connector.

    SDK-GAP (EH-48x, /var/tmp/l9/finish/au-decon-G4c/SDK-GAPS.md): raised in
    place of the old ``agent_utilities.knowledge_graph`` native-ingest call --
    agent-connector-sdk has no facade over EG's typed ingestion protocol yet,
    and the fleet precedent (agents/world-reference-mcp) moves direct-to-graph
    delivery to agent_connector_sdk.runner/sinks at the deployment layer, out
    of connector scope.
    """


def _kg_unavailable(name: str) -> None:
    raise KnowledgeGraphIngestUnavailable(
        f"{name}: direct-to-graph ingestion moved out of connector code "
        "(agent-utilities removed); no agent-connector-sdk facade exists yet "
        "-- see SDK-GAPS.md"
    )
