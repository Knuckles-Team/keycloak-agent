---
name: keycloak-agent-operations
skill_type: skill
description: >-
  Administer Keycloak through the keycloak-mcp tools: realms, users, groups, roles, organizations, identity providers, authentication flows, components and the Admin API catalog. Use for identity administration. For application SSO clients use keycloak-client-onboarder.
license: MIT
tags: [keycloak, sso, identity]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---
# Keycloak operations

Every tool takes a realm (default master). Group, role, organization and flow tools address objects by id or name in that realm.

## Rules

- Name the realm in every request and report.
- Deletes take confirm=true; pass it only after the person agrees.
- Verify sign-in through the browser path after changing flows or providers.

## Task workflows

### provision-a-realm

Create or remove a realm. Contract steps, in order:

1. `keycloak_list_realms`(no arguments)
2. `keycloak_create_realm`(realm_name)
3. `keycloak_get_realm`(realm_name)
4. `keycloak_delete_realm`(realm_name; optional confirm) (destructive: pass confirm=true only after the person agrees)

### onboard-a-user

Create a user, set a temporary password and place the user in groups. Contract steps, in order:

1. `keycloak_list_users`(realm; optional search)
2. `keycloak_create_user`(realm, username; optional email, enabled)
3. `keycloak_get_user`(realm, user_id)
4. `keycloak_reset_password`(realm, user_id, password; optional temporary)
5. `keycloak_agent_groups_list_groups`(; optional realm, briefRepresentation, exact, first, max, populateHierarchy)
6. `keycloak_agent_users_list_users_by_user_id_groups`(user_id; optional realm, briefRepresentation, first, max, search)

### offboard-a-user

Find a user, review their groups and delete the account. Contract steps, in order:

1. `keycloak_list_users`(realm; optional search)
2. `keycloak_get_user`(realm, user_id)
3. `keycloak_agent_users_list_users_by_user_id_groups`(user_id; optional realm, briefRepresentation, first, max, search)
4. `keycloak_delete_user`(realm, user_id; optional confirm) (destructive: pass confirm=true only after the person agrees)

### manage-groups

Create, read and delete groups. Contract steps, in order:

1. `keycloak_agent_groups_list_groups`(; optional realm, briefRepresentation, exact, first, max, populateHierarchy)
2. `keycloak_agent_groups_get_groups_by_group_id`(group_id; optional realm)
3. `keycloak_agent_groups_create_groups`(representation; optional realm)
4. `keycloak_agent_groups_delete_groups_by_group_id`(group_id; optional realm, confirm) (destructive: pass confirm=true only after the person agrees)

### manage-roles

Create, read and delete realm roles. Contract steps, in order:

1. `keycloak_agent_roles_list_roles`(; optional realm, briefRepresentation, first, max, search)
2. `keycloak_agent_roles_get_roles_by_role_name`(role_name; optional realm)
3. `keycloak_agent_roles_get_roles_by_id_by_role_id`(role_id; optional realm)
4. `keycloak_agent_roles_create_roles`(representation; optional realm)
5. `keycloak_agent_roles_delete_roles_by_role_name`(role_name; optional realm, confirm) (destructive: pass confirm=true only after the person agrees)

### manage-organizations

Create, read and delete organizations. Contract steps, in order:

1. `keycloak_agent_organizations_list_organizations`(; optional realm, briefRepresentation, exact, first, max, q)
2. `keycloak_agent_organizations_get_organizations_by_org_id`(org_id; optional realm)
3. `keycloak_agent_organizations_create_organizations`(representation; optional realm)
4. `keycloak_agent_organizations_delete_organizations_by_org_id`(org_id; optional realm, confirm) (destructive: pass confirm=true only after the person agrees)

### manage-identity-providers

Connect, read and remove external identity providers. Contract steps, in order:

1. `keycloak_agent_idps_list_identity_provider_instances`(; optional realm, briefRepresentation, capability, first, max, realmOnly)
2. `keycloak_agent_idps_get_identity_provider_instances_by_alias`(alias; optional realm)
3. `keycloak_agent_idps_create_identity_provider_instances`(representation; optional realm)
4. `keycloak_agent_idps_delete_identity_provider_instances_by_alias`(alias; optional realm, confirm) (destructive: pass confirm=true only after the person agrees)

### manage-authentication-flows

Read, create and delete authentication flows. Contract steps, in order:

1. `keycloak_agent_authentication_list_authentication_authenticator_providers`(; optional realm)
2. `keycloak_agent_authentication_list_authentication_flows`(; optional realm)
3. `keycloak_agent_authentication_get_authentication_flows_by_id`(id; optional realm)
4. `keycloak_agent_authentication_create_authentication_flows`(representation; optional realm)
5. `keycloak_agent_authentication_delete_authentication_flows_by_id`(id; optional realm, confirm) (destructive: pass confirm=true only after the person agrees)

### manage-realm-components

Read, create and delete realm components such as key providers and user federation. Contract steps, in order:

1. `keycloak_agent_components_list_components`(; optional realm, name, parent, providerId, type)
2. `keycloak_agent_components_get_components_by_id`(id; optional realm)
3. `keycloak_agent_components_create_components`(representation; optional realm)
4. `keycloak_agent_components_delete_components_by_id`(id; optional realm, confirm) (destructive: pass confirm=true only after the person agrees)

### release-locked-out-users

Clear brute-force login failures so locked users can sign in. Contract steps, in order:

1. `keycloak_agent_attack_detection_delete_attack_detection_brute_force_users`(; optional realm, confirm) (destructive: pass confirm=true only after the person agrees)

### discover-admin-api

Find the Admin API method that does something. Contract steps, in order:

1. `keycloak_agent_info_list_methods`(; optional tag)
2. `keycloak_agent_info_search_methods`(query)
3. `keycloak_agent_info_method_details`(method_name)

### ingest-identity-inventory

Mirror realms, users, clients and groups into the knowledge graph. Contract steps, in order:

1. `keycloak_ingest_realms`(no arguments)
2. `keycloak_ingest_users`(realm; optional search)
3. `keycloak_ingest_clients`(realm)
4. `keycloak_ingest_groups`(realm)
