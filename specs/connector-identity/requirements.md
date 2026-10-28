# CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R001` | **Fleet name.** `pyproject.toml` declares `keycloak-mcp` as the single `agent_connector_sdk.connector` entry point. The content pack, the manifest `connector`, the fingerprints and the ingest binding all carry `keycloak-mcp`. Proving test: `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name`. | Every connector name in the package is `keycloak-mcp`. |
| `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R002` | **Realm catalog requires a verified identity.** Before fetching realms, require the SDK entitlement resolver and an authenticated, tenant-bound actor. Return only valid realm entries granted to that actor. Refuse unavailable resolvers and malformed catalog responses. | `tests/test_identity_realm_scoping.py` covers real SDK actor scoping, a missing resolver, missing identity and malformed entries. |
| `CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY-R003` | **Client catalog auto-load is identity scoped.** Before listing Keycloak clients, require the actor's realm grant. Return only valid client UUID entries granted by the `keycloak-client` namespace. Refuse missing identity and malformed catalogs. This row does not claim that direct client operations are authorized. | `tests/test_identity_client_scoping.py` covers actor grants, realm refusal, missing identity and malformed entries. |
