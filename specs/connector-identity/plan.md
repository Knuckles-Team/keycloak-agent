# CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

`pyproject.toml` declares the fleet name once. The manifest, fingerprints and ingest binding carry the same name.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 3 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
pyproject.toml  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Realm entitlement boundary

Realm discovery checks the SDK actor before the Keycloak request. It filters
the returned catalog by the actor's realm grants. A missing resolver or a
malformed catalog refuses the operation. Client-level entitlement work and
the SDK fleet-wide R036 rollup remain separate.

### Client catalog scope

Client discovery first requires an actor's realm entitlement. It then filters
client UUIDs through the SDK's `keycloak-client` capability namespace. An
invalid catalog refuses the operation. Direct client methods and served actor
forwarding remain separate work.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R001`: the `keycloak-mcp` console script (pyproject.toml, scion_sdk.cli:serve) loads `keycloak_agent:connector` (keycloak_agent/__init__.py) -> keycloak_agent/connector_sources.py (server="keycloak-mcp", served as connector://resources) and the SDK connector_name("keycloak_agent").
2. `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002`: arbora fleet.call -> `keycloak_agent_realms` tool (keycloak_agent/mcp/mcp_realms.py::register_realms_tools:10) -> keycloak_agent/api/api_client_realms.py::Api.list_realms -> _entitled -> scion_sdk.entitlements.identity_scoped_resources.
3. `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003`: arbora fleet.call -> `keycloak_agent_clients` tool (keycloak_agent/mcp/mcp_clients.py:14, action list_clients) -> keycloak_agent/api/api_client_clients.py::Api.list_clients -> keycloak_agent/api/api_client_realms.py::_entitled for namespaces realm and keycloak-client.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
