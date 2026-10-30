from keycloak_agent.api.api_client_base import ApiClientBase


def _entitled(namespace: str, names: list[str]) -> list[str]:
    """Filter resources by the verified caller's SDK entitlements."""
    try:
        from scion_sdk.entitlements import identity_scoped_resources
    except ImportError as exc:
        raise PermissionError("realm entitlement resolver unavailable") from exc
    return list(identity_scoped_resources(namespace, names))


class Api(ApiClientBase):
    def list_realms(self) -> list:
        """List realms in Keycloak the caller is entitled to."""
        _entitled("realm", [])  # Refuse an unbound caller before the provider call.
        realms = self.request("GET", "/admin/realms")
        if not isinstance(realms, list) or any(
            not isinstance(realm, dict)
            or not isinstance(realm.get("realm"), str)
            or not realm["realm"].strip()
            for realm in realms
        ):
            raise ValueError("realm catalog is malformed")
        entitled = set(_entitled("realm", [realm["realm"] for realm in realms]))
        return [realm for realm in realms if realm["realm"] in entitled]

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
