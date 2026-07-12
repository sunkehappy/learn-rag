---
title: 'Organizations Release Process'
description: 'Release process specific Organization features.'
owning-stage: "~devops::tenant scale"
group: Organizations
toc_hide: true
---

This document outlines the release process for specific Organization features and [stages](../../../infrastructure-platforms/tenant-scale/organizations/release-stages.md).

## Artifact Registry Beta (design partners)

We will manually onboard ~25 design partners onto Organizations so that they can start using Artifact Registry.

### Step 1 - Enable the Organizations UI

**Owned by:** ~group::organizations

Enable the `org_stage_beta` feature flag globally.

```shell
/chatops run feature set org_stage_beta true
```

Enabling this feature flag will show the `Organizations` menu item in the `Your work` sidebar for users that have an Organization with the a [state of `active`](lifecycle.md#states). This means that users should not see any changes in the UI until after steps 3 and 4.

### Step 2 - Identify design partner's top-level groups (TLGs)

**Owned by:** ~devops::package

Identify design partners to be onboarded to Organizations and provide a list of TLG full paths.  

### Step 3 - Backfill TLGs with new Organization

**Owned by:** ~group::organizations

Enable the `root_group_organization_backfill` feature flag for the TLGs using the `group` actor. 

```shell
/chatops run feature set --group=a-customer-group root_group_organization_backfill true
```

This will do the following:

1. Create an Organization with the same name and path as the TLG
1. Transfer TLG into this Organization

### Step 4 - Confirm Organization and sync TLG members

**Owned by:** ~group::organizations

Enable the `root_group_organization_confirm` feature flag for the TLGs using the `group` actor. 

```shell
/chatops run feature set --group=a-customer-group root_group_organization_confirm true
```

This will do the following:

1. Confirm the Organization
1. Add TLG members as Organization Members. Owners become Organization Administrators and all other Members become Organization Regular Members.

### Step 5 - Notify design partners

**Owned by:** ~devops::package

Notify design partners with a link to documentation that explains how to enable and start using Artifact Registry.

### Step 6 - Enable Artifact Registry

**Owned by:** ~devops::package

The customer will now see an `Organizations` menu item in the `Your work` sidebar. They can enable under the `Artifacts` menu item in their Organization. Once enabled they can start using Artifact Registry.

### Rollback

```shell
/chatops run feature set org_stage_beta false
/chatops run feature set --group=a-customer-group root_group_organization_backfill false
/chatops run feature set --group=a-customer-group root_group_organization_confirm false
```

## Artifact Registry Beta (self-serve)

TBD
