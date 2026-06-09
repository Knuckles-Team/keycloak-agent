# Usage — API / CLI / MCP

`keycloak-agent` exposes the same capability three ways: as **MCP tools** an agent
calls, as a **Python API** (`Api`) you import, and as **console scripts**. The full
tool surface and the dynamic facade are described in [Overview](overview.md).

## As an MCP server

Once [deployed](deployment.md), the server registers Keycloak administration tools
under the `KEY` tag. Reads work as soon as the connection is configured;
administrative writes require valid admin credentials.

| Group | Tools |
|---|---|
| Realms | `list_realms`, `get_realm`, `create_realm`, `delete_realm` |
| Users | `list_users`, `get_user`, `create_user`, `delete_user`, `reset_password` |
| OIDC clients | `list_clients`, `get_client`, `create_client`, `get_client_secret`, `find_client_by_client_id`, `delete_client` |

Example agent prompts that map onto these tools:

- *"List the users in the `master` realm"* → `list_users`
- *"Provision an OIDC client `grafana` in realm `apps`"* → `create_client`
- *"Retrieve the client secret for `grafana`"* → `get_client_secret`

This server supports runtime toolset selection (`--tools` / `--toolsets`,
`MCP_ENABLED_TOOLS` / `MCP_DISABLED_TAGS`, or request headers / query parameters) so
you can restrict the exposed surface and keep the model's context window lean.

## As a Python API

`Api` is a dynamic facade composed of the realm, user, and OIDC-client domain
modules over the Keycloak Admin REST API.

```python
from keycloak_agent.api_client import Api

api = Api(
    url="http://your-keycloak:8080",
    username="admin",
    password="admin_secure_password",
    realm="master",
)

# Reads
realms = api.list_realms()
users = api.list_users("master", search="alice")
clients = api.list_clients("master")
secret = api.get_client_secret("master", clients[0]["id"])
```

Build a client straight from the environment:

```python
from keycloak_agent.auth import get_client
api = get_client()        # reads KEYCLOAK_* from the environment / .env
```

### Writes

Administrative writes provision realm resources:

```python
api.create_realm("apps")
api.create_user("apps", username="alice", email="alice@example.com", enabled=True)
api.create_client("apps", client_id="grafana", redirect_uris=["https://grafana.example.com/*"])
api.reset_password("apps", user_id, password="initial-secret", temporary=True)
```

## As a CLI

Two console scripts are installed:

```bash
keycloak-mcp --help          # the MCP server (stdio / streamable-http / sse)
keycloak-agent --help        # the optional Pydantic-AI agent server
```

Launch the MCP server directly as a module:

```bash
python -m keycloak_agent.mcp_server
```

The [agent server](deployment.md#run-the-agent-server) consumes the MCP tools for
autonomous identity operations; point it at a running MCP server with `--mcp-url`.
