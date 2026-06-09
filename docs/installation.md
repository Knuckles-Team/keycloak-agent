# Installation

`keycloak-agent` is a standard Python package and a prebuilt container image. Pick
the path that matches how you want to run it.

## Requirements

- **Python 3.11 – 3.14**.
- A reachable **Keycloak** server with an administrative account — see
  [Backing Platform](platform.md) to deploy one locally.

## From PyPI (recommended)

```bash
pip install keycloak-agent
```

### Optional extras

The base install is intentionally minimal. Install the extra for what you need:

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "keycloak-agent[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "keycloak-agent[agent]"` | Pydantic-AI agent + Logfire tracing |
| `all` | `pip install "keycloak-agent[all]"` | Everything above |
| `test` | `pip install "keycloak-agent[test]"` | `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |

```bash
# Typical: run the MCP server and the agent server
pip install "keycloak-agent[all]"
```

## From source

```bash
git clone https://github.com/Knuckles-Team/keycloak-agent.git
cd keycloak-agent
pip install -e ".[all]"          # editable install with every extra
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[all]"
uv run keycloak-mcp
```

## Prebuilt Docker image

A multi-stage, slim image is published on every release (installs
`keycloak-agent[all]`, entrypoint `keycloak-mcp`):

```bash
docker pull knucklessg1/keycloak-agent:latest

docker run --rm -i \
  -e KEYCLOAK_URL=http://your-keycloak:8080 \
  -e KEYCLOAK_USERNAME=admin \
  -e KEYCLOAK_PASSWORD=admin_secure_password \
  -e KEYCLOAK_REALM=master \
  knucklessg1/keycloak-agent:latest        # stdio transport (default)
```

For an HTTP server with a published port, see [Deployment](deployment.md).

## Verify the install

```bash
keycloak-mcp --help
python -c "import keycloak_agent; print(keycloak_agent.__version__)"
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP server and agent behind Caddy + DNS.
- **[Usage](usage.md)** — call the tools, the API, and the CLI.
- **[Configuration](deployment.md#configuration-environment)** — every environment variable.
