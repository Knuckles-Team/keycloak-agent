from keycloak_agent.api.api_client_base import ApiClientBase

class Api(ApiClientBase):
    def list_users(self, realm: str, search: str = None) -> list:
        """List users in a realm."""
        params = {"search": search} if search else None
        return self.request("GET", f"/admin/realms/{realm}/users", params=params)

    def get_user(self, realm: str, user_id: str) -> dict:
        """Get user details."""
        return self.request("GET", f"/admin/realms/{realm}/users/{user_id}")

    def create_user(self, realm: str, username: str, email: str = None, enabled: bool = True) -> dict:
        """Create a user."""
        return self.request("POST", f"/admin/realms/{realm}/users", data={"username": username, "email": email, "enabled": enabled})

    def delete_user(self, realm: str, user_id: str) -> dict:
        """Delete a user."""
        return self.request("DELETE", f"/admin/realms/{realm}/users/{user_id}")

    def reset_password(self, realm: str, user_id: str, password: str, temporary: bool = False) -> dict:
        """Reset a user's password."""
        return self.request("PUT", f"/admin/realms/{realm}/users/{user_id}/reset-password", data={"type": "password", "value": password, "temporary": temporary})
