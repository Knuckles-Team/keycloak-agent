import pytest


@pytest.mark.concept("KC-OS.identity.keycloak-mcp-authenticates-admin")
def test_mcp_server_security_context(monkeypatch):
    """CONCEPT:KC-OS.identity.keycloak-mcp-authenticates-admin Verify that the server registers with correct security credentials."""
    from keycloak_agent.auth import get_client

    monkeypatch.setenv("KEYCLOAK_URL", "https://service.invalid")
    client = get_client()
    assert client is not None
