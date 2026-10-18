# Keycloak Agent
## MCP Server | Agent

[![PyPI - Version](https://img.shields.io/pypi/v/keycloak-agent)](https://pypi.org/project/keycloak-agent/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/keycloak-agent)](https://github.com/Knuckles-Team/keycloak-agent/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/keycloak-agent)

Keycloak Identity and Access Management **MCP Server + Agent** for the agent-connector-sdk ecosystem. Built with the standardized dynamic-facade architecture, custom API routing, and FastMCP tool registration.

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

This MCP server supports dynamic toolset selection and visibility filtering at runtime. This allows the operator to restrict the set of exposed tools to prevent blowing up the LLM's context window.

The operator can configure tool filtering via multiple input channels:

- **CLI Arguments:** Pass `--tools` or `--toolsets` (or their disabled counterparts `--disabled-tools` and `--disabled-toolsets`) during startup.
- **Environment Variables:** Define standard environment variables:
  - `MCP_ENABLED_TOOLS` / `MCP_DISABLED_TOOLS`
  - `MCP_ENABLED_TAGS` / `MCP_DISABLED_TAGS`
- **HTTP SSE Request Headers:** Pass custom headers during transport initialization:
  - `x-mcp-enabled-tools` / `x-mcp-disabled-tools`
  - `x-mcp-enabled-tags` / `x-mcp-disabled-tags`
- **HTTP SSE Request Query Parameters:** Append query parameters directly to the operator's transport connection URL:
  - `?tools=tool1,tool2`
  - `?tags=tag1`

When query strings or parameters are provided, an LLM-free **Knowledge Graph resolution layer** (using `DynamicToolOrchestrator`) matches query intents against known tool tags, names, or descriptions, with safe fallback and automated 24-hour background cache refreshing.


---

## Installation

Pick the extra that matches what the operator want to run:

| Extra | Installs | Use when |
|-------|----------|----------|
| `keycloak-agent[mcp]` | Connector-focused MCP server (`agent-connector-sdk` — FastMCP/FastAPI + `epistemic-graph[full]`) | The operator only run the **MCP server** (smallest install / image) |
| `keycloak-agent[all]` | Everything (`mcp` + `agent` + `logfire`) | Development / both surfaces |

```bash
# Connector-focused MCP server (includes the shared graph engine)
uv pip install "keycloak-agent[mcp]"

# Agent runtime (adds model orchestration to the shared graph engine)

# Everything (development)
uv pip install "keycloak-agent[all]"      # or: python -m pip install "keycloak-agent[all]"
```

### Container images (`:mcp`)

One multi-stage `docker/Dockerfile` builds the MCP-only image (`--target mcp`):

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|

```bash
```

### Knowledge-graph database (`epistemic-graph`)

Agent Connector SDK core dependency (`epistemic-graph[full]`). The `[mcp]` extra keeps
deployments can use the bundled engine. For production or shared state, run
**epistemic-graph as a dedicated database service** and configure the runtime to use it.
Deployment recipes (single-node + Raft HA), connection configuration, and architecture
diagrams are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).

---

## Usage

The operator can start the FastMCP server in stdio mode via Python module execution:

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

For direct shell start, ran:

```bash
python -m keycloak_agent.mcp_server
```

---

### MCP Configuration Examples

<!-- MCP-CONFIG-EXAMPLES:START -->

> **Install the connector-focused `[mcp]` extra.** Examples use `keycloak-agent[mcp]` to add
> FastMCP / FastAPI through `agent-connector-sdk`; the required Agent Connector SDK core
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

Runtime references require an alias-aware launcher such as Arbora. Other
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

_Auto-generated from the code-read env surface (package vars) — do not edit._
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
network transport, connector ingestion, Arbora delegation, or trace export.
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
| `KEYCLOAK_AGENT_TLS_PROFILE` | — |  |
| `KEYCLOAK_AGENT_TLS_PROFILE_REF` | — |  |

#### Inherited agent-connector-sdk variables (apply to every connector)

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
| `PROVIDER` | — | Operator-configured LLM provider for the agent |
| `MODEL_ID` | — | Operator-configured model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_24 package + 23 inherited variable(s). Auto-generated from `.env.example` + the shared agent-connector-sdk set — do not edit._
<!-- ENV-VARS-TABLE:END -->

## Available MCP Tools

<!-- MCP-TOOLS-TABLE:START -->

#### Intent tools

| MCP Tool | Kind | Description |
|----------|------|-------------|
| `keycloak_agent_attack_detection` | intent | Manage Keycloak Agent brute force and attack detection operations. |
| `keycloak_agent_authentication` | intent | Manage Keycloak Agent authentication and authenticator flow operations. |
| `keycloak_agent_clients` | intent | Manage Keycloak Agent clients operations. |
| `keycloak_agent_components` | intent | Manage Keycloak Agent components operations. |
| `keycloak_agent_groups` | intent | Manage Keycloak Agent groups operations. |
| `keycloak_agent_idps` | intent | Manage Keycloak Agent identity providers operations. |
| `keycloak_agent_info` | intent | Inspect and discover available Keycloak API methods, paths, and signatures at runtime. |
| `keycloak_agent_organizations` | intent | Manage Keycloak Agent organizations operations. |
| `keycloak_agent_realms` | intent | Manage Keycloak Agent realms operations. |
| `keycloak_agent_roles` | intent | Manage Keycloak Agent roles and scope mappings. |
| `keycloak_agent_users` | intent | Manage Keycloak Agent users operations (Users, Role Mappings, Client Role Mappings). |
| `keycloak_ingest_clients` | intent | List clients in a realm and ingest them as ``:Client`` nodes (+ ``:inRealm``). |
| `keycloak_ingest_groups` | intent | List groups in a realm and ingest them as ``:Group`` nodes (+ ``:hasSubGroup``). |
| `keycloak_ingest_realms` | intent | List all realms and ingest them into epistemic-graph as ``:Realm`` nodes. |
| `keycloak_ingest_users` | intent | List users in a realm and ingest them as ``:User`` nodes (+ ``:inRealm`` links). |

_15 intent tool(s) · 0 operation(s). Call an operation as `act(action='<operation>', params={...})` (`ask` for reads); `find(action='describe', params={'action': '<operation>'})` returns its arguments. An operation is enabled unless its `<DOMAIN>TOOL` toggle is set false. Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->
