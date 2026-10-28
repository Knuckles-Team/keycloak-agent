from keycloak_agent.api.api_client_base import ApiClientBase
from keycloak_agent.api.api_client_realms import _entitled


class Api(ApiClientBase):
    def list_clients(self, realm: str) -> list:
        """List the caller's entitled client UUIDs in an entitled realm."""
        if realm not in _entitled("realm", [realm]):
            raise PermissionError("realm is not entitled")
        _entitled("keycloak-client", [])
        clients = self.request("GET", f"/admin/realms/{realm}/clients")
        if not isinstance(clients, list) or any(
            not isinstance(client, dict)
            or not isinstance(client.get("id"), str)
            or not client["id"].strip()
            for client in clients
        ):
            raise ValueError("client catalog is malformed")
        allowed = set(
            _entitled("keycloak-client", [client["id"] for client in clients])
        )
        return [client for client in clients if client["id"] in allowed]

    def get_client(self, realm: str, client_uuid: str) -> dict:
        """Get client details."""
        return self.request("GET", f"/admin/realms/{realm}/clients/{client_uuid}")

    def create_client(
        self,
        realm: str,
        client_id: str | None = None,
        secret: str | None = None,
        client_representation: dict | None = None,
    ) -> dict:
        """Create a client."""
        if client_representation:
            data = dict(client_representation)
            if client_id and "clientId" not in data:
                data["clientId"] = client_id
            if secret and "secret" not in data:
                data["secret"] = secret
        else:
            data = {"clientId": client_id, "enabled": True}
            if secret:
                data["secret"] = secret
        return self.request("POST", f"/admin/realms/{realm}/clients", data=data)

    def get_client_secret(self, realm: str, client_uuid: str) -> dict:
        """Get the client secret for a client UUID."""
        return self.request(
            "GET", f"/admin/realms/{realm}/clients/{client_uuid}/client-secret"
        )

    def find_client_by_client_id(self, realm: str, client_id: str) -> dict | None:
        """Find a client by its clientId and return it, or None if not found."""
        clients = self.request(
            "GET", f"/admin/realms/{realm}/clients", params={"clientId": client_id}
        )
        if isinstance(clients, list) and len(clients) > 0:
            return clients[0]
        return None

    def regenerate_client_secret(self, realm: str, client_uuid: str) -> dict:
        """Regenerate (rotate) a confidential client's secret by client UUID.

        POSTs to the client-secret endpoint, which makes Keycloak generate a new
        secret and invalidate the old one; returns ``{"type","value"}`` with the
        new value. Pair with the automated-credential-rotation skill (write the
        returned value to OpenBao + propagate to consumers — never log it).
        """
        return self.request(
            "POST", f"/admin/realms/{realm}/clients/{client_uuid}/client-secret"
        )

    def regenerate_client_secret_by_client_id(self, realm: str, client_id: str) -> dict:
        """Regenerate a client's secret by its human clientId (e.g. 'mcp-multiplexer').

        Resolves clientId -> UUID, then regenerates. Returns the same shape as
        ``regenerate_client_secret`` plus the resolved ``client_uuid``; raises if
        the client is not found.
        """
        found = self.find_client_by_client_id(realm, client_id)
        if not found:
            raise ValueError("Configured client was not found in the configured realm")
        uuid = found["id"]
        result = self.regenerate_client_secret(realm, uuid)
        if isinstance(result, dict):
            result = {**result, "client_uuid": uuid}
        return result

    def delete_client(self, realm: str, client_uuid: str) -> dict:
        """Delete a client."""
        return self.request("DELETE", f"/admin/realms/{realm}/clients/{client_uuid}")
