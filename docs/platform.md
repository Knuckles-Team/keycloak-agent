# Backing Platform — Keycloak

`keycloak-agent` is a **client** of a Keycloak Identity and Access Management server.
This page provides a Docker recipe for deploying one locally to serve as the target
of `KEYCLOAK_URL`. For production topologies, follow the upstream
[Keycloak documentation](https://www.keycloak.org/documentation).

!!! note "Backing-system recipe"
    Each connector in the ecosystem follows the same convention — a
    `docs/platform.md` recipe for the system it integrates with, accompanied by a
    sample Compose stack that mirrors [`services/`](https://github.com/Knuckles-Team).
    Systems offered only as a managed service have no local recipe.

## Single-node deployment (Compose)

Keycloak publishes the `quay.io/keycloak/keycloak` image. The following stack runs
one Keycloak server on `:8080` backed by PostgreSQL:

```yaml
# docker/keycloak.compose.yml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:24.0
    container_name: keycloak
    command: start-dev
    restart: unless-stopped
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=admin_secure_password
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=keycloak
      - KC_DB_PASSWORD=keycloak
      - KC_HTTP_ENABLED=true
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db

  keycloak-db:
    image: postgres:16-alpine
    container_name: keycloak-db
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=keycloak
      - POSTGRES_PASSWORD=keycloak
    volumes:
      - keycloak_db:/var/lib/postgresql/data

volumes:
  keycloak_db:
```

```bash
docker compose -f docker/keycloak.compose.yml up -d

# Wait for the admin console to answer
curl -fsS http://localhost:8080/realms/master
```

## Connect keycloak-agent

```bash
export KEYCLOAK_URL=http://localhost:8080
export KEYCLOAK_AGENT_USERNAME=admin
export KEYCLOAK_AGENT_PASSWORD=admin_secure_password
export KEYCLOAK_REALM=master

keycloak-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Combined deployment

A combined stack places Keycloak and the MCP server on one Docker network, so the
server reaches Keycloak by container name:

```yaml
# docker/stack.compose.yml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:24.0
    command: start-dev
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=admin_secure_password
    ports: ["8080:8080"]

  keycloak-agent:
    image: knucklessg1/keycloak-agent:latest
    depends_on: [keycloak]
    environment:
      - KEYCLOAK_URL=http://keycloak:8080
      - KEYCLOAK_AGENT_USERNAME=admin
      - KEYCLOAK_AGENT_PASSWORD=admin_secure_password
      - KEYCLOAK_REALM=master
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8000
    ports: ["8000:8000"]
```

```bash
docker compose -f docker/stack.compose.yml up -d
```

## Provision SSO clients

With Keycloak running and credentials configured, the
[`create_client`](usage.md#as-a-python-api) operation provisions OIDC single sign-on
clients in a realm — the foundation for wiring ecosystem services to centralized
authentication.
