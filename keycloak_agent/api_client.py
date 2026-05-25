"""CONCEPT:KEY-001 Dynamic client facade orchestration and resource mappings."""
#!/usr/bin/env python
from keycloak_agent.api.api_client_clients import Api as ClientsApi
from keycloak_agent.api.api_client_realms import Api as RealmsApi
from keycloak_agent.api.api_client_users import Api as UsersApi

__version__ = "0.15.0"


class Api(RealmsApi, UsersApi, ClientsApi):
    pass
