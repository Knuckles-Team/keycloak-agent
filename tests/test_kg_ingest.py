"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_realms`` / ``ingest_users`` /
``ingest_clients`` / ``ingest_groups`` seams with a fake engine client (no engine
required), asserting the txn add_node/commit + edge calls and the Keycloak
record -> :Realm/:User/:Client/:Group mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.security.brain_context import ActorContext, use_actor
from agent_utilities.models.company_brain import ActorType
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session

from keycloak_agent.kg_ingest import (
    ingest_clients,
    ingest_entities,
    ingest_groups,
    ingest_realms,
    ingest_users,
)


@pytest.fixture(autouse=True)
def _governed_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "User", "username": "u"},
            {"id": "b", "node_type": "Realm"},
        ],
        [{"source": "a", "target": "b", "relationship": "inRealm"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "keycloak-agent"
    assert c.nodes.values["a"]["domain"] == "keycloak"
    assert c.changes.edges == [("a", "b", {"relationship": "inRealm"})]


def test_ingest_realms_maps_realm():
    c = _FakeClient()
    res = ingest_realms(
        [{"realm": "homelab", "displayName": "Homelab", "enabled": True}],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["keycloak:realm:homelab"]
    assert node["node_type"] == "Realm"
    assert node["realmName"] == "homelab"
    assert node["externalToolId"] == "homelab"


def test_ingest_users_maps_user_and_realm_link():
    c = _FakeClient()
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


def test_retired_node_type_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities(
            [{"id": "retired", "type": "RetiredAlias"}],
            client=_FakeClient(),
        )


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
