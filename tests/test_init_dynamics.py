import pytest


@pytest.mark.concept("KEY-001")
def test_init_dynamics():
    import keycloak_agent

    assert keycloak_agent._MCP_AVAILABLE is True
