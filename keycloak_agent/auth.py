"""CONCEPT:KC-OS.identity.keycloak-mcp-authenticates-admin Identity credentials loader and session manager."""

from agent_connector_sdk.utilities import get_logger
from agent_connector_sdk.config import setting
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile
from agent_connector_sdk.auth.client_credentials import ClientCredentialsTokenProvider

from keycloak_agent.api_client import Api

logger = get_logger(__name__)


def get_client(tls_profile: ResolvedTLSProfile | None = None) -> Api:
    """Get authenticated client for keycloak_agent."""
    base_url = setting("KEYCLOAK_URL", "")
    token = setting("KEYCLOAK_TOKEN", "")
    username = setting("KEYCLOAK_AGENT_USERNAME", "")
    password = setting("KEYCLOAK_AGENT_PASSWORD", "")
    client_id = setting("KEYCLOAK_CLIENT_ID", "")
    client_secret = setting("KEYCLOAK_CLIENT_SECRET", "")
    realm = setting("KEYCLOAK_REALM", "master")

    if not base_url:
        raise RuntimeError("KEYCLOAK_URL is required")
    profile = tls_profile or resolve_tls_profile("keycloak_agent")

    # Preferred admin auth: a service-account client whose bearer is minted from
    # Keycloak's token endpoint and auto-refreshed (cache + pre-expiry refresh +
    # 401 re-mint via ApiClientBase). Static KEYCLOAK_TOKEN / basic-auth remain a
    # explicit alternatives when the operator supplies those credentials.
    token_provider = None
    if client_id and client_secret:
        token_url = (
            f"{base_url.rstrip('/')}/realms/{realm}/protocol/openid-connect/token"
        )
        audience = setting("KEYCLOAK_CLIENT_AUDIENCE", "") or client_id
        token_provider = ClientCredentialsTokenProvider(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
            audience=audience,
        )

    return Api(
        base_url=base_url,
        token=token,
        username=username,
        password=password,
        tls_profile=profile,
        token_provider=token_provider,
    )
