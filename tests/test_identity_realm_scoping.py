"""Identity-scoped realm auto-load (CONCEPT:AU-OS.identity.identity-scoped-resource-autoload).

The caller's entitled Keycloak realms auto-load in ``list_realms``; a
non-entitled realm name is denied in ``get_realm``. Tests the
filtering/enforcement logic with the entitlement source mocked (the resolver
itself is tested in agent-utilities).
"""

import pytest

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


def test_missing_resolver_degrades_to_full_list(monkeypatch):
    """A broken/absent import of the shared resolver fails open to the full list."""
    import builtins

    real_import = builtins.__import__

    def _blocked_import(name, *args, **kwargs):
        if name == "agent_utilities.security.entitlements":
            raise ImportError("simulated: resolver not available")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)
    assert api_client_realms._entitled("realm", ["a", "b"]) == ["a", "b"]
