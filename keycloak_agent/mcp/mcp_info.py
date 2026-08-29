"""MCP tools for inspecting the Keycloak API client schema."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from keycloak_agent.auth import get_client


def _collect_all_methods(client) -> dict:
    """Dynamic client methods plus any custom/explicit ones not already listed."""
    all_methods = dict(client.list_dynamic_methods())

    for attr in dir(client):
        if attr.startswith("_") or attr in ["request", "list_dynamic_methods"]:
            continue
        try:
            func = getattr(client, attr)
        except AttributeError:
            continue
        if not callable(func):
            continue

        if attr not in all_methods:
            all_methods[attr] = {
                "method": "CUSTOM",
                "path_template": "Defined in python mixin",
                "tag": "Custom",
                "summary": func.__doc__ or "Explicit Python method definition",
            }

    return all_methods


def _list_methods_result(client, all_methods: dict, kwargs: dict) -> dict:
    tag_filter = kwargs.get("tag")
    result = {}
    for name, info in sorted(all_methods.items()):
        if tag_filter and info.get("tag", "").lower() != tag_filter.lower():
            continue
        result[name] = {
            "path": f"{info.get('method')} {info.get('path_template')}",
            "summary": info.get("summary", "").split("\n")[0]
            if info.get("summary")
            else "",
        }
    return {"total": len(result), "methods": result}


def _method_matches_search(name: str, info: dict, query: str) -> bool:
    return (
        query in name.lower()
        or query in info.get("path_template", "").lower()
        or (info.get("summary") and query in info.get("summary", "").lower())
        or query in info.get("tag", "").lower()
    )


def _search_methods_result(client, all_methods: dict, kwargs: dict) -> dict:
    query = kwargs.get("query", "").lower()
    if not query:
        return {"error": "Missing required parameter 'query' in params_json."}

    result = {}
    for name, info in sorted(all_methods.items()):
        if _method_matches_search(name, info, query):
            result[name] = {
                "tag": info.get("tag"),
                "path": f"{info.get('method')} {info.get('path_template')}",
                "summary": info.get("summary", "").split("\n")[0]
                if info.get("summary")
                else "",
            }
    return {"total": len(result), "query": query, "matches": result}


def _method_details_result(client, all_methods: dict, kwargs: dict) -> dict:
    method_name = kwargs.get("method_name")
    if not method_name:
        return {
            "error": "Missing required parameter 'method_name' in params_json."
        }

    if method_name not in all_methods:
        return {"error": f"Method '{method_name}' not found."}

    info = all_methods[method_name]
    # Custom get_attr to support dynamic resolution
    func = getattr(client, method_name)
    return {
        "method_name": method_name,
        "http_method": info.get("method"),
        "path_template": info.get("path_template"),
        "tag": info.get("tag"),
        "docstring": func.__doc__ or info.get("summary"),
    }


_INFO_ACTIONS = {
    "list_methods": _list_methods_result,
    "search_methods": _search_methods_result,
    "method_details": _method_details_result,
}


def register_info_tools(mcp: FastMCP):
    """Register Keycloak Agent info tools."""

    @mcp.tool(tags=["info"])
    async def keycloak_agent_info(
        action: str = Field(
            default="list_methods",
            description="Info action to perform. Must be one of: 'list_methods', 'search_methods', 'method_details'",
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Inspect and discover available Keycloak API methods, paths, and signatures at runtime."""
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        all_methods = _collect_all_methods(client)

        handler = _INFO_ACTIONS.get(action)
        if handler is None:
            raise ValueError(f"Unknown action: {action}")
        return handler(client, all_methods, kwargs)
