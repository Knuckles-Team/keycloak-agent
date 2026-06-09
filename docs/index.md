# keycloak-agent

Keycloak Identity and Access Management **MCP Server + Agent** for the
agent-utilities ecosystem — typed, deterministic tools for realms, users, and OIDC
clients, plus an optional Pydantic-AI agent server.

!!! info "Official documentation"
    This site is the canonical reference for `keycloak-agent`, maintained alongside
    every release.

[![PyPI](https://img.shields.io/pypi/v/keycloak-agent)](https://pypi.org/project/keycloak-agent/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/keycloak-agent)](https://github.com/Knuckles-Team/keycloak-agent/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/keycloak-agent)

## Overview

`keycloak-agent` wraps the Keycloak Admin REST API with a typed, deterministic MCP
tool surface and ships an optional agent server. It provides:

- **`Api`** — a dynamic facade (`keycloak_agent.api_client.Api`) composed of realm,
  user, and OIDC-client domain modules over the Keycloak Admin REST API.
- **MCP tools** — realm, user, and client operations registered under the `KEY`
  tag, with runtime toolset selection to keep the model's context window lean.
- **An agent server** — an optional Pydantic-AI `keycloak-agent` that consumes the
  MCP tools for autonomous identity operations.

The server registers read operations that work as soon as the connection is
configured; administrative writes execute only when valid credentials are present.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP server and agent, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` client, and the CLI.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy Keycloak with Docker.
- :material-sitemap: **[Architecture](overview.md)** — the dynamic facade and tool surface.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:KEY-*` registry.

</div>

## Quick start

```bash
pip install "keycloak-agent[mcp]"
keycloak-mcp                       # stdio MCP server (default transport)
```

Connect it to a Keycloak server:

```bash
export KEYCLOAK_URL=http://your-keycloak:8080
export KEYCLOAK_USERNAME=admin
export KEYCLOAK_PASSWORD=admin_secure_password
export KEYCLOAK_REALM=master
keycloak-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, the agent server, reverse
proxy, DNS).
