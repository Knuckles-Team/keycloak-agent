"""Native epistemic-graph ingestion for Keycloak records.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Connector-specific mappers emit
canonical node_type nodes and relationship edges through ``agent_connector_sdk.ingest``
-- the generated ``SourceIngest`` client, not a local ingestion helper.
"""

from __future__ import annotations

from typing import Any

from agent_connector_sdk.ingest import (
    KnowledgeIngest,
    SourceStream,
)

STREAM = SourceStream.for_package(__package__.split(".")[0], "keycloak")


def _realm_of(record: dict[str, Any], realm: str | None) -> str | None:
    """Resolve the owning realm name from an explicit arg or the record itself."""
    return realm or record.get("realm") or record.get("realmName")


async def ingest_realms(
    realms: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
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
                "node_type": "Realm",
                "realmName": name,
                "displayName": realm.get("displayName"),
                "enabled": realm.get("enabled"),
                "externalToolId": str(name),
            }
        )
    if not entities:
        return None
    return await STREAM.entities(entities, ingest=ingest)


async def ingest_users(
    users: list[dict[str, Any]],
    *,
    realm: str | None = None,
    ingest: KnowledgeIngest | None = None,
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
    if not entities:
        return None
    return await STREAM.entities(entities, relationships, ingest=ingest)


async def ingest_clients(
    clients: list[dict[str, Any]],
    *,
    realm: str | None = None,
    ingest: KnowledgeIngest | None = None,
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
    if not entities:
        return None
    return await STREAM.entities(entities, relationships, ingest=ingest)


async def ingest_groups(
    groups: list[dict[str, Any]],
    *,
    realm: str | None = None,
    ingest: KnowledgeIngest | None = None,
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
    if not entities:
        return None
    return await STREAM.entities(entities, relationships, ingest=ingest)
