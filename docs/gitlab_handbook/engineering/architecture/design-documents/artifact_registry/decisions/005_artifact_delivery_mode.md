---
title: "Artifact Registry ADR 005: Artifact Delivery Mode"
owning-stage: "~devops::package"
description: "Decision to support redirect and proxy artifact delivery as a two-axis model: an instance-level default with an always-available per-namespace override"
toc_hide: true
---

<!-- Design Documents often contain forward-looking statements -->
<!-- vale gitlab.FutureTense = NO -->

## Context

When a client downloads an artifact (container layer, Maven JAR, npm tarball), the Artifact Registry must decide how to serve the content from object storage. Two established patterns exist in the industry and within GitLab:

1. **Redirect mode**: the service responds with an HTTP redirect (302/307) to a pre-signed object storage URL. The client fetches the content directly from the storage backend. The service never handles artifact bytes on the download path.
2. **Proxy mode**: the service fetches the content from object storage and streams it through to the client. All artifact bytes flow through the service.

Both the GitLab monolith and the Container Registry support both modes today:

- **Container Registry**: `storage.redirect.disable` (boolean, default `false`). When redirects are disabled, the registry streams content directly to the client instead of redirecting to the storage backend.
- **GitLab monolith**: `proxy_download` setting (default `false`) across all object-storage-backed features (artifacts, LFS, packages, uploads).

### Why proxy mode is needed

The GitLab [documentation](https://docs.gitlab.com/administration/object_storage/) lists real deployment scenarios where redirects do not work and proxying is mandatory:

- **Firewall restrictions**: Client networks block direct access to object storage endpoints. This is common in regulated environments and air-gapped or semi-isolated networks.
- **Untrusted CAs**: Object storage uses certificates from a CA that clients do not trust (common with third-party S3-compatible backends such as NetApp appliances and Ceph Object Gateway).
- **Non-public storage backends**: The object storage endpoint is not reachable from the client network (private VPC, internal-only endpoint).
- **HTTPS downgrade**: The object storage endpoint serves over plain HTTP, causing mixed-content errors when the client accessed the registry over HTTPS.
- **CORS restrictions**: Browser-based clients cannot follow cross-origin redirects to object storage without proper CORS headers on the storage side.
- **Pre-signed URL security**: Pre-signed URLs are time-limited but not tied to a specific user or session. In high-security environments, organizations prefer that artifact bytes never leave the service's network boundary.

Some of these scenarios affect GitLab customers at scale today, including customers using third-party S3-compatible solutions (NetApp, Ceph Object Gateway) where CA/firewall/routing limitations are a practical reality.

### The dual-personality deployment model

The Artifact Registry is designed to operate as a modular service that can serve multiple deployment models: GitLab.com (SaaS), GitLab Dedicated, and Self-Managed instances. In the remote/dual-personality model, a Self-Managed or Dedicated instance connects to the GitLab.com Artifact Registry as a remote backend.

In this model, the GitLab.com Artifact Registry serves downloads to clients that may be behind corporate firewalls with no ability to allowlist the IP ranges of the underlying storage provider (GCS, Cloud CDN). The service must be able to proxy artifact content for those namespaces while continuing to redirect for namespaces whose clients can reach storage directly.

This makes a global (instance-level) redirect-or-proxy toggle insufficient. The per-namespace setting ([ADR-022](022_namespace_decoupling.md)) must be available regardless of the instance default, because different namespaces on the same instance or organization may have different network constraints.

## Decision

**The Artifact Registry supports two artifact delivery patterns — redirect and proxy — selected as a two-axis model: an instance-level default plus an always-available per-namespace override.**

### Axis 1: Instance default

The instance is configured with one of two default delivery patterns:

- **Redirect** (the recommended default). All artifact downloads are served by redirecting the client to a pre-signed object storage URL. The client fetches the content directly from the storage backend. The service never handles artifact bytes on the download path. This minimizes service load and egress bandwidth — all responses from the service are small, which allows tight timeouts and a smaller resource footprint. Appropriate for deployments where all clients can reach the storage backend directly.
- **Proxy**. All artifact downloads are served by streaming the content from object storage through the service. All artifact bytes flow through the service. This is for deployments where clients cannot reach the storage backend directly, such as Self-Managed instances behind firewalls. Proxy requires the service to handle large response bodies (potentially multi-GB for container layers), which affects write timeouts, memory allocation, and bandwidth capacity.

The instance default is set in the service configuration and changes only on restart.

### Axis 2: Per-namespace override

A nullable per-namespace override (stored alongside the namespace record, see [ADR-022](022_namespace_decoupling.md) and [ADR-007](007_database_schema.md)) is available on every instance regardless of the instance default. Its tri-state semantics are:

- `NULL` — inherit the instance default.
- `redirect` — force redirect for this namespace.
- `proxy` — force proxy for this namespace.

The effective delivery pattern for any download request is:

```text
effective = namespace.delivery_mode_override ?? instance.delivery_mode
```

The per-namespace setting is managed by GitLab organization owners through the namespace management API (owned by S17 in the implementation specs). The granularity is per-namespace, not per-organization, per-repository, or per-artifact.

This two-axis form is the only knob shape the service exposes. There is no separate "hybrid" instance mode — the override is the same column on every instance, and operators choose which combinations they need.

### Scenarios this expresses

Every deployment scenario the Artifact Registry needs to support reduces to a combination of the two axes:

- **Single-tenant, all clients reach storage.** Instance default = `redirect`, no namespace overrides set.
- **Single-tenant behind firewall / with untrusted CA.** Instance default = `proxy`, no namespace overrides set.
- **Multi-tenant SaaS / dual-personality** (GitLab.com): instance default = `redirect`, individual namespaces whose clients cannot reach storage set their override to `proxy` (or vice versa).
- **Single-tenant with one exceptional namespace.** Instance default matches the common case; the exception sets its override to the other value.

### Constraints on the system

Supporting both delivery patterns has implications for the service design:

- **Timeouts**. Redirect responses are small and fast. Proxy responses can be multi-GB and take minutes. The service must support extended timeouts for proxy downloads without affecting redirect performance.
- **Resource footprint**. Proxy downloads stream large payloads through the service, increasing memory and bandwidth requirements per request. Capacity planning must account for the proportion of traffic served as proxy.
- **Storage backend access**. The storage backend must support both generating pre-signed URLs (for redirect) and streaming reads (for proxy).
- **CDN interaction**. Redirect benefits from CDN caching because clients fetch directly from CDN-backed storage URLs. Proxy bypasses CDN, losing the caching benefit. Implementation specs bypass the CDN / URL-cache middleware stack end-to-end when the effective delivery pattern is proxy.
- **Monitoring**. The service must distinguish between redirect and proxy traffic in metrics and logs so operators can track bandwidth, latency, and capacity impact per pattern.
- **Per-namespace lookup**. The override is read from the same namespace row that the request handlers already join for authorization and routing — no separate lookup or double join is required. The cost is a single nullable column on a query the handler already performs.

## Consequences

### Positive

1. **No customer impact from network restrictions**. Deployments behind firewalls, with untrusted CAs, or without direct storage access can use the Artifact Registry via proxy without workarounds.
2. **Parity with existing GitLab features**. Both the Container Registry and the GitLab monolith support proxy download. Not supporting it in the Artifact Registry would be a regression for customers migrating from those systems.
3. **Dual-personality support**. The override enables the remote model where GitLab.com serves namespaces with different network constraints without forcing all traffic through the service.
4. **Operationally consistent surface**. Operators see one instance-level knob and one per-namespace column on every deployment. There is no instance-mode gate that silently disables the per-namespace setting.
5. **Override is opt-in per namespace**. Deployments that do not need per-namespace control pay nothing — overrides are `NULL` and the effective pattern is just the instance default.

### Negative

1. **Increased service complexity**. The download path must handle two fundamentally different response patterns (small redirect vs large streaming body), with different timeout, memory, and error-handling characteristics.
2. **Higher resource requirements for proxy traffic**. Namespaces or instances served as proxy consume significantly more bandwidth and memory per request. A small number of high-traffic proxy namespaces can disproportionately affect service capacity.
3. **Reduced CDN effectiveness for proxy traffic**. Proxy bypasses CDN, losing the caching benefit that reduces storage backend load and improves download latency.
4. **Both patterns to test and maintain**. Each pattern has different behavior on the download path. Testing must cover both, in both the "no override set" and "override forces the opposite" combinations.

## Alternatives

### Alternative 1: Redirect only

The service always responds with redirects. Customers whose clients cannot reach storage must solve the problem outside the service (VPN, proxy sidecar, firewall rules).

**Pros:**

- Simplest service design. All responses are small. Tight timeouts, minimal memory.
- CDN is always effective.

**Cons:**

- **Breaks real customer deployments**: firewalls, untrusted CAs, and non-public backends are not hypothetical. These affect GitLab customers today.
- **Regression from existing features**: both the Container Registry and GitLab monolith support proxy download. Removing the capability is a step backward.
- **Blocks the dual-personality model**: remote Self-Managed/Dedicated instances connecting to GitLab.com cannot function if their clients cannot reach GCS/Cloud CDN.

**Why rejected:** The customer impact is concrete and well-documented.

### Alternative 2: Three named instance modes (`redirect` / `proxy` / `hybrid`)

The instance is configured to one of three modes: `redirect` (no per-namespace lookup; instance always redirects), `proxy` (no per-namespace lookup; instance always proxies), or `hybrid` (per-namespace override evaluated on each request, instance default = redirect). This was the previous decision recorded in this ADR.

**Pros:**

- Slightly cheaper on the download path in the `redirect` and `proxy` modes, where the per-namespace column is not read at all.
- Mode names map directly to the original three scenarios in the design discussion.

**Cons:**

- **Operationally inconsistent**. The per-namespace override is available in `hybrid` mode and unavailable in the other two. Operators have to know which instance-mode they are on to know whether the namespace setting they are looking at means anything. Namespace owners face the same ambiguity from the other side: their override may or may not take effect depending on a global setting they typically cannot see.
- **No additional expressiveness**. Every scenario the three-mode form expresses is expressible by `(instance default, override)`: `redirect` mode ≡ instance=`redirect` with zero overrides; `proxy` mode ≡ instance=`proxy` with zero overrides; `hybrid` mode ≡ instance=`redirect` (or `proxy`) with some namespaces set to the opposite value.
- **The optimization is marginal**. Skipping the override column read in the `redirect` / `proxy` modes saves nothing measurable — the handler already loads the namespace row for authorization and routing on every request, so the override read is part of an existing query.
- **One-way door if exceptions are ever needed**. A deployment that picks `redirect` or `proxy` mode today gives up the ability to set a single exceptional namespace override without an instance-level mode change (and the implied restart).

**Why rejected:** The two-axis form covers the same ground with a smaller, more consistent surface. The marginal cost saved by the three-mode form is not worth the operational ambiguity it introduces. This alternative was the original decision and is now superseded.

### Alternative 3: Per-repository configuration

Allow the delivery override at the repository level rather than the namespace level.

**Pros:**

- Finer-grained control. A namespace could use redirect for most repositories and proxy only for specific ones.

**Cons:**

- **Over-engineering for the problem**: network constraints apply to the namespace's client environment, not to individual repositories. If a client cannot reach storage, it cannot reach it for any repository in that namespace.
- **Management overhead**: administrators would need to configure every repository individually.
- **Inconsistent user experience**: different repositories in the same namespace behaving differently is confusing.

**Why rejected:** Network constraints usually apply at the namespace/network boundary, not at the repository level. Per-namespace is the right granularity. If concrete user demand emerges, a per-repository override that inherits from the namespace setting but can be overridden individually could be considered in the future, but this is out of scope.

## References

- [Container Registry `storage.redirect.disable`](https://gitlab.com/gitlab-org/container-registry/-/blob/master/registry/storage/blobserver.go)
- [GitLab monolith `proxy_download` documentation](https://docs.gitlab.com/administration/object_storage/)
- [ADR-007: Database Schema](007_database_schema.md) (`namespaces.delivery_mode_override` column)
- [ADR-008: Content-Addressable Storage](008_content_addressable_storage.md) (read path)
- [ADR-009: API Design](009_api_design.md) (download endpoints)
- [ADR-022: Namespace Decoupling](022_namespace_decoupling.md) (namespace as configuration boundary)
- [S01: HTTP Server and Routing](https://gitlab.com/gitlab-org/ops/artifact-registry/-/merge_requests/34) (timeout and response-size assumptions affected by this decision)
- [S06: Storage Layer](https://gitlab.com/gitlab-org/ops/artifact-registry/-/merge_requests/108) (implements the resolution algorithm; `StorageConfig.delivery_mode` proto field, `BlobStore.OpenBlob` `WithDeliveryMode` option, `WithForceStream` precedence)
- [Related discussion on redirect vs proxy](https://gitlab.com/gitlab-org/ops/artifact-registry/-/merge_requests/34#note_3276797114)
- [Two-axis collapse rationale](https://gitlab.com/gitlab-org/ops/artifact-registry/-/merge_requests/108#note_3353135649) (MR-108 discussion that drove this decision)
