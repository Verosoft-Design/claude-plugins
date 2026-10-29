---
fno-version: [all]
domain: security
keywords: [menu-item, privilege, duty, role, entry-point, security]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# Every new menu item needs a privilege, in a duty, in a role

## Description

In Finance and Operations, users reach forms, reports and actions through menu items, and access to a menu item is granted only through a security privilege that names it as an entry point. Privileges are grouped into duties and duties into roles. A menu item that no privilege covers can be used only by the System administrator role. xppbp reports it as `BPErrorMenuItemNotCoveredByPrivilege`, and a privilege no duty references as `BPErrorPrivilegeNotCoveredByDuty`. On 2026-10-29 a model with 80 menu items and no privileges reported the first on its menu items.

## Best Practice

With each new display, output or action menu item, add or extend a privilege (view and maintain variants where the form edits data) and put it in a duty. Add the duty to an existing role through a role extension, or to a new role for a new persona. Extend standard duties and roles with `AxSecurityDutyExtension` and `AxSecurityRoleExtension`, never by over-layering. Check the result with the d365fo MCP's `security_info` and a BP check of the menu item.

## Anti Pattern

Shipping menu items without privileges and testing only as an administrator, which hides the gap until a real user gets "You do not have access". Adding privileges straight into a standard duty or role instead of an extension.
