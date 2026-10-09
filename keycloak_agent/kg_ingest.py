"""Native epistemic-graph ingestion for Keycloak records.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Connector-specific mappers emit
canonical node_type nodes and relationship edges through ``agent_connector_sdk.ingest``
-- the generated ``SourceIngest`` client, not a local ingestion helper.
"""

from __future__ import annotations

from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Entity,
    IngestBinding,
    IngestError,
    KnowledgeIngest,
    Relationship,
    current_ingest,
)

_BINDING = IngestBinding(connector="keycloak-agent", stream="keycloak")

_ENTITY_RESERVED_KEYS = frozenset({"id", "node_type"})
_RELATIONSHIP_RESERVED_KEYS = frozenset({"source", "target", "relationship"})


def _to_entity(record: dict[str, Any]) -> Entity:
    return Entity(
        id=record.get("id"),
        node_type=record.get("node_type"),
        properties={
            key: value
            for key, value in record.items()
            if key not in _ENTITY_RESERVED_KEYS
        },
    )


def _to_relationship(record: dict[str, Any]) -> Relationship:
    properties = {
        key: value
        for key, value in record.items()
        if key not in _RELATIONSHIP_RESERVED_KEYS
    }
    return Relationship(
        source=record["source"],
        target=record["target"],
        relationship=record["relationship"],
        properties=properties or None,
    )


async def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships through the SDK ingest facade."""
    if not entities:
        raise IngestError("ingest_entities needs at least one entity")
    change_set = ChangeSet(
        entities=tuple(_to_entity(entity) for entity in entities),
        relationships=tuple(
            _to_relationship(relationship) for relationship in relationships or ()
        ),
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


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
    return await ingest_entities(entities, ingest=ingest)


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
    return await ingest_entities(entities, relationships, ingest=ingest)


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
    return await ingest_entities(entities, relationships, ingest=ingest)


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
    return await ingest_entities(entities, relationships, ingest=ingest)
