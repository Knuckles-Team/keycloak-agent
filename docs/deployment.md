# Deployment

This page covers running `keycloak-agent` as a long-lived service: the transports,
the optional agent server, a Docker Compose stack, putting it behind a Caddy reverse
proxy, and giving it a DNS name with Technitium. To provision the **Keycloak**
server it connects to, see [Backing Platform](platform.md).

> `keycloak-agent` ships **two** console scripts: an **MCP server** (`keycloak-mcp`)
> exposing the typed tool surface, and an optional **Pydantic-AI agent server**
> (`keycloak-agent`) that consumes those tools. Deploy the MCP server on its own for
> a policy router / agent to call, or add the agent server for autonomous operation.

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    keycloak-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    keycloak-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    keycloak-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`keycloak-agent` is configured entirely from the environment. The **required** set:

| Var | Default | Meaning |
|---|---|---|
| `KEYCLOAK_URL` | `http://localhost:8080` | Keycloak base admin URL |
| `KEYCLOAK_USERNAME` | `admin` | Admin account username |
| `KEYCLOAK_PASSWORD` | `admin_secure_password` | Admin account password |
| `KEYCLOAK_REALM` | `master` | Realm name |

Plus `HOST` / `PORT` / `TRANSPORT` for HTTP transports. The full set is documented
in [`.env.example`](https://github.com/Knuckles-Team/keycloak-agent/blob/main/.env.example);
copy it to `.env` and fill in your values. The server registers its tools and
remains inactive on administrative writes when credentials are absent.

## Docker Compose

The repo ships [`docker/compose.yml`](https://github.com/Knuckles-Team/keycloak-agent/blob/main/docker/compose.yml).
It reads a sibling `.env` and publishes the HTTP server on `:8000`:

```yaml
services:
  keycloak-agent:
    image: knucklessg1/keycloak-agent:latest
    container_name: keycloak-agent
    hostname: keycloak-agent
    restart: always
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
cp .env.example .env          # then edit KEYCLOAK_* values
docker compose -f docker/compose.yml up -d
docker compose -f docker/compose.yml logs -f
```

## Run the agent server

The optional **agent server** (`keycloak-agent` console script) starts a Pydantic-AI
agent that consumes the MCP tools. Point it at a running MCP server with `--mcp-url`,
or let it launch one from a bundled `mcp_config.json`:

```bash
# Connect the agent to an already-deployed MCP HTTP server
keycloak-agent --mcp-url http://keycloak-agent:8000/mcp --host 0.0.0.0 --port 9000
```

The agent server listens on `:9000` by default. A companion Compose file deploys it
alongside the MCP server, wiring `MCP_URL` to the MCP service by container name:

```yaml
services:
  keycloak-agent-server:
    image: knucklessg1/keycloak-agent:latest
    container_name: keycloak-agent-server
    hostname: keycloak-agent-server
    restart: always
    entrypoint: ["keycloak-agent"]
    env_file:
      - .env
    environment:
      - MCP_URL=http://keycloak-agent:8000/mcp
      - HOST=0.0.0.0
      - PORT=9000
    ports:
      - "9000:9000"
    depends_on:
      - keycloak-agent
```

```bash
docker compose -f docker/agent.compose.yml up -d
```

## Behind a Caddy reverse proxy

Expose the HTTP server on a hostname with automatic TLS. Add to your `Caddyfile`:

```caddy
# Internal (self-signed) — homelab .arpa zone
keycloak-agent.arpa {
    tls internal
    reverse_proxy keycloak-agent:8000
}
```

```caddy
# Public — automatic Let's Encrypt
keycloak-agent.example.com {
    reverse_proxy keycloak-agent:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

Point the hostname at the host running Caddy. Via the Technitium API:

```bash
curl -s "http://technitium.arpa:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=keycloak-agent.arpa" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=10.0.0.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `keycloak-agent.arpa → <caddy-host-ip>` in the Technitium web
console (`http://technitium.arpa:5380`). The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to your client's `mcp_config.json` (multiplexer nickname `key`):

```json
{
  "mcpServers": {
    "keycloak_agent": {
      "command": "uv",
      "args": ["run", "keycloak-mcp"],
      "env": {
        "KEYCLOAK_URL": "http://your-keycloak:8080",
        "KEYCLOAK_USERNAME": "admin",
        "KEYCLOAK_PASSWORD": "admin_secure_password",
        "KEYCLOAK_REALM": "master"
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://keycloak-agent.arpa/mcp` instead.
