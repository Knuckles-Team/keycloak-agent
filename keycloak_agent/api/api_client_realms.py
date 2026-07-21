from keycloak_agent.api.api_client_base import ApiClientBase


def _entitled(namespace: str, names: list[str]) -> list[str]:
    """Filter ``names`` to the subset the calling identity's Okta/Keycloak groups
    entitle (CONCEPT:AU-OS.identity.identity-scoped-resource-autoload). Degrades
    to the full list if agent-utilities predates the resolver.
    """
    try:
        from agent_utilities.security.entitlements import identity_scoped_resources
    except Exception:
        return list(names)
    return list(identity_scoped_resources(namespace, names))


class Api(ApiClientBase):
    def list_realms(self) -> list:
        """List realms in Keycloak the caller is entitled to."""
        realms = self.request("GET", "/admin/realms")
        if isinstance(realms, list):
            names = [
                r["realm"] for r in realms if isinstance(r, dict) and r.get("realm")
            ]
            entitled = set(_entitled("realm", names))
            realms = [
                r
                for r in realms
                if not isinstance(r, dict) or not r.get("realm") or r["realm"] in entitled
            ]
        return realms

    def get_realm(self, realm_name: str) -> dict:
        """Get realm details. Denied if the caller is not entitled to the realm."""
        if realm_name not in _entitled("realm", [realm_name]):
            raise PermissionError(
                f"Your identity is not entitled to the realm '{realm_name}'."
            )
        return self.request("GET", f"/admin/realms/{realm_name}")

    def create_realm(self, realm_name: str) -> dict:
        """Create a new realm."""
        return self.request(
            "POST", "/admin/realms", data={"realm": realm_name, "enabled": True}
        )

    def delete_realm(self, realm_name: str) -> dict:
        """Delete a realm."""
        return self.request("DELETE", f"/admin/realms/{realm_name}")
