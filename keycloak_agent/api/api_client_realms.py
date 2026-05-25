from keycloak_agent.api.api_client_base import ApiClientBase


class Api(ApiClientBase):
    def list_realms(self) -> list:
        """List realms in Keycloak."""
        return self.request("GET", "/admin/realms")

    def get_realm(self, realm_name: str) -> dict:
        """Get realm details."""
        return self.request("GET", f"/admin/realms/{realm_name}")

    def create_realm(self, realm_name: str) -> dict:
        """Create a new realm."""
        return self.request(
            "POST", "/admin/realms", data={"realm": realm_name, "enabled": True}
        )

    def delete_realm(self, realm_name: str) -> dict:
        """Delete a realm."""
        return self.request("DELETE", f"/admin/realms/{realm_name}")
