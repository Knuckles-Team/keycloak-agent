"""EH-410: Keycloak user/admin events enter the graph pseudonymized."""

from __future__ import annotations

from typing import Any

from agent_utilities.security.audit_pseudonym import AuditPseudonymizer

import keycloak_agent.kg_ingest as kg

PSEUDO = AuditPseudonymizer(b"test-only-audit-key")


def _capture(monkeypatch) -> dict[str, dict[str, Any]]:
    written: dict[str, dict[str, Any]] = {}

    def capture(entities, relationships=None, **_kwargs):
        written.update({entity["id"]: entity for entity in entities})
        return {"nodes": len(entities), "edges": len(relationships or [])}

    monkeypatch.setattr(kg, "ingest_entities", capture)
    return written


def test_user_events_are_pseudonymized_authentication_events(monkeypatch):
    written = _capture(monkeypatch)
    event = {
        "type": "LOGIN_ERROR",
        "time": 1700000000000,
        "realmId": "homelab",
        "clientId": "graph-os",
        "userId": "4b5d-alice-uuid",
        "sessionId": "sess-1",
        "ipAddress": "198.51.100.23",
        "error": "invalid_user_credentials",
        "details": {"username": "alice", "redirect_uri": "https://secret.example"},
    }
    res = kg.ingest_security_events([event], realm="homelab", pseudonymizer=PSEUDO)
    assert res == {"nodes": 2, "edges": 1}
    (node,) = [n for n in written.values() if n["node_type"] == "AuthenticationEvent"]
    assert node["type"] == "LOGIN_ERROR" and node["error"] == "invalid_user_credentials"
    assert node["userId"] == PSEUDO.identity("4b5d-alice-uuid")
    assert node["details_username"] == PSEUDO.identity("alice")
    assert node["ipAddress"] == "198.51.100.0/24"
    rendered = repr(written)
    for leaked in ("alice", "198.51.100.23", "secret.example", "sess-1"):
        assert leaked not in rendered, leaked


def test_admin_events_hash_resource_paths_and_actor(monkeypatch):
    written = _capture(monkeypatch)
    event = {
        "operationType": "DELETE",
        "resourceType": "USER",
        "time": 1700000000001,
        "resourcePath": "users/4b5d-alice-uuid",
        "authDetails": {"userId": "admin-uuid", "ipAddress": "2001:db8:1:2::9"},
        "representation": '{"username": "alice"}',
    }
    kg.ingest_security_events(
        [event], realm="homelab", admin=True, pseudonymizer=PSEUDO
    )
    (node,) = [n for n in written.values() if n["node_type"] == "AdminAuditEvent"]
    assert node["resourcePath"] == PSEUDO.secret_path("users/4b5d-alice-uuid")
    assert node["authDetails_userId"] == PSEUDO.identity("admin-uuid")
    assert node["authDetails_ipAddress"] == "2001:db8:1::/48"
    assert "alice" not in repr(written) and "representation" not in node


def test_the_same_event_maps_to_the_same_node(monkeypatch):
    written = _capture(monkeypatch)
    event = {"type": "LOGIN", "time": 1, "userId": "u"}
    kg.ingest_security_events([event, dict(event)], realm="r", pseudonymizer=PSEUDO)
    assert (
        len([n for n in written.values() if n["node_type"] == "AuthenticationEvent"])
        == 1
    )
