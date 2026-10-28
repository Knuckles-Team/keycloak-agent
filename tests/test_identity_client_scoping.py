"""Identity-scoped client catalog auto-load."""

import pytest
from agent_connector_sdk.identity import ActorContext, ActorType, use_actor

from keycloak_agent.api.api_client_clients import Api


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003")
def test_client_catalog_returns_only_granted_ids(monkeypatch):
    api = object.__new__(Api)
    calls = []
    monkeypatch.setattr(
        api,
        "request",
        lambda *a, **k: (
            calls.append(a)
            or [
                {"id": "uuid-a", "clientId": "web"},
                {"id": "uuid-b", "clientId": "service"},
            ]
        ),
    )
    actor = ActorContext(
        actor_id="actor",
        actor_type=ActorType.HUMAN,
        tenant_id="tenant",
        roles=("realm:prod", "keycloak-client:uuid-a"),
        authenticated=True,
    )
    with use_actor(actor):
        assert api.list_clients("prod") == [{"id": "uuid-a", "clientId": "web"}]
    assert len(calls) == 1


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003")
def test_unentitled_realm_never_reaches_provider(monkeypatch):
    api = object.__new__(Api)
    calls = []
    monkeypatch.setattr(api, "request", lambda *a, **k: calls.append(a))
    actor = ActorContext(
        actor_id="actor",
        actor_type=ActorType.HUMAN,
        tenant_id="tenant",
        roles=("realm:prod", "keycloak-client:*"),
        authenticated=True,
    )
    with use_actor(actor), pytest.raises(PermissionError):
        api.list_clients("other")
    assert not calls


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003")
@pytest.mark.parametrize("catalog", [[{}], [None], [{"id": ""}], {"id": "uuid-a"}])
def test_malformed_client_catalog_refuses(monkeypatch, catalog):
    api = object.__new__(Api)
    monkeypatch.setattr(api, "request", lambda *a, **k: catalog)
    actor = ActorContext(
        actor_id="actor",
        actor_type=ActorType.HUMAN,
        tenant_id="tenant",
        roles=("realm:prod", "keycloak-client:*"),
        authenticated=True,
    )
    with use_actor(actor), pytest.raises(ValueError, match="malformed"):
        api.list_clients("prod")


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003")
def test_missing_identity_never_reaches_provider(monkeypatch):
    api = object.__new__(Api)
    calls = []
    monkeypatch.setattr(api, "request", lambda *a, **k: calls.append(a))
    with pytest.raises(PermissionError):
        api.list_clients("prod")
    assert not calls
