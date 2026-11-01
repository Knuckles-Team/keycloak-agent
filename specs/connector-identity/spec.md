# CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY — The connector is filed under its fleet name

Owner: keycloak-agent. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R071`, `PIPE-GATES-R010`.

## Purpose and user stories

The engine and arbora list a connector's tools and ingest under its fleet name. This connector's fleet name is `keycloak-mcp`.

## Why a new spec

The specs of this repository were read; none owns this capability. This spec states it for this connector only.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - The connector is filed under its fleet name (Priority: P1)

The engine and arbora list a connector's tools and ingest under its fleet name. This connector's fleet name is `keycloak-mcp`.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R001` (fleet name) is exercised, **Then** every connector name in the package is `keycloak-mcp`.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002` (realm catalog requires a verified identity) is exercised, **Then** `tests/test_identity_realm_scoping.py` covers real SDK actor scoping, a missing resolver, missing identity and malformed entries. Test: `tests/test_identity_realm_scoping.py::test_real_authenticated_identity_scopes_the_catalog`.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003` (client catalog auto-load is identity scoped) is exercised, **Then** `tests/test_identity_client_scoping.py` covers actor grants, realm refusal, missing identity and malformed entries. Test: `tests/test_identity_client_scoping.py::test_client_catalog_returns_only_granted_ids`.

### Edge Cases

- If `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R001` is not met, its proving test fails: fleet name.
- If `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002` is not met, its proving test fails: realm catalog requires a verified identity.
- If `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003` is not met, its proving test fails: client catalog auto-load is identity scoped.

## Requirements

- **FR-001**: Fleet name. Rows: `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R001`.
- **FR-002**: Realm catalog requires a verified identity. Rows: `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002`.
- **FR-003**: Client catalog auto-load is identity scoped. Rows: `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003`.

## Success Criteria

- **SC-001**: Every connector name in the package is `keycloak-mcp`. Rows: `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R001`.
- **SC-002**: `tests/test_identity_realm_scoping.py` covers real SDK actor scoping, a missing resolver, missing identity and malformed entries. Rows: `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002`.
- **SC-003**: `tests/test_identity_client_scoping.py` covers actor grants, realm refusal, missing identity and malformed entries. Rows: `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
