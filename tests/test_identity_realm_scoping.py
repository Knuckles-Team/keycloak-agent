"""Identity-scoped realm auto-load (CONCEPT:AU-OS.identity.identity-scoped-resource-autoload).

The caller's entitled Keycloak realms auto-load in ``list_realms``; a
non-entitled realm name is denied in ``get_realm``. Tests the
filtering/enforcement logic with the entitlement source mocked (the resolver
itself is tested in scion-sdk).
"""

import pytest
from scion_sdk.identity import ANONYMOUS_ACTOR, use_actor

from keycloak_agent.api import api_client_realms
from keycloak_agent.api.api_client_realms import Api


def _client(monkeypatch, entitled):
    monkeypatch.setattr(
        api_client_realms,
        "_entitled",
        lambda namespace, names: [n for n in names if n in entitled],
    )
    api = object.__new__(Api)  # bypass ApiClientBase.__init__ (no network)
    return api


def test_list_realms_filters_to_entitled(monkeypatch):
    api = _client(monkeypatch, {"prod"})
    monkeypatch.setattr(
        api,
        "request",
        lambda *a, **k: [{"realm": "prod"}, {"realm": "dev"}],
    )
    result = api.list_realms()
    assert [r["realm"] for r in result] == ["prod"]


def test_get_realm_denies_non_entitled(monkeypatch):
    api = _client(monkeypatch, {"prod"})
    with pytest.raises(PermissionError):
        api.get_realm("dev")


def test_get_realm_allows_entitled(monkeypatch):
    api = _client(monkeypatch, {"prod"})
    monkeypatch.setattr(api, "request", lambda *a, **k: {"realm": "prod"})
    assert api.get_realm("prod") == {"realm": "prod"}


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002")
def test_missing_resolver_refuses_before_loading(monkeypatch):
    """A missing resolver never grants every realm."""
    import builtins

    real_import = builtins.__import__

    def _blocked_import(name, *args, **kwargs):
        if name == "scion_sdk.entitlements":
            raise ImportError("simulated: resolver not available")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)
    with pytest.raises(PermissionError, match="resolver unavailable"):
        api_client_realms._entitled("realm", ["a", "b"])


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002")
def test_real_authenticated_identity_scopes_the_catalog(monkeypatch):
    from scion_sdk.identity import ActorContext, ActorType, use_actor

    api = object.__new__(Api)
    calls = []
    monkeypatch.setattr(
        api,
        "request",
        lambda *a, **k: calls.append(a) or [{"realm": "prod"}, {"realm": "dev"}],
    )
    actor = ActorContext(
        actor_id="alice",
        actor_type=ActorType.HUMAN,
        tenant_id="tenant",
        roles=("realm:prod",),
        authenticated=True,
    )
    with use_actor(actor):
        assert api.list_realms() == [{"realm": "prod"}]
        with pytest.raises(PermissionError):
            api.get_realm("dev")
    assert len(calls) == 1


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002")
def test_unauthenticated_caller_never_reaches_provider(monkeypatch):
    # An unbound library call is the SYSTEM actor; the served transport refuses
    # anonymous callers. The anonymous actor must still see no realm.
    api = object.__new__(Api)
    monkeypatch.setattr(api, "request", lambda *a, **k: [{"realm": "prod"}])
    with use_actor(ANONYMOUS_ACTOR):
        assert api.list_realms() == []


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002")
@pytest.mark.parametrize("catalog", [[{}], [None], [{"realm": ""}], {"realm": "prod"}])
def test_malformed_catalog_never_returns_unscoped_data(monkeypatch, catalog):
    api = _client(monkeypatch, {"prod"})
    monkeypatch.setattr(api, "request", lambda *a, **k: catalog)
    with pytest.raises(ValueError, match="malformed"):
        api.list_realms()


@pytest.mark.spec("CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002")
def test_forged_or_unscoped_identity_never_reaches_provider(monkeypatch):
    from scion_sdk.identity import ActorContext, ActorType, use_actor

    api = object.__new__(Api)
    calls = []
    monkeypatch.setattr(api, "request", lambda *a, **k: calls.append(a))
    for authenticated, tenant in ((False, "tenant"), (True, "")):
        actor = ActorContext(
            actor_id="alice",
            actor_type=ActorType.HUMAN,
            tenant_id=tenant,
            roles=("realm:*",),
            authenticated=authenticated,
        )
        with use_actor(actor), pytest.raises(PermissionError):
            api.list_realms()
    assert not calls
