"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_realms`` / ``ingest_users`` /
``ingest_clients`` / ``ingest_groups`` seams with a fake engine client (no engine
required), asserting the txn add_node/commit + edge calls and the Keycloak
record -> :Realm/:User/:Client/:Group mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import pytest

from keycloak_agent import kg_ingest
from keycloak_agent.kg_ingest import (
    KnowledgeGraphIngestUnavailable,
    ingest_clients,
    ingest_entities,
    ingest_groups,
    ingest_realms,
    ingest_users,
)


class _FakeSink:
    """Stands in for the retired native-ingest write path (SDK-GAPS.md #0).

    Exposes the same ``.nodes.values[...]`` / ``.changes.edges`` shape the
    old ``_FakeClient`` gave these tests (computed from the entities/
    relationships actually passed to the now-retired ``ingest_entities``),
    so the mapper assertions below are unchanged from before the migration.
    """

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def __call__(self, entities, relationships=None, **kwargs: Any):
        self.calls.append(
            {"entities": list(entities), "relationships": list(relationships or [])}
        )
        return {"nodes": len(entities), "edges": len(relationships or [])}

    @property
    def nodes(self) -> Any:
        values = {e["id"]: e for call in self.calls for e in call["entities"]}
        return type("_N", (), {"values": values})()

    @property
    def changes(self) -> Any:
        edges = [
            (r["source"], r["target"], {"relationship": r["relationship"]})
            for call in self.calls
            for r in call["relationships"]
        ]
        return type("_C", (), {"edges": edges})()


def test_ingest_entities_is_unavailable():
    """The retired primitive fails closed (SDK-GAPS.md #0) instead of
    silently no-op'ing or validating input -- it never reaches native_ingest.
    """
    with pytest.raises(KnowledgeGraphIngestUnavailable):
        ingest_entities(
            [
                {"id": "a", "node_type": "User", "username": "u"},
                {"id": "b", "node_type": "Realm"},
            ],
            [{"source": "a", "target": "b", "relationship": "inRealm"}],
        )


def test_ingest_realms_maps_realm(monkeypatch):
    c = _FakeSink()
    monkeypatch.setattr(kg_ingest, "ingest_entities", c)
    res = ingest_realms(
        [{"realm": "homelab", "displayName": "Homelab", "enabled": True}],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["keycloak:realm:homelab"]
    assert node["node_type"] == "Realm"
    assert node["realmName"] == "homelab"
    assert node["externalToolId"] == "homelab"


def test_ingest_users_maps_user_and_realm_link(monkeypatch):
    c = _FakeSink()
    monkeypatch.setattr(kg_ingest, "ingest_entities", c)
    res = ingest_users(
        [{"id": "u1", "username": "alice", "email": "a@x.io", "enabled": True}],
        realm="homelab",
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.nodes.values["keycloak:user:u1"]["node_type"] == "User"
    assert c.nodes.values["keycloak:user:u1"]["username"] == "alice"
    assert c.nodes.values["keycloak:realm:homelab"]["node_type"] == "Realm"
    assert c.changes.edges == [
        ("keycloak:user:u1", "keycloak:realm:homelab", {"relationship": "inRealm"})
    ]


def test_ingest_clients_maps_client_and_realm_link(monkeypatch):
    c = _FakeSink()
    monkeypatch.setattr(kg_ingest, "ingest_entities", c)
    res = ingest_clients(
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
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    node = c.nodes.values["keycloak:client:cuuid1"]
    assert node["node_type"] == "Client"
    assert node["clientId"] == "grafana"
    assert node["publicClient"] is False
    assert c.changes.edges == [
        (
            "keycloak:client:cuuid1",
            "keycloak:realm:homelab",
            {"relationship": "inRealm"},
        )
    ]


def test_ingest_groups_walks_subgroups(monkeypatch):
    c = _FakeSink()
    monkeypatch.setattr(kg_ingest, "ingest_entities", c)
    res = ingest_groups(
        [
            {
                "id": "g1",
                "name": "admins",
                "path": "/admins",
                "subGroups": [{"id": "g2", "name": "ops", "path": "/admins/ops"}],
            }
        ],
        realm="homelab",
        client=c,
    )
    # 2 groups + 1 realm node; edges: 2 inRealm + 1 hasSubGroup
    assert res == {"nodes": 3, "edges": 3}
    assert c.nodes.values["keycloak:group:g1"]["node_type"] == "Group"
    assert c.nodes.values["keycloak:group:g1"]["groupPath"] == "/admins"
    assert c.nodes.values["keycloak:group:g2"]["groupPath"] == "/admins/ops"
    assert (
        "keycloak:group:g1",
        "keycloak:group:g2",
        {"relationship": "hasSubGroup"},
    ) in c.changes.edges
