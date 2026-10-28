# CONN-KEYCLOAK-AGENT-CONNECTOR-IDENTITY — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares the fleet name once. The manifest, fingerprints and ingest binding carry the same name.


## Realm entitlement boundary

Realm discovery checks the SDK actor before the Keycloak request. It filters
the returned catalog by the actor's realm grants. A missing resolver or a
malformed catalog refuses the operation. Client-level entitlement work and
the SDK fleet-wide R036 rollup remain separate.


## Client catalog scope

Client discovery first requires an actor's realm entitlement. It then filters
client UUIDs through the SDK's `keycloak-client` capability namespace. An
invalid catalog refuses the operation. Direct client methods and served actor
forwarding remain separate work.
