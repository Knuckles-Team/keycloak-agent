from keycloak_agent.api.api_client_base import ApiClientBase


class Api(ApiClientBase):
    def list_clients(self, realm: str) -> list:
        """List clients in a realm."""
        return self.request("GET", f"/admin/realms/{realm}/clients")

    def get_client(self, realm: str, client_uuid: str) -> dict:
        """Get client details."""
        return self.request("GET", f"/admin/realms/{realm}/clients/{client_uuid}")

    def create_client(self, realm: str, client_id: str, secret: str = None) -> dict:
        """Create a client."""
        data = {"clientId": client_id, "enabled": True}
        if secret:
            data["secret"] = secret
        return self.request("POST", f"/admin/realms/{realm}/clients", data=data)

    def delete_client(self, realm: str, client_uuid: str) -> dict:
        """Delete a client."""
        return self.request("DELETE", f"/admin/realms/{realm}/clients/{client_uuid}")
