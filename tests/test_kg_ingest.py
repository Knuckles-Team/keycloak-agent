"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_realms`` / ``ingest_users`` /
``ingest_clients`` / ``ingest_groups`` seams with a fake engine client (no engine
required), asserting the txn add_node/commit + edge calls and the Keycloak
record -> :Realm/:User/:Client/:Group mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError

from keycloak_agent.kg_ingest import (
    ingest_clients,
    ingest_entities,
    ingest_groups,
    ingest_realms,
    ingest_users,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def add_edge(self, txn, source, target, props):
        self.edges.append((source, target, props))

    def commit(self, txn):
        self.committed = True
        return True


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "User", "username": "u"},
            {"id": "b", "node_type": "Realm"},
        ],
        [{"source": "a", "target": "b", "relationship": "inRealm"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "keycloak-agent"
    assert c.txn.nodes["a"]["domain"] == "keycloak"
    assert c.txn.edges == [("a", "b", {"relationship": "inRealm"})]


def test_ingest_realms_maps_realm():
    c = _FakeClient()
    res = ingest_realms(
        [{"realm": "homelab", "displayName": "Homelab", "enabled": True}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.txn.nodes["keycloak:realm:homelab"]
    assert node["node_type"] == "Realm"
    assert node["realmName"] == "homelab"
    assert node["externalToolId"] == "homelab"


def test_ingest_users_maps_user_and_realm_link():
    c = _FakeClient()
    res = ingest_users(
        [{"id": "u1", "username": "alice", "email": "a@x.io", "enabled": True}],
        realm="homelab",
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.nodes["keycloak:user:u1"]["node_type"] == "User"
    assert c.txn.nodes["keycloak:user:u1"]["username"] == "alice"
    assert c.txn.nodes["keycloak:realm:homelab"]["node_type"] == "Realm"
    assert c.txn.edges == [
        ("keycloak:user:u1", "keycloak:realm:homelab", {"relationship": "inRealm"})
    ]


def test_ingest_clients_maps_client_and_realm_link():
    c = _FakeClient()
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
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    node = c.txn.nodes["keycloak:client:cuuid1"]
    assert node["node_type"] == "Client"
    assert node["clientId"] == "grafana"
    assert node["publicClient"] is False
    assert c.txn.edges == [
        ("keycloak:client:cuuid1", "keycloak:realm:homelab", {"relationship": "inRealm"})
    ]


def test_ingest_groups_walks_subgroups():
    c = _FakeClient()
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
        graph="__commons__",
    )
    # 2 groups + 1 realm node; edges: 2 inRealm + 1 hasSubGroup
    assert res == {"nodes": 3, "edges": 3}
    assert c.txn.nodes["keycloak:group:g1"]["node_type"] == "Group"
    assert c.txn.nodes["keycloak:group:g1"]["groupPath"] == "/admins"
    assert c.txn.nodes["keycloak:group:g2"]["groupPath"] == "/admins/ops"
    assert (
        "keycloak:group:g1",
        "keycloak:group:g2",
        {"relationship": "hasSubGroup"},
    ) in c.txn.edges


def test_retired_node_type_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities(
            [{"id": "retired", "type": "RetiredAlias"}],
            client=_FakeClient(),
        )


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
