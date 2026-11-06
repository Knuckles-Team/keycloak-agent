# CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT-R001` | **Default content.** `pyproject.toml` declares `keycloak-mcp` as the single `scion_sdk.connector` entry point. The server lists the packaged `skill://` and `ontology://` resources and the packaged prompts with no `content=` argument. Proving test: `tests/test_default_content_surfaces.py`. Caller chain: the `keycloak-mcp` console script (pyproject.toml) loads the `scion_sdk.connector` entry point `keycloak_agent:connector` -> keycloak_agent/__init__.py::connector (a Connector with no content= argument) -> the SDK default content registration serves skill://, ontology:// and prompts. Shape: tests build the server from keycloak_agent and list resources and prompts over the packaged keycloak_agent/skills, keycloak_agent/ontology and keycloak_agent/prompts directories. | `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. Planned test: `tests/test_default_content_surfaces.py::test_default_content_surfaces_list_skills_ontology_prompts`. |
| `CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT-R002` | **Advertised actions are real.** Every action name a keycloak tool advertises in its description is a generated or hand-written client method, so each expanded per-action tool resolves. Proving test: `tests/test_tool_action_names.py`. | Groups, roles, components, identity providers, organizations and authentication tools list actions that exist in the client. |
