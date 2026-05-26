import json
import os
import re
from typing import Any
from urllib.parse import urljoin

import requests
import urllib3


class ApiClientBase:
    _schema = None
    _methods = {}

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        verify: bool = True,
    ):
        self.base_url = base_url
        self.token = token
        self.username = username
        self.password = password
        self._session = requests.Session()
        self._session.verify = verify

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})
        elif username and password:
            self._session.auth = (username, password)

        # Pre-load the schema and populate methods
        self._load_schema()

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
        if p == "admin/realms":
            if method == "GET":
                return "list_realms"
            if method == "POST":
                return "create_realm"
        if p == "admin/realms/{realm}":
            if method == "GET":
                return "get_realm"
            if method == "PUT":
                return "update_realm"
            if method == "DELETE":
                return "delete_realm"

        # Strip '/admin/realms/{realm}' or '/admin' prefixes
        realm_prefix = "admin/realms/{realm}"
        if p.startswith(realm_prefix):
            p = p[len(realm_prefix) :].strip("/")
        elif p.startswith("admin/"):
            p = p[len("admin/") :].strip("/")

        parts = []
        for part in p.split("/"):
            if part.startswith("{") and part.endswith("}"):
                param = part[1:-1].replace("-", "_")
                parts.append(f"by_{param}")
            else:
                parts.append(part.replace("-", "_"))

        cleaned_path = "_".join(parts)
        method_lower = method.lower()

        if method_lower == "get":
            if parts and parts[-1].startswith("by_"):
                prefix = "get"
            else:
                prefix = (
                    "list"
                    if not (
                        "count" in cleaned_path
                        or "status" in cleaned_path
                        or "validate" in cleaned_path
                    )
                    else "get"
                )
        elif method_lower == "post":
            if any(
                x in cleaned_path
                for x in [
                    "copy",
                    "reset",
                    "trigger",
                    "execute",
                    "clear",
                    "lower_priority",
                    "raise_priority",
                ]
            ):
                prefix = "post"
            else:
                prefix = "create"
        elif method_lower == "put":
            prefix = "update"
        elif method_lower == "delete":
            prefix = "delete"
        else:
            prefix = method_lower

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
        placeholders = re.findall(r"\{([^{}]+)\}", path_template)
        path = path_template
        remaining = kwargs.copy()

        for ph in placeholders:
            ph_key = ph
            ph_key_alt = ph.replace("-", "_")
            val = None
            if ph_key in remaining:
                val = remaining.pop(ph_key)
            elif ph_key_alt in remaining:
                val = remaining.pop(ph_key_alt)
            else:
                if ph == "realm":
                    val = "master"
                else:
                    raise ValueError(f"Missing required path parameter: {ph}")
            path = path.replace(f"{{{ph}}}", str(val))

        body = None
        if method in ["POST", "PUT", "PATCH"]:
            if "body" in remaining:
                body = remaining.pop("body")
            elif "representation" in remaining:
                body = remaining.pop("representation")
            elif "data" in remaining:
                body = remaining.pop("data")
            else:
                body = remaining
                remaining = {}

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

        headers = {"Content-Type": "application/json"}

        json_data = data if isinstance(data, (dict, list)) else None
        req_data = data if not isinstance(data, (dict, list)) else None

        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            data=req_data,
        )

        if response.status_code >= 400:
            raise Exception(f"API error: {response.status_code} - {response.text}")

        if response.status_code == 204 or not response.text.strip():
            return {"status": "success"}

        try:
            return response.json()
        except Exception:
            return {"status": "success", "text": response.text}
