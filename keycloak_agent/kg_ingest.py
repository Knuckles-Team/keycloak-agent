"""Native epistemic-graph ingestion for Keycloak records.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Connector-specific mappers emit
canonical node_type nodes and relationship edges. The required agent-utilities
native-ingest primitive owns the transaction and raises NativeIngestError when the
authoritative engine cannot commit.
"""

from __future__ import annotations

from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)

_SOURCE = "keycloak-agent"
_DOMAIN = "keycloak"


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships through agent-utilities."""
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


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


# ── EH-410: pseudonymized security-audit events ──────────────────────────────
# Operator ruling 2026-09-24: identities are keyed HMAC references, IPs are cut to
# /24 (IPv4) or /48 (IPv6), and only the allowlisted scalar fields below pass --
# free-form ``details``/``representation`` bodies never do.
_USER_EVENT_POLICY = {
    "keep": ("type", "time", "clientId", "error", "realmId"),
    "identities": ("userId", "sessionId", "details.username"),
    "ips": ("ipAddress",),
}
_ADMIN_EVENT_POLICY = {
    "keep": ("operationType", "resourceType", "time", "error", "realmId"),
    "identities": ("authDetails.userId", "authDetails.clientId"),
    "secret_paths": ("resourcePath",),
    "ips": ("authDetails.ipAddress",),
}


def _event_node(
    event: dict[str, Any], node_type: str, realm: str, pseudonymizer: Any, policy: Any
) -> dict[str, Any]:
    import json

    fingerprint = json.dumps(event, sort_keys=True, default=str)
    node = pseudonymizer.record(event, policy)
    node.update(
        {
            "id": f"keycloak:event:{pseudonymizer.reference('event', fingerprint)}",
            "node_type": node_type,
            "realmName": realm,
            "epistemic_class": "observation",
        }
    )
    return node


def ingest_security_events(
    events: list[dict[str, Any]],
    *,
    realm: str,
    admin: bool = False,
    pseudonymizer: Any | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Map Keycloak user/admin events → pseudonymized ``:AuthenticationEvent`` /
    ``:AdminAuditEvent`` nodes (+ ``:inRealm``) and ingest them.

    ``pseudonymizer`` defaults to the deployment key in OpenBao
    (``AuditPseudonymizer.from_settings``); without it the feed refuses.
    """
    from agent_utilities.security.audit_pseudonym import (
        AuditFieldPolicy,
        AuditPseudonymizer,
    )

    pseudo = pseudonymizer or AuditPseudonymizer.from_settings()
    spec = _ADMIN_EVENT_POLICY if admin else _USER_EVENT_POLICY
    policy = AuditFieldPolicy(**spec)
    node_type = "AdminAuditEvent" if admin else "AuthenticationEvent"
    realm_id = f"keycloak:realm:{realm}"
    entities: list[dict[str, Any]] = [
        _event_node(event, node_type, realm, pseudo, policy)
        for event in events or []
        if isinstance(event, dict)
    ]
    if not entities:
        return {"nodes": 0, "edges": 0}
    relationships = [
        {"source": node["id"], "target": realm_id, "relationship": "inRealm"}
        for node in entities
    ]
    entities.append({"id": realm_id, "node_type": "Realm", "realmName": realm})
    return ingest_entities(entities, relationships, client=client, graph=graph)
