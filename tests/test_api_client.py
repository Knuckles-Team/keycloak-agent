import pytest


@pytest.mark.concept("AU-KG.ontology.package-scoped-concept")
def test_api_client_basic_mock(mock_ctx):
    """CONCEPT:AU-KG.ontology.package-scoped-concept Test basic mock initialization of client facade."""
    assert mock_ctx is not None
    assert hasattr(mock_ctx, "info")


@pytest.mark.concept("AU-KG.ontology.package-scoped-concept")
def test_api_client_endpoints(mock_ctx):
    """CONCEPT:AU-KG.ontology.package-scoped-concept Verify endpoint configuration on dynamic client."""
    from keycloak_agent.auth import get_client

    client = get_client()
    assert client is not None
    assert hasattr(client, "request")
