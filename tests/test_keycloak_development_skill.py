"""PIPE-CONNSPEC-R132.4: the Keycloak development skill is packaged."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "keycloak_agent" / "skills" / "keycloak-agent-development" / "SKILL.md"

pytestmark = pytest.mark.spec("PIPE-CONNSPEC-R132.4")


def test_development_skill_has_rapid_contract_and_package_binding() -> None:
    text = SKILL.read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert SKILL.is_file()
    assert re.search(r"^name:\s*keycloak-agent-development\s*$", frontmatter, re.M)
    assert re.search(r"^skill_type:\s*skill\s*$", frontmatter, re.M)
    assert "## Rapid delivery: the 5-minute contract" in text
    for term in (
        "keycloak_agent/__init__.py",
        "keycloak_agent/api_client.py",
        "keycloak_agent/api/api_client_base.py",
        "keycloak_agent/api/openapi.json",
        "keycloak_agent/auth.py",
        "keycloak_agent/mcp_server.py",
        "keycloak_agent/mcp/",
        "keycloak_agent/ontology/",
        "keycloak_agent/connector_sources.py",
        "KEYCLOAK_URL",
        "KEYCLOAK_REALM",
        "KEYCLOAK_CLIENT_ID",
        "KEYCLOAK_CLIENT_SECRET",
        "keycloak-mcp",
        "skills/**",
        "python_pipeline.yml@main",
        "container_pipeline.yml@main",
        "render_connector: true",
        "pages_pipeline.yml@main",
        "uv run --locked --extra test pytest",
    ):
        assert term in text

    assert "verify=False" not in text
    assert "--no-verify" not in text
    package_data = project["tool"]["setuptools"]["package-data"]["keycloak_agent"]
    assert "skills/**" in package_data
    assert project["project"]["entry-points"]["scion_sdk.connector"] == {
        "keycloak-mcp": "keycloak_agent:connector"
    }
