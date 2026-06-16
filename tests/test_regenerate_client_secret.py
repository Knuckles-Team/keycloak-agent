"""Keycloak client-secret regeneration (rotation support)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from keycloak_agent.api.api_client_clients import Api


def _api() -> Api:
    """Build an Api without running ApiClientBase.__init__ (no network)."""
    return object.__new__(Api)


def test_regenerate_client_secret_posts_to_endpoint():
    api = _api()
    api.request = MagicMock(return_value={"type": "secret", "value": "new"})
    out = api.regenerate_client_secret("homelab", "uuid-1")
    api.request.assert_called_once_with(
        "POST", "/admin/realms/homelab/clients/uuid-1/client-secret"
    )
    assert out["value"] == "new"


def test_regenerate_by_client_id_resolves_then_posts():
    api = _api()
    api.find_client_by_client_id = MagicMock(return_value={"id": "uuid-9"})
    api.request = MagicMock(return_value={"type": "secret", "value": "rotated"})
    out = api.regenerate_client_secret_by_client_id("homelab", "mcp-multiplexer")
    api.find_client_by_client_id.assert_called_once_with("homelab", "mcp-multiplexer")
    api.request.assert_called_once_with(
        "POST", "/admin/realms/homelab/clients/uuid-9/client-secret"
    )
    assert out["client_uuid"] == "uuid-9" and out["value"] == "rotated"


def test_regenerate_by_client_id_raises_when_not_found():
    api = _api()
    api.find_client_by_client_id = MagicMock(return_value=None)
    with pytest.raises(ValueError, match="not found"):
        api.regenerate_client_secret_by_client_id("homelab", "ghost")
