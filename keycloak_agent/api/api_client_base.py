import json
import os
import re
from typing import Any
from urllib.parse import urljoin

import requests
from agent_utilities.core.transport_security import (
    ResolvedTLSProfile,
    resolve_configured_tls_profile,
)

# Direct (path, HTTP method) -> generated-method-name overrides for the main
# realm endpoints, where the generic path-segment naming below would collide
# ("admin/realms" GET/POST both operate on the collection, not one segment).
_DIRECT_REALM_METHOD_NAMES = {
    ("admin/realms", "GET"): "list_realms",
    ("admin/realms", "POST"): "create_realm",
    ("admin/realms/{realm}", "GET"): "get_realm",
    ("admin/realms/{realm}", "PUT"): "update_realm",
    ("admin/realms/{realm}", "DELETE"): "delete_realm",
}

_POST_ACTION_TOKENS = (
    "copy",
    "reset",
    "trigger",
    "execute",
    "clear",
    "lower_priority",
    "raise_priority",
)
_GET_SINGLETON_TOKENS = ("count", "status", "validate")

# HTTP verbs whose generated-method prefix is a fixed rename, independent of path.
_METHOD_PREFIX_BY_VERB = {
    "put": "update",
    "delete": "delete",
}


def _strip_realm_prefix(p: str) -> str:
    """Strip a leading 'admin/realms/{realm}/' or 'admin/' path prefix."""
    realm_prefix = "admin/realms/{realm}"
    if p.startswith(realm_prefix):
        return p[len(realm_prefix) :].strip("/")
    if p.startswith("admin/"):
        return p[len("admin/") :].strip("/")
    return p


def _path_segment_to_name_part(part: str) -> str:
    if part.startswith("{") and part.endswith("}"):
        param = part[1:-1].replace("-", "_")
        return f"by_{param}"
    return part.replace("-", "_")


def _get_method_prefix(parts: list[str], cleaned_path: str) -> str:
    if parts and parts[-1].startswith("by_"):
        return "get"
    if any(token in cleaned_path for token in _GET_SINGLETON_TOKENS):
        return "get"
    return "list"


def _post_method_prefix(cleaned_path: str) -> str:
    if any(token in cleaned_path for token in _POST_ACTION_TOKENS):
        return "post"
    return "create"


def _method_prefix(method_lower: str, parts: list[str], cleaned_path: str) -> str:
    if method_lower == "get":
        return _get_method_prefix(parts, cleaned_path)
    if method_lower == "post":
        return _post_method_prefix(cleaned_path)
    return _METHOD_PREFIX_BY_VERB.get(method_lower, method_lower)


def _resolve_path_placeholder_value(ph: str, remaining: dict) -> Any:
    ph_alt = ph.replace("-", "_")
    if ph in remaining:
        return remaining.pop(ph)
    if ph_alt in remaining:
        return remaining.pop(ph_alt)
    if ph == "realm":
        return "master"
    raise ValueError(f"Missing required path parameter: {ph}")


def _substitute_path_placeholders(path_template: str, remaining: dict) -> str:
    """Fill every ``{placeholder}`` in path_template, popping matches out of
    ``remaining`` (mutated in place) as it goes."""
    path = path_template
    for ph in re.findall(r"\{([^{}]+)\}", path_template):
        val = _resolve_path_placeholder_value(ph, remaining)
        path = path.replace(f"{{{ph}}}", str(val))
    return path


def _extract_request_body(method: str, remaining: dict) -> Any:
    """For a body-carrying verb, pop the body out of ``remaining`` (mutated
    in place): an explicit body/representation/data key, else every
    leftover kwarg becomes the body and ``remaining`` is drained."""
    if method not in ["POST", "PUT", "PATCH"]:
        return None
    for key in ("body", "representation", "data"):
        if key in remaining:
            return remaining.pop(key)
    body = dict(remaining)
    remaining.clear()
    return body


class ApiClientBase:
    _schema: dict[str, Any] | None = None
    _methods: dict[str, Any] = {}

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        tls_profile: ResolvedTLSProfile | None = None,
        token_provider: Any = None,
    ):
        self.base_url = base_url
        self.token = token
        self.username = username
        self.password = password
        # Optional self-refreshing token source (ClientCredentialsTokenProvider).
        # When set, every request carries a freshly-minted bearer and a 401
        # triggers a forced re-mint + one retry — so a rotated/expired admin
        # token (Keycloak master-realm tokens are short-lived) self-heals.
        self._token_provider = token_provider
        self.tls_profile = tls_profile or resolve_configured_tls_profile(
            "keycloak_agent"
        )
        self._session = self.tls_profile.configure_requests_session(requests.Session())

        if token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})
        elif username and password:
            self._session.auth = (username, password)

        # Pre-load the schema and populate methods
        self._load_schema()

    def close(self) -> None:
        """Release transport resources and runtime-only TLS material."""
        self._session.close()
        self.tls_profile.cleanup()

    @classmethod
    def _load_schema(cls):
        if cls._schema is not None:
            return

        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, "openapi.json")
        if not os.path.exists(schema_path):
            cls._schema = {"paths": {}}
            return

        try:
            with open(schema_path) as f:
                cls._schema = json.load(f)
        except Exception:
            cls._schema = {"paths": {}}

        paths = cls._schema.get("paths", {})
        for path, methods in paths.items():
            for method, op in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue

                method_name = cls._generate_method_name(method, path)
                tags = op.get("tags", ["Untagged"])
                tag = tags[0] if tags else "Untagged"
                summary = op.get("summary", "")

                cls._methods[method_name] = {
                    "method": method.upper(),
                    "path_template": path,
                    "tag": tag,
                    "summary": summary,
                }

    @classmethod
    def _generate_method_name(cls, method: str, path: str) -> str:
        p = path.strip("/")

        # Direct mappings for main realm endpoints
        direct_name = _DIRECT_REALM_METHOD_NAMES.get((p, method))
        if direct_name:
            return direct_name

        p = _strip_realm_prefix(p)

        parts = [_path_segment_to_name_part(part) for part in p.split("/")]
        cleaned_path = "_".join(parts)
        method_lower = method.lower()
        prefix = _method_prefix(method_lower, parts, cleaned_path)

        name = f"{prefix}_{cleaned_path}"
        name = re.sub(r"_+", "_", name).strip("_")
        return name

    def __getattr__(self, name: str) -> Any:
        self._load_schema()

        if name in self._methods:
            method_info = self._methods[name]

            def dynamic_method(**kwargs):
                return self._execute_dynamic_call(
                    method=method_info["method"],
                    path_template=method_info["path_template"],
                    kwargs=kwargs,
                )

            dynamic_method.__name__ = name
            dynamic_method.__doc__ = f"{method_info['summary']}\n\nPath: {method_info['method']} {method_info['path_template']}"
            setattr(self, name, dynamic_method)
            return dynamic_method

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def _execute_dynamic_call(
        self, method: str, path_template: str, kwargs: dict
    ) -> Any:
        remaining = kwargs.copy()
        path = _substitute_path_placeholders(path_template, remaining)
        body = _extract_request_body(method, remaining)
        params = remaining if remaining else None
        return self.request(method, path, params=params, data=body)

    def list_dynamic_methods(self) -> dict:
        self._load_schema()
        return self._methods

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
    ) -> Any:
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = urljoin(self.base_url, endpoint)

        json_data = data if isinstance(data, dict | list) else None
        req_data = data if not isinstance(data, dict | list) else None

        def _send(force_token: bool) -> requests.Response:
            headers = {"Content-Type": "application/json"}
            if self._token_provider is not None:
                headers["Authorization"] = (
                    f"Bearer {self._token_provider.get_token(force=force_token)}"
                )
            return self._session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                data=req_data,
            )

        response = _send(force_token=False)
        # A 401 means the cached admin token rotated/expired between mint and use
        # — force a fresh token and retry once before surfacing the error.
        if response.status_code == 401 and self._token_provider is not None:
            response = _send(force_token=True)

        if response.status_code >= 400:
            raise Exception(f"API error: {response.status_code}")

        if response.status_code == 204 or not response.text.strip():
            return {"status": "success"}

        try:
            return response.json()
        except Exception:
            return {"status": "success", "text": response.text}
