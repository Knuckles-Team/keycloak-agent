"""Every action a keycloak tool advertises must be a real generated client method."""

import re
from pathlib import Path

from keycloak_agent.api.api_client_base import ApiClientBase

MCP_DIR = Path(__file__).parent.parent / "keycloak_agent" / "mcp"
# Actions served by hand-written client methods rather than the generated ones.
HAND_WRITTEN = {
    "list_realms",
    "get_realm",
    "create_realm",
    "delete_realm",
    "list_users",
    "get_user",
    "create_user",
    "delete_user",
    "reset_password",
    "list_users_by_user_id_groups",
    "list_clients",
    "get_client",
    "create_client",
    "delete_client",
    "get_client_secret",
    "regenerate_client_secret",
    "regenerate_client_secret_by_client_id",
    "find_client_by_client_id",
}


def test_advertised_actions_exist():
    ApiClientBase._load_schema()
    known = set(ApiClientBase._methods) | HAND_WRITTEN
    missing = []
    for path in sorted(MCP_DIR.glob("mcp_*.py")):
        text = path.read_text()
        for desc in re.findall(
            r'description="Action to perform\. e\.g\. ([^"]+)"', text
        ):
            for name in re.findall(r"'([a-z_A-Z]+)'", desc):
                if name not in known:
                    missing.append((path.name, name))
    assert not missing, missing
