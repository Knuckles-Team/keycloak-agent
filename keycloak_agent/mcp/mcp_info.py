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
        return {"error": "Missing required parameter 'method_name' in params_json."}

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


def register_info_tools(mcp: FastMCP):
    """Register the Keycloak API discovery tools."""

    @mcp.tool(tags=["info"], annotations={"readOnlyHint": True, "idempotentHint": True})
    async def keycloak_agent_info_list_methods(
        tag: str | None = Field(
            default=None,
            description="Only methods of this API tag, for example Groups.",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """List the Keycloak Admin API methods the client can call, optionally by tag."""
        return _list_methods_result(client, _collect_all_methods(client), {"tag": tag})

    @mcp.tool(tags=["info"], annotations={"readOnlyHint": True, "idempotentHint": True})
    async def keycloak_agent_info_search_methods(
        query: str = Field(
            description="Text to look for in method names, paths, tags and summaries."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Search the Keycloak Admin API methods by name, path, tag or summary."""
        return _search_methods_result(
            client, _collect_all_methods(client), {"query": query}
        )

    @mcp.tool(tags=["info"], annotations={"readOnlyHint": True, "idempotentHint": True})
    async def keycloak_agent_info_method_details(
        method_name: str = Field(
            description="Name of a client method from list_methods."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Read the HTTP method, path template, tag and docstring of one client method."""
        return _method_details_result(
            client, _collect_all_methods(client), {"method_name": method_name}
        )
