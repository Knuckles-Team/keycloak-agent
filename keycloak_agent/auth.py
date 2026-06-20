"""CONCEPT:KEY-003 Identity credentials loader and session manager."""

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.config import setting
from agent_utilities.mcp.client_credentials import ClientCredentialsTokenProvider

from keycloak_agent.api_client import Api

logger = get_logger(__name__)


def get_client() -> Api:
    """Get authenticated client for keycloak_agent."""
    base_url = setting("KEYCLOAK_URL") or setting("KEYCLOAK_AGENT_BASE_URL", "")
    token = setting("KEYCLOAK_TOKEN", "")
    username = setting("KEYCLOAK_AGENT_USERNAME", "")
    password = setting("KEYCLOAK_AGENT_PASSWORD", "")
    verify = setting("KEYCLOAK_AGENT_SSL_VERIFY", True)
    client_id = setting("KEYCLOAK_CLIENT_ID", "")
    client_secret = setting("KEYCLOAK_CLIENT_SECRET", "")
    realm = setting("KEYCLOAK_REALM", "master")

    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost"

    # Preferred admin auth: a service-account client whose bearer is minted from
    # Keycloak's token endpoint and auto-refreshed (cache + pre-expiry refresh +
    # 401 re-mint via ApiClientBase). Static KEYCLOAK_TOKEN / basic-auth remain a
    # fallback for tests and legacy deploys.
    token_provider = None
    if client_id and client_secret:
        token_url = (
            f"{base_url.rstrip('/')}/realms/{realm}/protocol/openid-connect/token"
        )
        token_provider = ClientCredentialsTokenProvider(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
            verify=verify,
        )

    return Api(
        base_url=base_url,
        token=token,
        username=username,
        password=password,
        verify=verify,
        token_provider=token_provider,
    )
