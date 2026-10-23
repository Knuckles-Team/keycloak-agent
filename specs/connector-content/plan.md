# CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `keycloak-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `keycloak_agent` from it.
