import sys
import pytest

def test_startup():
    # Basic import test
    import keycloak_agent
    assert keycloak_agent.__version__ == "0.15.0"
