# Keycloak Agent
## MCP Server | Agent

[![PyPI - Version](https://img.shields.io/pypi/v/keycloak-agent)](https://pypi.org/project/keycloak-agent/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/keycloak-agent)](https://github.com/Knuckles-Team/keycloak-agent/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/keycloak-agent)

Keycloak Identity and Access Management **MCP Server + Agent** for the agent-utilities ecosystem. Built with the standardized dynamic-facade architecture, custom API routing, and FastMCP tool registration.

> **Documentation** — Installation, deployment, usage across the API, CLI, and MCP
> interfaces, and guidance for provisioning the Keycloak platform are maintained in
> the [official documentation](https://knuckles-team.github.io/keycloak-agent/).

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [MCP Tools](#mcp-tools)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Keycloak MCP provides a high-performance, model-optimized interface to Keycloak capabilities. It isolates the model from underlying API transport complexity, ensuring safe, idempotent, and highly traceable system interactions.

---

## Features

- **Dynamic Facade Orchestration**: Integrates multi-inheritance clients cleanly under a single facade.
- **Battle-Tested Resilience**: Out-of-the-box credential authentication, connection polling, and request retry strategies.
- **FastMCP Declarative Tools**: Fast, native schema registration with full inline validation.
- **Complete Test Intent Diversity**: Deep, automated unit, integration, and mock tests ensuring high code coverage.

---

## ⚙️ Dynamic Tool Selection & Visibility

This MCP server supports dynamic toolset selection and visibility filtering at runtime. This allows you to restrict the set of exposed tools in order to prevent blowing up the LLM's context window.

You can configure tool filtering via multiple input channels:

- **CLI Arguments:** Pass `--tools` or `--toolsets` (or their disabled counterparts `--disabled-tools` and `--disabled-toolsets`) during startup.
- **Environment Variables:** Define standard environment variables:
  - `MCP_ENABLED_TOOLS` / `MCP_DISABLED_TOOLS`
  - `MCP_ENABLED_TAGS` / `MCP_DISABLED_TAGS`
- **HTTP SSE Request Headers:** Pass custom headers during transport initialization:
  - `x-mcp-enabled-tools` / `x-mcp-disabled-tools`
  - `x-mcp-enabled-tags` / `x-mcp-disabled-tags`
- **HTTP SSE Request Query Parameters:** Append query parameters directly to your transport connection URL:
  - `?tools=tool1,tool2`
  - `?tags=tag1`

When query strings or parameters are supplied, an LLM-free **Knowledge Graph resolution layer** (using `DynamicToolOrchestrator`) matches query intents against known tool tags, names, or descriptions, with safe fallback and automated 24-hour background cache refreshing.


---

## Installation

Pick the extra that matches what you want to run:

| Extra | Installs | Use when |
|-------|----------|----------|
| `keycloak-agent[mcp]` | Connector-focused MCP server (`agent-utilities[mcp]` — FastMCP/FastAPI + `epistemic-graph[full]`) | You only run the **MCP server** (smallest install / image) |
| `keycloak-agent[agent]` | Agent runtime (`agent-utilities[agent-runtime,logfire]` — model orchestration + `epistemic-graph[full]`) | You run the **integrated agent** |
| `keycloak-agent[all]` | Everything (`mcp` + `agent` + `logfire`) | Development / both surfaces |

```bash
# Connector-focused MCP server (includes the shared graph engine)
uv pip install "keycloak-agent[mcp]"

# Agent runtime (adds model orchestration to the shared graph engine)
uv pip install "keycloak-agent[agent]"

# Everything (development)
uv pip install "keycloak-agent[all]"      # or: python -m pip install "keycloak-agent[all]"
```

### Container images (`:mcp` vs `:agent`)

One multi-stage `docker/Dockerfile` builds two right-sized images, selected by `--target`:

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|
| `example/keycloak-agent:mcp` | `--target mcp` | `keycloak-agent[mcp]` — **connector-focused**, includes `epistemic-graph[full]`; no model-orchestration stack | `keycloak-mcp` |
| `example/keycloak-agent@sha256:<digest>` | `--target agent` (default) | `keycloak-agent[agent]` — **agent runtime**, model orchestration + `epistemic-graph[full]` | `keycloak-agent` |

```bash
docker build --target mcp   -t example/keycloak-agent:mcp    docker/   # connector-focused MCP server
docker build --target agent -t example/keycloak-agent:agent-local docker/   # agent runtime
```

### Knowledge-graph database (`epistemic-graph`)

Both `[mcp]` and `[agent]` carry the **epistemic-graph** engine through the required
Agent Utilities core dependency (`epistemic-graph[full]`). The `[mcp]` extra keeps
the server connector-focused; `[agent]` additionally enables model orchestration. Local
deployments can use the bundled engine. For production or shared state, run
**epistemic-graph as a dedicated database service** and configure the runtime to use it.
Deployment recipes (single-node + Raft HA), connection configuration, and architecture
diagrams are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).

---

## Usage

You can launch the FastMCP server in stdio mode via Python module execution:

```python
import asyncio
from keycloak_agent.mcp_server import get_mcp_instance

async def main():
    mcp = get_mcp_instance()
    # Execute stdio loop or launch server
    print("MCP Server ready.")

if __name__ == "__main__":
    asyncio.run(main())
```

For direct shell launch, execute:

```bash
python -m keycloak_agent.mcp_server
```

---

### MCP Configuration Examples

<!-- MCP-CONFIG-EXAMPLES:START -->

> **Install the connector-focused `[mcp]` extra.** Examples use `keycloak-agent[mcp]` to add
> FastMCP / FastAPI through `agent-utilities[mcp]`; the required Agent Utilities core
> still carries `epistemic-graph[full]`. The `[agent-runtime]` extra additionally
> enables model orchestration.

#### stdio Transport (local IDEs — Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "keycloak-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "keycloak-agent[mcp]",
        "keycloak-mcp"
      ],
      "env": {
        "MCP_TOOL_MODE": "intent",
        "ATTACK_DETECTIONTOOL": "True",
        "AUTHENTICATIONTOOL": "True",
        "CLIENTSTOOL": "True",
        "COMPONENTSTOOL": "True",
        "GROUPSTOOL": "True",
        "IDPSTOOL": "True",
        "INFOTOOL": "True",
        "INGESTTOOL": "True",
        "KEYCLOAK_REALM": "master",
        "ORGANIZATIONSTOOL": "True",
        "REALMSTOOL": "True",
        "ROLESTOOL": "True",
        "USERSTOOL": "True"
      }
    }
  }
}
```

Runtime references require an alias-aware launcher such as GraphOS. Other
launchers must omit those entries and inject the resolved values through their
own runtime secret boundary.

#### Streamable-HTTP Transport (networked / production)

```json
{
  "mcpServers": {
    "keycloak-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "keycloak-agent[mcp]",
        "keycloak-mcp",
        "--transport",
        "streamable-http",
        "--port",
        "8000"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "127.0.0.1",
        "PORT": "8000",
        "MCP_TOOL_MODE": "intent",
        "ATTACK_DETECTIONTOOL": "True",
        "AUTHENTICATIONTOOL": "True",
        "CLIENTSTOOL": "True",
        "COMPONENTSTOOL": "True",
        "GROUPSTOOL": "True",
        "IDPSTOOL": "True",
        "INFOTOOL": "True",
        "INGESTTOOL": "True",
        "KEYCLOAK_REALM": "master",
        "ORGANIZATIONSTOOL": "True",
        "REALMSTOOL": "True",
        "ROLESTOOL": "True",
        "USERSTOOL": "True"
      }
    }
  }
}
```

Alternatively, connect to a pre-deployed Streamable-HTTP instance by `url`:

```json
{
  "mcpServers": {
    "keycloak-mcp": {
      "url": "http://localhost:8000/keycloak-mcp/mcp"
    }
  }
}
```

Run a reviewed container image as a least-privilege stdio child (no
listener or published port):

```bash
docker run -i --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --pids-limit=256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
  -e TRANSPORT=stdio \
  -e MCP_TOOL_MODE=intent \
  -e ATTACK_DETECTIONTOOL=True \
  -e AUTHENTICATIONTOOL=True \
  -e CLIENTSTOOL=True \
  -e COMPONENTSTOOL=True \
  -e GROUPSTOOL=True \
  -e IDPSTOOL=True \
  -e INFOTOOL=True \
  -e INGESTTOOL=True \
  -e KEYCLOAK_REALM=master \
  -e ORGANIZATIONSTOOL=True \
  -e REALMSTOOL=True \
  -e ROLESTOOL=True \
  -e USERSTOOL=True \
  registry.example.invalid/keycloak-agent@sha256:<digest> keycloak-mcp
```

For containerized network HTTP, supply an authenticated TLS ingress (or
direct server TLS), exact `MCP_ALLOWED_HOSTS`, and an exact trusted-proxy
CIDR policy through the operator-owned deployment profile. The generator
does not emit an unauthenticated non-loopback listener.

_Auto-generated from the code-read env surface (`MCP_TOOL_MODE` + package vars) — do not edit._
<!-- MCP-CONFIG-EXAMPLES:END -->

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`keycloak-agent` can run as a local stdio process or container, or behind a remote
network boundary. The
[Deployment guide](https://knuckles-team.github.io/keycloak-agent/deployment/) carries
the detailed transport contract.

- **Local container** — launch a reviewed immutable image as a least-privilege
  stdio child with no listener or published port.
- **Remote URL** — connect through an operator-supplied authenticated HTTPS
  ingress. Keep its URL, outbound identity references, trust profile, and exact
  `MCP_ALLOWED_HOSTS` in `AgentConfig`.
<!-- END GENERATED: additional-deployment-options -->

## Contributing

Please audit all code changes against the repository's contribution and review requirements, and run:

```bash
pre-commit run --all-files
```

---

## Documentation

The complete documentation is published as the
[official documentation site](https://knuckles-team.github.io/keycloak-agent/) and is
the recommended reference for installation, deployment, and day-to-day operation.

| Page | Contents |
|---|---|
| [Installation](https://knuckles-team.github.io/keycloak-agent/installation/) | pip, source, extras, prebuilt Docker image |
| [Deployment](https://knuckles-team.github.io/keycloak-agent/deployment/) | run the MCP server and agent, Compose, Caddy + Technitium, env config |
| [Usage](https://knuckles-team.github.io/keycloak-agent/usage/) | the MCP tools, the `Api` client, the CLI |
| [Backing Platform](https://knuckles-team.github.io/keycloak-agent/platform/) | deploy Keycloak with Docker |
| [Overview](https://knuckles-team.github.io/keycloak-agent/overview/) | the dynamic facade and tool surface |
| [Concepts](https://knuckles-team.github.io/keycloak-agent/concepts/) | concept registry (`CONCEPT:KEY-*`) |

`AGENTS.md` is the canonical contributor/agent guidance.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete details.


<!-- BEGIN agent-utilities-deployment (generated; do not edit between markers) -->

## Deploy with `agent-utilities-deployment`

Provision this package with the consolidated **`agent-utilities-deployment`**
workflow. It selects an installed-package, editable-source, or immutable-container
path; records only runtime secret and TLS-profile references in `AgentConfig`; and
runs doctor, registration, policy, observability, and rollback gates. Ask your agent
to **"deploy `keycloak-agent` with agent-utilities-deployment"**.

| Install mode | Command |
|------|---------|
| Installed package | `uv tool install "keycloak-agent[mcp]"`, then run `keycloak-mcp` |
| Editable source | `uv pip install -e ".[agent]"`, then run `keycloak-mcp` |
| Immutable container | deploy `registry.example.invalid/keycloak-agent@sha256:<digest>` through the operator-selected orchestrator |

The repository embeds no deployment profile, credential value, certificate path, or
environment-specific endpoint. Supply those at runtime through `AgentConfig` and the
configured secret provider.

<!-- END agent-utilities-deployment -->

<!-- GOVERNED-CAPABILITY:START -->
## Governed capability contract

This package ships a compact canonical skill surface with specialist procedures
kept as referenced workflows. The current MCP tools, skill metadata,
`connector_manifest.yml`, ontology, mappings, shapes, fixtures, migrations,
tool-schema fingerprints, and certification metadata form one versioned
capability contract. Validate them together; do not rely on stale tool names or
historical per-task skill wrappers.

Runtime endpoints, credentials, certificate trust, tenant identity, retention,
and observability policy are deployment inputs and are never packaged values.
See [Configuration, trust, and privacy](docs/configuration.md) before enabling a
network transport, connector ingestion, GraphOS delegation, or trace export.
<!-- GOVERNED-CAPABILITY:END -->

## Environment Variables

<!-- ENV-VARS-TABLE:START -->

#### Package environment variables

| Variable | Example | Description |
|----------|---------|-------------|
| `KEYCLOAK_URL` | — | Keycloak base Admin URL (required) |
| `KEYCLOAK_REALM` | `master` | Keycloak realm name |
| `TLS_PROFILE` | `private-pki` | TLS verification is mandatory. Select a named runtime profile from AgentConfig. |
| `TLS_PROFILES_REF` | `secret://runtime/tls-profiles` |  |
| `KEYCLOAK_AGENT_USERNAME` | — | Admin account username |
| `KEYCLOAK_AGENT_PASSWORD` | secret-injected | Admin account password |
| `KEYCLOAK_TOKEN` | secret-injected | Static bearer token |
| `KEYCLOAK_CLIENT_ID` | — | A service-account client whose bearer is minted from Keycloak's token endpoint and auto-refreshed. Set both to use client-credentials instead of basic auth. |
| `KEYCLOAK_CLIENT_SECRET` | secret-injected |  |
| `KEYCLOAK_CLIENT_AUDIENCE` | — | Token audience the minted bearer is scoped to. Defaults to KEYCLOAK_CLIENT_ID (self-audience) when unset. |
| `MCP_TOOL_MODE` | `condensed` | MCP_TOOL_MODE selects which tools are exposed: condensed (default, action-routed tools) \| verbose (1:1 per-operation tools) \| both. |
| `ATTACK_DETECTIONTOOL` | `True` | These names match the authoritative "Toggle Env Var" column in the README MCP tools table (condensed action-routed surface). |
| `AUTHENTICATIONTOOL` | `True` |  |
| `CLIENTSTOOL` | `True` |  |
| `COMPONENTSTOOL` | `True` |  |
| `GROUPSTOOL` | `True` |  |
| `IDPSTOOL` | `True` |  |
| `INFOTOOL` | `True` |  |
| `INGESTTOOL` | `True` |  |
| `ORGANIZATIONSTOOL` | `True` |  |
| `REALMSTOOL` | `True` |  |
| `ROLESTOOL` | `True` |  |
| `USERSTOOL` | `True` |  |

#### Inherited agent-utilities variables (apply to every connector)

| Variable | Example | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | MCP transport: `stdio` \| `streamable-http` \| `sse` |
| `HOST` | `127.0.0.1` | Loopback bind host (set an authenticated ingress explicitly) |
| `PORT` | `8000` | Bind port (HTTP transports) |
| `MCP_ENABLED_TOOLS` | — | Comma-separated tool allow-list |
| `MCP_DISABLED_TOOLS` | — | Comma-separated tool deny-list |
| `MCP_ENABLED_TAGS` | — | Comma-separated tag allow-list |
| `MCP_DISABLED_TAGS` | — | Comma-separated tag deny-list |
| `EUNOMIA_TYPE` | `none` | Authorization mode: `none` \| `embedded` \| `remote` |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` | Embedded Eunomia policy file |
| `EUNOMIA_REMOTE_URL` | — | Remote Eunomia authorization server URL |
| `ENABLE_OTEL` | `False` | Enable OpenTelemetry export |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | OTLP collector endpoint |
| `MCP_CLIENT_AUTH` | — | Outbound MCP child auth: `oidc-client-credentials` \| `basic` \| `none` |
| `OIDC_CLIENT_ID` | — | OIDC client id (service-account auth) |
| `OIDC_CLIENT_SECRET_REF` | `secret://identity/oidc-client-secret` | Runtime secret reference for the OIDC service account |
| `MCP_BASIC_AUTH_USERNAME` | — | HTTP Basic username (`MCP_CLIENT_AUTH=basic`) |
| `MCP_BASIC_AUTH_PASSWORD_REF` | `secret://identity/mcp-basic-password` | Runtime secret reference for HTTP Basic auth (`MCP_CLIENT_AUTH=basic`) |
| `DEBUG` | `False` | Verbose logging |
| `PYTHONUNBUFFERED` | `1` | Unbuffered stdout (recommended in containers) |
| `MCP_URL` | `http://localhost:8000/mcp` | URL of the MCP server the agent connects to |
| `PROVIDER` | `openai` | LLM provider for the agent |
| `MODEL_ID` | `gpt-4o` | Model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_23 package + 23 inherited variable(s). Auto-generated from `.env.example` + the shared agent-utilities set — do not edit._
<!-- ENV-VARS-TABLE:END -->

## Available MCP Tools

<!-- MCP-TOOLS-TABLE:START -->

#### Condensed action-routed tools (`MCP_TOOL_MODE=condensed`)

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `keycloak_agent_attack_detection` | `ATTACK_DETECTIONTOOL` | Manage Keycloak Agent brute force and attack detection operations. |
| `keycloak_agent_authentication` | `AUTHENTICATIONTOOL` | Manage Keycloak Agent authentication and authenticator flow operations. |
| `keycloak_agent_clients` | `CLIENTSTOOL` | Manage Keycloak Agent clients operations. |
| `keycloak_agent_components` | `COMPONENTSTOOL` | Manage Keycloak Agent components operations. |
| `keycloak_agent_groups` | `GROUPSTOOL` | Manage Keycloak Agent groups operations. |
| `keycloak_agent_idps` | `IDPSTOOL` | Manage Keycloak Agent identity providers operations. |
| `keycloak_agent_info` | `INFOTOOL` | Inspect and discover available Keycloak API methods, paths, and signatures at runtime. |
| `keycloak_agent_organizations` | `ORGANIZATIONSTOOL` | Manage Keycloak Agent organizations operations. |
| `keycloak_agent_realms` | `REALMSTOOL` | Manage Keycloak Agent realms operations. |
| `keycloak_agent_roles` | `ROLESTOOL` | Manage Keycloak Agent roles and scope mappings. |
| `keycloak_agent_users` | `USERSTOOL` | Manage Keycloak Agent users operations (Users, Role Mappings, Client Role Mappings). |
| `keycloak_ingest_clients` | `INGESTTOOL` | List clients in a realm and ingest them as ``:Client`` nodes (+ ``:inRealm``). |
| `keycloak_ingest_groups` | `INGESTTOOL` | List groups in a realm and ingest them as ``:Group`` nodes (+ ``:hasSubGroup``). |
| `keycloak_ingest_realms` | `INGESTTOOL` | List all realms and ingest them into epistemic-graph as ``:Realm`` nodes. |
| `keycloak_ingest_users` | `INGESTTOOL` | List users in a realm and ingest them as ``:User`` nodes (+ ``:inRealm`` links). |

#### Verbose 1:1 API-mapped tools (`MCP_TOOL_MODE=verbose` or `both`)

<details>
<summary>17 per-operation tools — one per public API method (click to expand)</summary>

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `keycloak_create_client` | `APITOOL` | Create a client. |
| `keycloak_create_realm` | `APITOOL` | Create a new realm. |
| `keycloak_create_user` | `APITOOL` | Create a user. |
| `keycloak_delete_client` | `APITOOL` | Delete a client. |
| `keycloak_delete_realm` | `APITOOL` | Delete a realm. |
| `keycloak_delete_user` | `APITOOL` | Delete a user. |
| `keycloak_find_client_by_client_id` | `APITOOL` | Find a client by its clientId and return it, or None if not found. |
| `keycloak_get_client` | `APITOOL` | Get client details. |
| `keycloak_get_client_secret` | `APITOOL` | Get the client secret for a client UUID. |
| `keycloak_get_realm` | `APITOOL` | Get realm details. Denied if the caller is not entitled to the realm. |
| `keycloak_get_user` | `APITOOL` | Get user details. |
| `keycloak_list_clients` | `APITOOL` | List clients in a realm. |
| `keycloak_list_realms` | `APITOOL` | List realms in Keycloak the caller is entitled to. |
| `keycloak_list_users` | `APITOOL` | List users in a realm. |
| `keycloak_regenerate_client_secret` | `APITOOL` | Regenerate (rotate) a confidential client's secret by client UUID. |
| `keycloak_regenerate_client_secret_by_client_id` | `APITOOL` | Regenerate a client's secret by its human clientId (e.g. 'mcp-multiplexer'). |
| `keycloak_reset_password` | `APITOOL` | Reset a user's password. |

</details>

_15 action-routed tool(s) · 17 verbose 1:1 tool(s). Each is enabled unless its `<DOMAIN>TOOL` toggle is set false; `MCP_TOOL_MODE` selects the surface (**`intent` default** — the six verb-tools, granular set loaded on demand · `condensed` action-routed · `verbose` 1:1 · `both`). Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->
