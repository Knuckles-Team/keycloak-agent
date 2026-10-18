import pytest


@pytest.mark.concept("KEY-002")
def test_startup():
    # Basic import test
    import keycloak_agent

    import tomllib
    from pathlib import Path

    project = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert keycloak_agent.__version__ == project["project"]["version"]
