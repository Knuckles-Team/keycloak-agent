# CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py` | The listings include the packaged skills, ontology and prompts. |
| T-002 | `CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT-R002` | `tests/test_tool_action_names.py` | Every advertised action resolves to a client method. |
| T-003 | `CONN-KEYCLOAK-AGENT-CONNECTOR-CONTENT-R003` | `tests/test_ontology_extends_core.py::test_pack_declares_no_core_term` | The served Turtle declares none of the listed core terms. |
