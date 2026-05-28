from keycloak_agent.api.api_client_base import ApiClientBase


class Api(ApiClientBase):
    def list_clients(self, realm: str) -> list:
        """List clients in a realm."""
        return self.request("GET", f"/admin/realms/{realm}/clients")

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

    def delete_client(self, realm: str, client_uuid: str) -> dict:
        """Delete a client."""
        return self.request("DELETE", f"/admin/realms/{realm}/clients/{client_uuid}")
