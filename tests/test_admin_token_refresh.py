"""Service-account admin auth: per-request bearer + 401 re-mint/retry.

CONCEPT:KEY-003 — keycloak-mcp authenticates to the admin API with a
self-refreshing client-credentials token instead of a baked static token.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from keycloak_agent.api.api_client_base import ApiClientBase


class _FakeProvider:
    """Stand-in for ClientCredentialsTokenProvider; records get_token calls."""

    def __init__(self) -> None:
        self.calls: list[bool] = []
        self._n = 0

    def get_token(self, *, force: bool = False) -> str:
        self.calls.append(force)
        self._n += 1
        return f"tok{self._n}"


def _base(provider) -> ApiClientBase:
    obj = object.__new__(ApiClientBase)
    obj.base_url = "http://kc/"
    obj._token_provider = provider
    obj._session = MagicMock()
    return obj


def _resp(status: int, text: str = "{}"):
    r = MagicMock()
    r.status_code = status
    r.text = text
    r.json.return_value = {"ok": True}
    return r


def test_request_attaches_minted_bearer():
    provider = _FakeProvider()
    api = _base(provider)
    api._session.request.return_value = _resp(200)

    api.request("GET", "/admin/realms")

    assert provider.calls == [False]  # minted without forcing a refresh
    _, kwargs = api._session.request.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer tok1"


def test_request_remints_and_retries_once_on_401():
    provider = _FakeProvider()
    api = _base(provider)
    api._session.request.side_effect = [_resp(401, "expired"), _resp(200)]

    out = api.request("GET", "/admin/realms")

    assert provider.calls == [False, True]  # retry forced a fresh token
    assert api._session.request.call_count == 2
    assert out == {"ok": True}


def test_no_provider_keeps_legacy_path():
    api = _base(None)
    api._session.request.return_value = _resp(200)

    api.request("GET", "/admin/realms")

    _, kwargs = api._session.request.call_args
    assert "Authorization" not in kwargs["headers"]
    api._session.request.assert_called_once()
