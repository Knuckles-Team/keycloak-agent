"""Epistemic-graph typed-node ingestion via agent_connector_sdk — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_realms`` / ``ingest_users`` /
``ingest_clients`` / ``ingest_groups`` seams against a fake transport one level below
the SDK's own ``KnowledgeIngest`` facade, so these tests still run the SDK's real
request-building contract. Asserts the Keycloak record -> :Realm/:User/:Client/:Group
mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest

from keycloak_agent.kg_ingest import (
    ingest_clients,
    ingest_entities,
    ingest_groups,
    ingest_realms,
    ingest_users,
)


class _FakeTransport:
    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def source_status(self, connector, stream):
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request):
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, data):
        raise AssertionError("keycloak-agent ingestion carries no media")


@pytest.fixture
def ingest():
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


def _node_type(record: Any) -> str:
    """A real generated ``SourceRecord`` has no bare ``node_type`` field — it's the
    last segment of ``mapping_reference``
    (``manifest:<connector>#schema_mappings/<NodeType>``)."""
    return record.mapping_reference.rsplit("/", 1)[-1]


def _rel_name(relationship: Any) -> str:
    """Likewise, a ``SourceRelationship``'s kind is the last segment of
    ``relation_reference`` (``manifest:<connector>#resources/<NodeType>/relations/<kind>``)."""
    return relationship.relation_reference.rsplit("/", 1)[-1]


async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "User", "username": "u"},
            {"id": "b", "node_type": "Realm"},
        ],
        [{"source": "a", "target": "b", "relationship": "inRealm"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(transport.requests) == 1
    records = {r.record_id: r for r in transport.requests[0].records}
    assert set(records) == {"a", "b"}
    rel = transport.requests[0].relationships[0]
    assert (rel.source.record_id, rel.target.record_id, _rel_name(rel)) == (
        "a",
        "b",
        "inRealm",
    )


async def test_ingest_realms_maps_realm(ingest):
    service, transport = ingest
    res = await ingest_realms(
        [{"realm": "homelab", "displayName": "Homelab", "enabled": True}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = transport.requests[0].records[0]
    assert node.record_id == "keycloak:realm:homelab"
    assert _node_type(node) == "Realm"
    assert node.payload["realmName"] == "homelab"
    assert node.payload["externalToolId"] == "homelab"


async def test_ingest_users_maps_user_and_realm_link(ingest):
    service, transport = ingest
    res = await ingest_users(
        [{"id": "u1", "username": "alice", "email": "a@x.io", "enabled": True}],
        realm="homelab",
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    records = {r.record_id: r for r in transport.requests[0].records}
    user = records["keycloak:user:u1"]
    assert _node_type(user) == "User"
    # The SDK's PersistencePrivacyGuard (IngestBinding(sanitize=True), the default)
    # redacts personal-identifier fields before they ever leave the process -- a
    # real, deliberate improvement this migration picks up for free: Keycloak
    # usernames/emails no longer land in the knowledge graph in plaintext.
    assert user.payload["username"] == "[REDACTED_PERSON]"
    assert user.payload["email"] == "[REDACTED_EMAIL]"
    assert user.payload["enabled"] is True
    assert user.record_id == "keycloak:user:u1"  # structural id field: untouched
    assert _node_type(records["keycloak:realm:homelab"]) == "Realm"
    rel = transport.requests[0].relationships[0]
    assert (rel.source.record_id, rel.target.record_id, _rel_name(rel)) == (
        "keycloak:user:u1",
        "keycloak:realm:homelab",
        "inRealm",
    )


async def test_ingest_clients_maps_client_and_realm_link(ingest):
    service, transport = ingest
    res = await ingest_clients(
        [
            {
                "id": "cuuid1",
                "clientId": "grafana",
                "protocol": "openid-connect",
                "publicClient": False,
                "enabled": True,
            }
        ],
        realm="homelab",
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    records = {r.record_id: r for r in transport.requests[0].records}
    node = records["keycloak:client:cuuid1"]
    assert _node_type(node) == "Client"
    assert node.payload["clientId"] == "grafana"
    assert node.payload["publicClient"] is False
    rel = transport.requests[0].relationships[0]
    assert (rel.source.record_id, rel.target.record_id, _rel_name(rel)) == (
        "keycloak:client:cuuid1",
        "keycloak:realm:homelab",
        "inRealm",
    )


async def test_ingest_groups_walks_subgroups(ingest):
    service, transport = ingest
    res = await ingest_groups(
        [
            {
                "id": "g1",
                "name": "admins",
                "path": "/admins",
                "subGroups": [{"id": "g2", "name": "ops", "path": "/admins/ops"}],
            }
        ],
        realm="homelab",
        ingest=service,
    )
    # 2 groups + 1 realm node; edges: 2 inRealm + 1 hasSubGroup
    assert res == {"nodes": 3, "edges": 3}
    records = {r.record_id: r for r in transport.requests[0].records}
    assert _node_type(records["keycloak:group:g1"]) == "Group"
    assert records["keycloak:group:g1"].payload["groupPath"] == "/admins"
    assert records["keycloak:group:g2"].payload["groupPath"] == "/admins/ops"
    rels = {
        (r.source.record_id, r.target.record_id, _rel_name(r))
        for r in transport.requests[0].relationships
    }
    assert ("keycloak:group:g1", "keycloak:group:g2", "hasSubGroup") in rels


async def test_retired_node_type_alias_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError):
        await ingest_entities(
            [{"id": "retired", "type": "RetiredAlias"}], ingest=service
        )


async def test_empty_native_ingest_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)


async def test_empty_mappers_are_a_noop(ingest):
    service, transport = ingest
    assert await ingest_realms([], ingest=service) is None
    assert await ingest_users([], ingest=service) is None
    assert await ingest_clients([], ingest=service) is None
    assert await ingest_groups([], ingest=service) is None
    assert transport.requests == []
