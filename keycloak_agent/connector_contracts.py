"""Tool-use contracts, surface links, data locations and business roles of keycloak-mcp.

The SDK serves this declaration as the connector's surface ontology and checks it
against the served tools, prompts and skills (SCION-CONNECTOR-CONTROL-R916).
"""

# ruff: noqa: E501
from __future__ import annotations

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS: tuple[ToolUseContract, ...] = (
    ToolUseContract(
        "onboard-an-sso-client",
        description="Register an OIDC client for an application and hand its secret to the vault",
        steps=(
            ToolStep(
                "keycloak_list_realms",
                params=(),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_find_client_by_client_id",
                params=("realm", "client_id"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_create_client",
                params=("realm",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_get_client",
                params=("realm", "client_uuid"),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
            ToolStep(
                "keycloak_get_client_secret",
                params=("realm", "client_uuid"),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
        ),
    ),
    ToolUseContract(
        "rotate-a-client-secret",
        description="Issue a new client secret and verify the old one is gone",
        steps=(
            ToolStep(
                "keycloak_get_client",
                params=("realm", "client_uuid"),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                    Refusal("not_found", "the named object does not exist"),
                ),
            ),
            ToolStep(
                "keycloak_regenerate_client_secret",
                params=("realm", "client_uuid"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_regenerate_client_secret_by_client_id",
                params=("realm", "client_id"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_get_client_secret",
                params=("realm", "client_uuid"),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
        ),
    ),
    ToolUseContract(
        "retire-an-sso-client",
        description="Remove a client that no application uses",
        steps=(
            ToolStep(
                "keycloak_list_clients",
                params=("realm",),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_get_client",
                params=("realm", "client_uuid"),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
            ToolStep(
                "keycloak_delete_client",
                params=("realm", "client_uuid"),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                    Refusal("not_found", "the named object does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "review-realm-clients",
        description="List the clients of a realm",
        steps=(
            ToolStep(
                "keycloak_list_realms",
                params=(),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_get_realm",
                params=("realm_name",),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
            ToolStep(
                "keycloak_list_clients",
                params=("realm",),
                result=("result",),
                refusals=(),
            ),
        ),
    ),
    ToolUseContract(
        "provision-a-realm",
        description="Create or remove a realm",
        steps=(
            ToolStep(
                "keycloak_list_realms",
                params=(),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_create_realm",
                params=("realm_name",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_get_realm",
                params=("realm_name",),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
            ToolStep(
                "keycloak_delete_realm",
                params=("realm_name",),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                    Refusal("not_found", "the named object does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "onboard-a-user",
        description="Create a user, set a temporary password and place the user in groups",
        steps=(
            ToolStep(
                "keycloak_list_users",
                params=("realm",),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_create_user",
                params=("realm", "username"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_get_user",
                params=("realm", "user_id"),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
            ToolStep(
                "keycloak_reset_password",
                params=("realm", "user_id", "password"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_groups_list_groups",
                params=("realm", "briefRepresentation", "exact"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_users_list_users_by_user_id_groups",
                params=("user_id",),
                result=("result",),
                refusals=(),
            ),
        ),
    ),
    ToolUseContract(
        "offboard-a-user",
        description="Find a user, review their groups and delete the account",
        steps=(
            ToolStep(
                "keycloak_list_users",
                params=("realm",),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_get_user",
                params=("realm", "user_id"),
                result=("result",),
                refusals=(Refusal("not_found", "the named object does not exist"),),
            ),
            ToolStep(
                "keycloak_agent_users_list_users_by_user_id_groups",
                params=("user_id",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_delete_user",
                params=("realm", "user_id"),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                    Refusal("not_found", "the named object does not exist"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "manage-groups",
        description="Create, read and delete groups",
        steps=(
            ToolStep(
                "keycloak_agent_groups_list_groups",
                params=("realm", "briefRepresentation", "exact"),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_agent_groups_get_groups_by_group_id",
                params=("group_id",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_groups_create_groups",
                params=("representation",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_groups_delete_groups_by_group_id",
                params=("group_id",),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "manage-roles",
        description="Create, read and delete realm roles",
        steps=(
            ToolStep(
                "keycloak_agent_roles_list_roles",
                params=("realm", "briefRepresentation", "first"),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_agent_roles_get_roles_by_role_name",
                params=("role_name",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_roles_get_roles_by_id_by_role_id",
                params=("role_id",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_roles_create_roles",
                params=("representation",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_roles_delete_roles_by_role_name",
                params=("role_name",),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "manage-organizations",
        description="Create, read and delete organizations",
        steps=(
            ToolStep(
                "keycloak_agent_organizations_list_organizations",
                params=("realm", "briefRepresentation", "exact"),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_agent_organizations_get_organizations_by_org_id",
                params=("org_id",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_organizations_create_organizations",
                params=("representation",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_organizations_delete_organizations_by_org_id",
                params=("org_id",),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "manage-identity-providers",
        description="Connect, read and remove external identity providers",
        steps=(
            ToolStep(
                "keycloak_agent_idps_list_identity_provider_instances",
                params=("realm", "briefRepresentation", "capability"),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_agent_idps_get_identity_provider_instances_by_alias",
                params=("alias",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_idps_create_identity_provider_instances",
                params=("representation",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_idps_delete_identity_provider_instances_by_alias",
                params=("alias",),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "manage-authentication-flows",
        description="Read, create and delete authentication flows",
        steps=(
            ToolStep(
                "keycloak_agent_authentication_list_authentication_authenticator_providers",
                params=("realm",),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_agent_authentication_list_authentication_flows",
                params=("realm",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_authentication_get_authentication_flows_by_id",
                params=("id",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_authentication_create_authentication_flows",
                params=("representation",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_authentication_delete_authentication_flows_by_id",
                params=("id",),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "manage-realm-components",
        description="Read, create and delete realm components such as key providers and user federation",
        steps=(
            ToolStep(
                "keycloak_agent_components_list_components",
                params=("realm", "name", "parent"),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_agent_components_get_components_by_id",
                params=("id",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_components_create_components",
                params=("representation",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_components_delete_components_by_id",
                params=("id",),
                result=("result",),
                refusals=(
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "release-locked-out-users",
        description="Clear brute-force login failures so locked users can sign in",
        steps=(
            ToolStep(
                "keycloak_agent_attack_detection_delete_attack_detection_brute_force_users",
                params=("realm", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                    Refusal(
                        "confirmation_required",
                        "the destructive call omits confirm=true",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "discover-admin-api",
        description="Find the Admin API method that does something",
        steps=(
            ToolStep(
                "keycloak_agent_info_list_methods",
                params=("tag",),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_agent_info_search_methods",
                params=("query",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_agent_info_method_details",
                params=("method_name",),
                result=("result",),
                refusals=(),
            ),
        ),
    ),
    ToolUseContract(
        "ingest-identity-inventory",
        description="Mirror realms, users, clients and groups into the knowledge graph",
        steps=(
            ToolStep(
                "keycloak_ingest_realms",
                params=(),
                result=("result",),
                refusals=(
                    Refusal(
                        "access_denied", "the credential lacks access to the system"
                    ),
                ),
            ),
            ToolStep(
                "keycloak_ingest_users",
                params=("realm",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_ingest_clients",
                params=("realm",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "keycloak_ingest_groups",
                params=("realm",),
                result=("result",),
                refusals=(),
            ),
        ),
    ),
)

LINKS: tuple[SurfaceLink, ...] = (
    SurfaceLink(
        "onboard-an-sso-client",
        tools=(
            "keycloak_list_realms",
            "keycloak_find_client_by_client_id",
            "keycloak_create_client",
            "keycloak_get_client",
            "keycloak_get_client_secret",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-sso-integrator"),
        skills=("keycloak-client-onboarder",),
    ),
    SurfaceLink(
        "rotate-a-client-secret",
        tools=(
            "keycloak_get_client",
            "keycloak_regenerate_client_secret",
            "keycloak_regenerate_client_secret_by_client_id",
            "keycloak_get_client_secret",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-sso-integrator"),
        skills=("keycloak-client-onboarder",),
    ),
    SurfaceLink(
        "retire-an-sso-client",
        tools=(
            "keycloak_list_clients",
            "keycloak_get_client",
            "keycloak_delete_client",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-sso-integrator"),
        skills=("keycloak-client-onboarder",),
    ),
    SurfaceLink(
        "review-realm-clients",
        tools=("keycloak_list_realms", "keycloak_get_realm", "keycloak_list_clients"),
        prompts=(
            "keycloak-mcp-operator",
            "keycloak-mcp-sso-integrator",
            "keycloak-mcp-realm-administrator",
        ),
        skills=("keycloak-client-onboarder",),
    ),
    SurfaceLink(
        "provision-a-realm",
        tools=(
            "keycloak_list_realms",
            "keycloak_create_realm",
            "keycloak_get_realm",
            "keycloak_delete_realm",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-realm-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "onboard-a-user",
        tools=(
            "keycloak_list_users",
            "keycloak_create_user",
            "keycloak_get_user",
            "keycloak_reset_password",
            "keycloak_agent_groups_list_groups",
            "keycloak_agent_users_list_users_by_user_id_groups",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-identity-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "offboard-a-user",
        tools=(
            "keycloak_list_users",
            "keycloak_get_user",
            "keycloak_agent_users_list_users_by_user_id_groups",
            "keycloak_delete_user",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-identity-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "manage-groups",
        tools=(
            "keycloak_agent_groups_list_groups",
            "keycloak_agent_groups_get_groups_by_group_id",
            "keycloak_agent_groups_create_groups",
            "keycloak_agent_groups_delete_groups_by_group_id",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-identity-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "manage-roles",
        tools=(
            "keycloak_agent_roles_list_roles",
            "keycloak_agent_roles_get_roles_by_role_name",
            "keycloak_agent_roles_get_roles_by_id_by_role_id",
            "keycloak_agent_roles_create_roles",
            "keycloak_agent_roles_delete_roles_by_role_name",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-identity-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "manage-organizations",
        tools=(
            "keycloak_agent_organizations_list_organizations",
            "keycloak_agent_organizations_get_organizations_by_org_id",
            "keycloak_agent_organizations_create_organizations",
            "keycloak_agent_organizations_delete_organizations_by_org_id",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-identity-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "manage-identity-providers",
        tools=(
            "keycloak_agent_idps_list_identity_provider_instances",
            "keycloak_agent_idps_get_identity_provider_instances_by_alias",
            "keycloak_agent_idps_create_identity_provider_instances",
            "keycloak_agent_idps_delete_identity_provider_instances_by_alias",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-realm-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "manage-authentication-flows",
        tools=(
            "keycloak_agent_authentication_list_authentication_authenticator_providers",
            "keycloak_agent_authentication_list_authentication_flows",
            "keycloak_agent_authentication_get_authentication_flows_by_id",
            "keycloak_agent_authentication_create_authentication_flows",
            "keycloak_agent_authentication_delete_authentication_flows_by_id",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-realm-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "manage-realm-components",
        tools=(
            "keycloak_agent_components_list_components",
            "keycloak_agent_components_get_components_by_id",
            "keycloak_agent_components_create_components",
            "keycloak_agent_components_delete_components_by_id",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-realm-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "release-locked-out-users",
        tools=(
            "keycloak_agent_attack_detection_delete_attack_detection_brute_force_users",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-identity-administrator"),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "discover-admin-api",
        tools=(
            "keycloak_agent_info_list_methods",
            "keycloak_agent_info_search_methods",
            "keycloak_agent_info_method_details",
        ),
        prompts=(
            "keycloak-mcp-operator",
            "keycloak-mcp-sso-integrator",
            "keycloak-mcp-realm-administrator",
        ),
        skills=("keycloak-agent-operations",),
    ),
    SurfaceLink(
        "ingest-identity-inventory",
        tools=(
            "keycloak_ingest_realms",
            "keycloak_ingest_users",
            "keycloak_ingest_clients",
            "keycloak_ingest_groups",
        ),
        prompts=("keycloak-mcp-operator", "keycloak-mcp-identity-administrator"),
        skills=("keycloak-agent-operations",),
    ),
)

LOCATIONS: tuple[DataLocation, ...] = (
    DataLocation(
        "keycloak-realms",
        ("Organization",),
        "KEYCLOAK_URL",
        "keycloak_list_realms",
        federation_key="realm",
    ),
    DataLocation(
        "keycloak-users",
        ("IdentityUser",),
        "KEYCLOAK_URL",
        "keycloak_list_users",
        federation_key="user_id",
    ),
    DataLocation(
        "keycloak-clients",
        ("Application",),
        "KEYCLOAK_URL",
        "keycloak_list_clients",
        federation_key="client_uuid",
    ),
    DataLocation(
        "keycloak-groups",
        ("IdentityGroup",),
        "KEYCLOAK_URL",
        "keycloak_agent_groups_list_groups",
        federation_key="group_id",
    ),
    DataLocation(
        "keycloak-roles",
        ("IdentityRole",),
        "KEYCLOAK_URL",
        "keycloak_agent_roles_list_roles",
        federation_key="role_name",
    ),
)

ROLES: tuple[BusinessRole, ...] = (
    BusinessRole(
        "sso-integrator",
        tasks=(
            "onboard-an-sso-client",
            "rotate-a-client-secret",
            "retire-an-sso-client",
            "review-realm-clients",
            "discover-admin-api",
        ),
    ),
    BusinessRole(
        "identity-administrator",
        tasks=(
            "onboard-a-user",
            "offboard-a-user",
            "manage-groups",
            "manage-roles",
            "manage-organizations",
            "release-locked-out-users",
            "ingest-identity-inventory",
        ),
    ),
    BusinessRole(
        "realm-administrator",
        tasks=(
            "provision-a-realm",
            "manage-identity-providers",
            "manage-authentication-flows",
            "manage-realm-components",
            "discover-admin-api",
            "review-realm-clients",
        ),
    ),
)
