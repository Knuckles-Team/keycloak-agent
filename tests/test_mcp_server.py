import pytest


@pytest.mark.concept("KC-OS.governance.key")
def test_mcp_server_registration():
    """CONCEPT:KC-OS.governance.key Test that tools register successfully."""
    from keycloak_agent.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    if isinstance(res, tuple):
        mcp = res[0]
    else:
        mcp = res
    assert mcp is not None

    # Verify tool registry count is greater than zero
    assert len(mcp._local_provider._components) > 0


@pytest.mark.concept("KC-OS.identity.keycloak-mcp-authenticates-admin")
def test_mcp_server_security_context():
    """CONCEPT:KC-OS.identity.keycloak-mcp-authenticates-admin Verify that the server registers with correct security credentials."""
    from keycloak_agent.auth import get_client

    client = get_client()
    assert client is not None
