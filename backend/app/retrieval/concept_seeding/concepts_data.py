"""Curated system-design concept KB. Each entry is grounding material the debate
personas retrieve from before arguing. dimension_hint aligns loosely with the
persona dimensions (constraints, performance, security, feedback) or "general"."""

CONCEPTS = [
    # --- constraints ---
    {
        "id": "cap-theorem",
        "title": "CAP Theorem",
        "dimension_hint": "constraints",
        "tags": ["distributed-systems", "consistency"],
        "text": "CAP theorem: a distributed system can provide at most two of Consistency, "
        "Availability, and Partition tolerance during a network partition. Since partitions "
        "are unavoidable at scale, real systems choose between CP (reject requests to stay "
        "consistent) and AP (stay available, accept temporary inconsistency).",
    },
    {
        "id": "pacelc",
        "title": "PACELC Theorem",
        "dimension_hint": "constraints",
        "tags": ["distributed-systems", "latency", "consistency"],
        "text": "PACELC extends CAP: even without a partition (E), a system must trade off "
        "Latency versus Consistency. This explains why systems like DynamoDB favor low "
        "latency with eventual consistency even in the normal case.",
    },
    {
        "id": "consistency-models",
        "title": "Consistency Models",
        "dimension_hint": "constraints",
        "tags": ["consistency"],
        "text": "Common consistency models, strongest to weakest: linearizability (reads see "
        "latest write, globally ordered), sequential consistency, causal consistency (respects "
        "cause-effect order), and eventual consistency (replicas converge given no new writes). "
        "Stronger consistency costs latency and availability.",
    },
    {
        "id": "sla-slo-sli",
        "title": "SLA, SLO, and SLI",
        "dimension_hint": "constraints",
        "tags": ["reliability"],
        "text": "SLI (Service Level Indicator) is a measured metric (e.g. p99 latency). SLO "
        "(Objective) is the internal target for that metric. SLA (Agreement) is the external, "
        "often contractual, commitment with consequences for missing it. SLOs should be "
        "stricter than SLAs to leave error-budget margin.",
    },
    {
        "id": "error-budget",
        "title": "Error Budgets",
        "dimension_hint": "constraints",
        "tags": ["reliability"],
        "text": "An error budget is 1 minus the SLO (e.g. 99.9% SLO leaves a 0.1% budget). "
        "Teams can spend the budget on risky releases; once exhausted, the team should freeze "
        "features and focus on reliability. This aligns velocity with reliability constraints.",
    },
    {
        "id": "capacity-planning",
        "title": "Capacity Planning",
        "dimension_hint": "constraints",
        "tags": ["scale"],
        "text": "Capacity planning estimates required resources from expected QPS, payload size, "
        "growth rate, and peak-to-average traffic ratio. A common mistake is planning for "
        "average load instead of peak load plus headroom (commonly 30-50%) for spikes and "
        "failover.",
    },
    {
        "id": "vertical-vs-horizontal-scaling",
        "title": "Vertical vs Horizontal Scaling",
        "dimension_hint": "constraints",
        "tags": ["scale"],
        "text": "Vertical scaling (bigger machines) is simple but has a hard ceiling and a single "
        "point of failure. Horizontal scaling (more machines) has near-unlimited ceiling but "
        "requires the application to be stateless or use consistent partitioning, and adds "
        "operational complexity.",
    },
    {
        "id": "build-vs-buy",
        "title": "Build vs Buy",
        "dimension_hint": "constraints",
        "tags": ["tradeoffs", "team"],
        "text": "Building in-house maximizes control and avoids vendor lock-in but costs "
        "engineering time and ongoing maintenance. Buying (managed services, SaaS) is faster "
        "to ship and offloads operational burden but introduces cost-at-scale and dependency "
        "risk. Small teams should default to buy for non-differentiating capabilities.",
    },
    {
        "id": "team-topology-constraint",
        "title": "Team Size as a Design Constraint",
        "dimension_hint": "constraints",
        "tags": ["team", "conway"],
        "text": "Conway's Law: system architecture tends to mirror team communication structure. "
        "A small team should avoid architectures (e.g. many microservices) that require "
        "coordination overhead exceeding the team's size — a modular monolith is often the "
        "right constraint-aware choice.",
    },
    {
        "id": "budget-constraint",
        "title": "Budget as a Hard Constraint",
        "dimension_hint": "constraints",
        "tags": ["cost"],
        "text": "Infrastructure cost constraints should be stated in the brief explicitly (e.g. "
        "free tier only, or a monthly ceiling). Designs that assume unlimited compute/storage "
        "budget silently violate this constraint and must be flagged during debate.",
    },
    {
        "id": "compliance-constraint",
        "title": "Regulatory / Compliance Constraints",
        "dimension_hint": "constraints",
        "tags": ["compliance"],
        "text": "Constraints like GDPR (data residency, right to erasure), HIPAA (PHI handling), "
        "or PCI-DSS (cardholder data) shape storage location, encryption, retention, and audit "
        "logging requirements. These are non-negotiable constraints, not performance tradeoffs.",
    },
    {
        "id": "backward-compatibility",
        "title": "Backward Compatibility Constraint",
        "dimension_hint": "constraints",
        "tags": ["api", "migration"],
        "text": "Any system with existing clients must treat API/schema backward compatibility "
        "as a constraint: additive-only changes, versioned endpoints, or dual-write migration "
        "periods. Breaking changes require a deprecation window communicated to consumers.",
    },
    {
        "id": "data-gravity",
        "title": "Data Gravity",
        "dimension_hint": "constraints",
        "tags": ["architecture"],
        "text": "Data gravity: as datasets grow, it becomes cheaper to bring compute to the data "
        "than to move data to compute. This constrains where new services should be deployed "
        "and discourages naive cross-region joins on large tables.",
    },

    # --- performance ---
    {
        "id": "caching-patterns",
        "title": "Caching Patterns",
        "dimension_hint": "performance",
        "tags": ["cache"],
        "text": "Common caching patterns: cache-aside (app reads cache, falls back to DB and "
        "populates cache on miss), read-through (cache itself loads from DB), write-through "
        "(writes go to cache and DB synchronously), and write-behind (writes go to cache, "
        "flushed to DB asynchronously, risking data loss on crash).",
    },
    {
        "id": "cache-invalidation",
        "title": "Cache Invalidation",
        "dimension_hint": "performance",
        "tags": ["cache"],
        "text": "Cache invalidation strategies: TTL-based expiry (simple, bounded staleness), "
        "explicit invalidation on write (fresher, more complex), and versioned/keyed cache "
        "entries. Phil Karlton's quip stands: cache invalidation is one of the two hard "
        "problems in computer science.",
    },
    {
        "id": "cdn",
        "title": "CDN (Content Delivery Network)",
        "dimension_hint": "performance",
        "tags": ["cache", "latency"],
        "text": "A CDN caches static (and sometimes dynamic) content at edge nodes close to "
        "users, cutting latency and offloading origin servers. Effective for read-heavy, "
        "geographically distributed traffic; less useful for highly personalized or "
        "write-heavy workloads.",
    },
    {
        "id": "load-balancing",
        "title": "Load Balancing Strategies",
        "dimension_hint": "performance",
        "tags": ["scale"],
        "text": "Load balancer algorithms: round robin (simple, ignores server load), least "
        "connections (routes to least busy server), and consistent hashing (routes by key, "
        "useful for cache locality). L4 (transport-layer) balancers are faster; L7 "
        "(application-layer) balancers can route on content/headers.",
    },
    {
        "id": "database-indexing",
        "title": "Database Indexing",
        "dimension_hint": "performance",
        "tags": ["database"],
        "text": "Indexes speed up reads on indexed columns at the cost of slower writes "
        "(index maintenance) and extra storage. B-tree indexes suit range queries; hash "
        "indexes suit equality lookups. Over-indexing is a common performance anti-pattern.",
    },
    {
        "id": "sharding",
        "title": "Database Sharding",
        "dimension_hint": "performance",
        "tags": ["database", "scale"],
        "text": "Sharding partitions data across multiple database instances by a shard key "
        "(e.g. user_id hash) to scale writes beyond a single machine. Introduces complexity: "
        "cross-shard joins and transactions become expensive or impossible, and shard-key "
        "choice is hard to change later.",
    },
    {
        "id": "read-replicas",
        "title": "Read Replicas",
        "dimension_hint": "performance",
        "tags": ["database", "scale"],
        "text": "Read replicas offload read traffic from a primary database via asynchronous "
        "replication. Scales read-heavy workloads cheaply but introduces replication lag — "
        "reads from a replica may be stale, which matters for read-your-own-write use cases.",
    },
    {
        "id": "connection-pooling",
        "title": "Connection Pooling",
        "dimension_hint": "performance",
        "tags": ["database"],
        "text": "Opening a new database connection per request is expensive (TCP handshake, "
        "auth). Connection pools reuse a fixed set of warm connections, dramatically reducing "
        "per-request latency and preventing the database from being overwhelmed by connection "
        "churn under load.",
    },
    {
        "id": "async-processing",
        "title": "Asynchronous Processing / Message Queues",
        "dimension_hint": "performance",
        "tags": ["queue", "latency"],
        "text": "Offloading slow or non-critical work (emails, image processing, analytics) to "
        "a message queue (e.g. SQS, RabbitMQ, Kafka) keeps the request path fast and lets "
        "workers scale independently. Trades immediate consistency for eventual completion "
        "and requires idempotent consumers.",
    },
    {
        "id": "batching",
        "title": "Batching Requests",
        "dimension_hint": "performance",
        "tags": ["throughput"],
        "text": "Batching combines multiple small operations (DB writes, API calls) into one, "
        "amortizing fixed overhead (network round trips, transaction commits) across many "
        "items. Improves throughput at the cost of added latency per individual item and "
        "more complex error handling for partial batch failures.",
    },
    {
        "id": "n-plus-one",
        "title": "N+1 Query Problem",
        "dimension_hint": "performance",
        "tags": ["database", "anti-pattern"],
        "text": "The N+1 problem occurs when fetching a list of N items triggers N additional "
        "queries (e.g. one per related object) instead of a single joined or batched query. "
        "A classic performance anti-pattern in ORMs; fixed via eager loading or batched "
        "fetching.",
    },
    {
        "id": "latency-vs-throughput",
        "title": "Latency vs Throughput",
        "dimension_hint": "performance",
        "tags": ["fundamentals"],
        "text": "Latency is the time for a single operation to complete; throughput is "
        "operations completed per unit time. They are related but distinct: batching and "
        "queuing can improve throughput while increasing per-item latency. Optimize for the "
        "one the product actually needs.",
    },
    {
        "id": "percentile-latency",
        "title": "Percentile Latency (p50/p99)",
        "dimension_hint": "performance",
        "tags": ["metrics"],
        "text": "Average latency hides tail behavior. p50 (median) shows typical experience; "
        "p99 shows the worst experience for 1 in 100 requests, which matters a lot at scale "
        "since a large fraction of users will eventually hit it. Design and alert on tail "
        "percentiles, not just averages.",
    },
    {
        "id": "backpressure",
        "title": "Backpressure",
        "dimension_hint": "performance",
        "tags": ["queue", "resilience"],
        "text": "Backpressure is a mechanism for a slower downstream component to signal an "
        "upstream producer to slow down (bounded queues, rejecting requests, load shedding) "
        "rather than buffering unboundedly and eventually running out of memory or crashing.",
    },
    {
        "id": "hot-partition",
        "title": "Hot Partition / Hot Key",
        "dimension_hint": "performance",
        "tags": ["database", "scale"],
        "text": "A hot partition occurs when a sharding or partitioning scheme routes "
        "disproportionate traffic to one shard (e.g. a viral user ID, sequential IDs, or a "
        "popular cache key), bottlenecking that node while others sit idle. Mitigated by "
        "better key design, salting, or request coalescing.",
    },

    # --- security ---
    {
        "id": "authn-vs-authz",
        "title": "Authentication vs Authorization",
        "dimension_hint": "security",
        "tags": ["auth"],
        "text": "Authentication verifies who a user is (login, tokens, MFA). Authorization "
        "determines what an authenticated user is allowed to do (RBAC, ABAC, ACLs). Conflating "
        "the two is a common source of security bugs — always check both on every protected "
        "action.",
    },
    {
        "id": "rate-limiting",
        "title": "Rate Limiting",
        "dimension_hint": "security",
        "tags": ["abuse-prevention"],
        "text": "Rate limiting caps requests per identity (user, IP, API key) over a time "
        "window to prevent abuse and protect downstream capacity. Common algorithms: token "
        "bucket (allows bursts up to a cap), sliding window log/counter (smoother enforcement). "
        "Apply at the edge (gateway) to protect the whole system.",
    },
    {
        "id": "owasp-injection",
        "title": "Injection Attacks (OWASP)",
        "dimension_hint": "security",
        "tags": ["owasp"],
        "text": "Injection (SQL, NoSQL, command, LDAP) occurs when untrusted input is "
        "concatenated into a query or command interpreter. Prevented by parameterized "
        "queries/prepared statements and never building queries via string concatenation of "
        "user input.",
    },
    {
        "id": "owasp-broken-authn",
        "title": "Broken Authentication (OWASP)",
        "dimension_hint": "security",
        "tags": ["owasp", "auth"],
        "text": "Broken authentication covers weak password policies, missing brute-force "
        "protection, session tokens exposed in URLs, and improper session invalidation on "
        "logout. Mitigations: MFA, secure random session tokens, short-lived tokens with "
        "refresh, and rate-limited login attempts.",
    },
    {
        "id": "owasp-access-control",
        "title": "Broken Access Control (OWASP)",
        "dimension_hint": "security",
        "tags": ["owasp", "authz"],
        "text": "The most common OWASP Top 10 finding: failing to enforce authorization checks "
        "server-side, allowing users to access or modify resources they shouldn't (e.g. IDOR — "
        "insecure direct object reference, changing an ID in a URL to view another user's "
        "data). Every resource access must be authorized server-side, never trust client-side "
        "checks alone.",
    },
    {
        "id": "encryption-transit-rest",
        "title": "Encryption in Transit and at Rest",
        "dimension_hint": "security",
        "tags": ["encryption"],
        "text": "Encryption in transit (TLS) protects data moving over the network from "
        "eavesdropping/tampering. Encryption at rest (disk/DB-level encryption) protects "
        "stored data if physical media or backups are compromised. Both are typically table "
        "stakes, not optional add-ons, for systems handling any sensitive data.",
    },
    {
        "id": "secrets-management",
        "title": "Secrets Management",
        "dimension_hint": "security",
        "tags": ["secrets"],
        "text": "API keys, database credentials, and signing keys must never be hardcoded or "
        "committed to source control. Use a secrets manager or environment variables injected "
        "at deploy time, rotate credentials periodically, and scope each credential to the "
        "minimum required permissions.",
    },
    {
        "id": "least-privilege",
        "title": "Principle of Least Privilege",
        "dimension_hint": "security",
        "tags": ["authz"],
        "text": "Every component, service account, and user should hold only the minimum "
        "permissions needed to do its job. Reduces blast radius when credentials or a service "
        "are compromised. Applies to database roles, cloud IAM policies, and inter-service "
        "auth alike.",
    },
    {
        "id": "input-validation",
        "title": "Input Validation",
        "dimension_hint": "security",
        "tags": ["validation"],
        "text": "All input crossing a trust boundary (user input, third-party API responses, "
        "file uploads) must be validated: type, length, format, and allow-listed values where "
        "possible. Validate on the server even if the client also validates, since client-side "
        "checks can be bypassed.",
    },
    {
        "id": "csrf-xss",
        "title": "CSRF and XSS",
        "dimension_hint": "security",
        "tags": ["owasp", "web"],
        "text": "XSS (Cross-Site Scripting) injects malicious scripts into pages viewed by "
        "other users, mitigated by output encoding and Content-Security-Policy. CSRF "
        "(Cross-Site Request Forgery) tricks a logged-in user's browser into making unwanted "
        "requests, mitigated by CSRF tokens and SameSite cookies.",
    },
    {
        "id": "ddos-mitigation",
        "title": "DDoS Mitigation",
        "dimension_hint": "security",
        "tags": ["availability"],
        "text": "Distributed denial-of-service defenses layer: CDN/edge absorption of "
        "volumetric traffic, rate limiting and WAF rules for application-layer attacks, and "
        "auto-scaling with circuit breakers so a traffic spike degrades gracefully rather than "
        "cascading into a full outage.",
    },
    {
        "id": "audit-logging",
        "title": "Audit Logging",
        "dimension_hint": "security",
        "tags": ["compliance", "observability"],
        "text": "Audit logs record who did what, when, immutably — distinct from debug logs. "
        "Required for compliance (SOC2, HIPAA) and incident forensics. Should be tamper-evident "
        "(write-once or hash-chained) and exclude sensitive payload data unless specifically "
        "required and protected.",
    },
    {
        "id": "supply-chain-security",
        "title": "Supply Chain Security",
        "dimension_hint": "security",
        "tags": ["dependencies"],
        "text": "Third-party dependencies (packages, base container images) are an attack "
        "surface. Mitigations: pinned versions, automated vulnerability scanning (e.g. "
        "Dependabot), minimal base images, and verifying package integrity/provenance before "
        "adding a new dependency.",
    },
    {
        "id": "data-minimization",
        "title": "Data Minimization",
        "dimension_hint": "security",
        "tags": ["privacy"],
        "text": "Collect and retain only the data actually needed for the feature to function. "
        "Reduces breach impact, simplifies compliance (GDPR data minimization principle), and "
        "lowers long-term storage/liability cost. A common design smell is storing PII "
        "speculatively for possible future use.",
    },
    {
        "id": "threat-modeling",
        "title": "Threat Modeling (STRIDE)",
        "dimension_hint": "security",
        "tags": ["process"],
        "text": "STRIDE is a threat-modeling mnemonic: Spoofing, Tampering, Repudiation, "
        "Information disclosure, Denial of service, Elevation of privilege. Walking a design "
        "through each category surfaces security gaps systematically rather than relying on "
        "ad hoc review.",
    },

    # --- feedback / cross-cutting / general ---
    {
        "id": "single-point-of-failure",
        "title": "Single Point of Failure",
        "dimension_hint": "feedback",
        "tags": ["reliability"],
        "text": "A single point of failure (SPOF) is any component whose failure takes down "
        "the whole system — a lone database instance, an unreplicated cache, a hardcoded "
        "dependency on one region. Identifying and eliminating SPOFs (via redundancy, "
        "failover) is a core critique to raise against any proposed architecture.",
    },
    {
        "id": "idempotency",
        "title": "Idempotency",
        "dimension_hint": "feedback",
        "tags": ["reliability", "api"],
        "text": "An idempotent operation produces the same result no matter how many times "
        "it's applied. Critical for safe retries in distributed systems (network timeouts mean "
        "the client can't know if a request succeeded) — implemented via idempotency keys or "
        "naturally idempotent operations (PUT with full state vs POST that always creates).",
    },
    {
        "id": "circuit-breaker",
        "title": "Circuit Breaker Pattern",
        "dimension_hint": "feedback",
        "tags": ["resilience"],
        "text": "A circuit breaker stops calling a failing downstream service after a failure "
        "threshold, failing fast instead of piling up timeouts, then periodically probes to "
        "see if the dependency has recovered. Prevents cascading failure across a system of "
        "services.",
    },
    {
        "id": "graceful-degradation",
        "title": "Graceful Degradation",
        "dimension_hint": "feedback",
        "tags": ["resilience"],
        "text": "A system should degrade gracefully under partial failure — e.g. serving "
        "stale cached data or a reduced feature set — rather than failing completely. A design "
        "that has no fallback path when a non-critical dependency is down is a common "
        "critique target.",
    },
    {
        "id": "two-phase-commit",
        "title": "Two-Phase Commit vs Saga",
        "dimension_hint": "feedback",
        "tags": ["transactions", "microservices"],
        "text": "Two-phase commit (2PC) gives atomic distributed transactions but blocks on a "
        "coordinator and doesn't scale well. The Saga pattern instead breaks a distributed "
        "transaction into a sequence of local transactions with compensating actions on "
        "failure — better availability, more application complexity to get right.",
    },
    {
        "id": "eventual-consistency-ux",
        "title": "Eventual Consistency and UX",
        "dimension_hint": "feedback",
        "tags": ["consistency", "ux"],
        "text": "Choosing eventual consistency for performance/availability has real UX "
        "consequences (a user's own write may not appear immediately). A design that adopts "
        "eventual consistency should explicitly address read-your-own-writes expectations for "
        "the affected user flows, or accept and document the tradeoff.",
    },
    {
        "id": "monolith-vs-microservices",
        "title": "Monolith vs Microservices",
        "dimension_hint": "feedback",
        "tags": ["architecture"],
        "text": "Microservices offer independent scaling/deployment but add network latency, "
        "distributed-transaction complexity, and operational overhead best justified by team "
        "scale and genuinely independent domains. A modular monolith often serves small teams "
        "and early-stage products better, deferring the split until boundaries are proven.",
    },
    {
        "id": "api-versioning",
        "title": "API Versioning Strategies",
        "dimension_hint": "feedback",
        "tags": ["api"],
        "text": "API versioning approaches: URI versioning (/v1/...), header-based versioning, "
        "and additive-only evolution without explicit versions. URI versioning is simplest to "
        "reason about and cache; header-based is cleaner but harder to debug and test "
        "manually.",
    },
    {
        "id": "observability-pillars",
        "title": "Observability: Logs, Metrics, Traces",
        "dimension_hint": "feedback",
        "tags": ["observability"],
        "text": "The three observability pillars: logs (discrete events, good for detail), "
        "metrics (aggregated numeric time series, good for alerting/trends), and traces "
        "(request flow across services, good for diagnosing latency in distributed calls). A "
        "design proposal missing all three lacks a story for diagnosing production issues.",
    },
    {
        "id": "feature-flags",
        "title": "Feature Flags",
        "dimension_hint": "feedback",
        "tags": ["deployment"],
        "text": "Feature flags decouple deployment from release, enabling gradual rollout, "
        "kill switches for bad releases, and A/B testing without a redeploy. A useful mitigation "
        "to suggest when a design carries deployment risk.",
    },
    {
        "id": "polling-vs-webhooks-vs-streaming",
        "title": "Polling vs Webhooks vs Streaming",
        "dimension_hint": "feedback",
        "tags": ["realtime"],
        "text": "Polling is simple but wastes resources and adds latency proportional to poll "
        "interval. Webhooks push events on occurrence, efficient but require the receiver to "
        "expose a reachable endpoint and handle retries/dedup. Persistent streaming (SSE, "
        "WebSockets) gives the lowest latency but adds connection-management complexity at "
        "scale.",
    },
    {
        "id": "consistent-hashing",
        "title": "Consistent Hashing",
        "dimension_hint": "feedback",
        "tags": ["distributed-systems", "scale"],
        "text": "Consistent hashing maps both nodes and keys onto a hash ring so that adding "
        "or removing a node only remaps a small fraction of keys (roughly 1/N), unlike naive "
        "modulo hashing which remaps almost everything. Foundational for scalable sharding and "
        "load balancing.",
    },
    {
        "id": "cqrs",
        "title": "CQRS",
        "dimension_hint": "feedback",
        "tags": ["architecture"],
        "text": "Command Query Responsibility Segregation splits the write model (commands) "
        "from the read model (queries), allowing each to be optimized and scaled "
        "independently — often paired with event sourcing. Adds synchronization complexity "
        "between the two models and is usually overkill outside genuinely read/write-asymmetric "
        "domains.",
    },
    {
        "id": "outbox-pattern",
        "title": "Transactional Outbox Pattern",
        "dimension_hint": "feedback",
        "tags": ["messaging", "consistency"],
        "text": "The outbox pattern solves the dual-write problem (writing to a DB and "
        "publishing an event must both happen or neither) by writing the event to an outbox "
        "table in the same DB transaction, then a separate relay process publishes it to the "
        "message broker — avoiding lost or duplicate events from a naive two-system write.",
    },

    # --- constraints (added) ---
    {
        "id": "geo-distribution-constraint",
        "title": "Geographic Distribution as a Constraint",
        "dimension_hint": "constraints",
        "tags": ["latency", "compliance"],
        "text": "Serving a globally distributed user base constrains design on two fronts: "
        "physics (round-trip latency to a single region degrades UX for distant users, pushing "
        "toward multi-region deployment) and law (data residency rules like GDPR may require "
        "EU user data to stay in EU regions). Multi-region adds replication-consistency "
        "tradeoffs that single-region designs never have to make.",
    },
    {
        "id": "read-write-ratio-constraint",
        "title": "Read/Write Ratio as a Design Driver",
        "dimension_hint": "constraints",
        "tags": ["scale", "fundamentals"],
        "text": "The read-to-write ratio of a workload should drive early architecture choices: "
        "read-heavy systems (e.g. 100:1) justify caching layers and read replicas; write-heavy "
        "systems justify sharding and async write paths. Designing a heavy caching layer for a "
        "write-heavy workload (or vice versa) is a common constraint-mismatch critique.",
    },
    {
        "id": "multi-tenancy-constraint",
        "title": "Multi-Tenancy Isolation Constraint",
        "dimension_hint": "constraints",
        "tags": ["architecture", "isolation"],
        "text": "Multi-tenant systems must choose an isolation model: shared database with a "
        "tenant_id column (cheapest, weakest isolation), schema-per-tenant, or database/cluster "
        "-per-tenant (strongest isolation, highest operational cost). The choice is constrained "
        "by tenant count, noisy-neighbor risk tolerance, and any per-tenant compliance "
        "requirements — not purely a performance decision.",
    },

    # --- performance (added) ---
    {
        "id": "message-delivery-semantics",
        "title": "Message Delivery Semantics",
        "dimension_hint": "performance",
        "tags": ["queue", "consistency"],
        "text": "Message queues offer at-most-once (may lose messages, never duplicates), "
        "at-least-once (may duplicate, never loses — the common default, requires idempotent "
        "consumers), or exactly-once (strongest, usually achieved via dedup + at-least-once, "
        "adds cost/complexity). A design claiming 'exactly-once' without describing how is a "
        "red flag worth challenging.",
    },
    {
        "id": "storage-engine-tradeoffs",
        "title": "Storage Engine Tradeoffs (LSM vs B-Tree)",
        "dimension_hint": "performance",
        "tags": ["database", "fundamentals"],
        "text": "B-tree storage engines (traditional RDBMS) give fast, predictable reads at the "
        "cost of slower random writes (in-place updates). LSM-tree engines (Cassandra, "
        "RocksDB) buffer writes in memory and flush sequentially, giving very high write "
        "throughput at the cost of read amplification and background compaction overhead. "
        "Workload shape, not familiarity, should drive the choice.",
    },
    {
        "id": "compression-tradeoffs",
        "title": "Compression Tradeoffs",
        "dimension_hint": "performance",
        "tags": ["storage", "network"],
        "text": "Compressing data in transit and at rest reduces network/storage cost and can "
        "improve effective throughput on bandwidth-constrained links, but costs CPU on both "
        "ends and adds latency for small payloads where compression overhead exceeds the "
        "savings. Favor compression for large payloads and cross-region transfer, skip it for "
        "tiny hot-path responses.",
    },
    {
        "id": "warm-vs-cold-storage",
        "title": "Hot, Warm, and Cold Storage Tiers",
        "dimension_hint": "performance",
        "tags": ["storage", "cost"],
        "text": "Data access patterns justify storage tiering: hot tier (SSD/in-memory, "
        "expensive, low latency) for recent/frequently-accessed data, warm tier for occasional "
        "access, and cold/archival tier (object storage, cheap, high retrieval latency) for "
        "rarely-accessed or compliance-retained data. Storing everything in the hot tier is a "
        "common cost-performance anti-pattern.",
    },
    {
        "id": "geo-replication-latency",
        "title": "Geo-Replication and Write Latency",
        "dimension_hint": "performance",
        "tags": ["distributed-systems", "latency"],
        "text": "Synchronous multi-region replication (waiting for all regions to acknowledge a "
        "write) guarantees consistency but adds the round-trip latency of the slowest region to "
        "every write. Asynchronous replication keeps writes fast but risks data loss on regional "
        "failover. Systems needing both low write latency and multi-region durability typically "
        "pick a quorum-based approach (e.g. write to a majority of regions).",
    },

    # --- security (added) ---
    {
        "id": "owasp-ssrf",
        "title": "Server-Side Request Forgery (OWASP)",
        "dimension_hint": "security",
        "tags": ["owasp"],
        "text": "SSRF occurs when an attacker gets the server to make requests to unintended "
        "internal destinations (cloud metadata endpoints, internal admin services) by supplying "
        "a URL that the server fetches on the attacker's behalf. Mitigated by allow-listing "
        "outbound destinations, blocking requests to internal IP ranges, and not trusting "
        "user-supplied URLs for server-side fetches.",
    },
    {
        "id": "token-based-auth",
        "title": "Token-Based Auth: Session vs JWT",
        "dimension_hint": "security",
        "tags": ["auth"],
        "text": "Server-side sessions (opaque token + server-side store) support instant "
        "revocation but require a shared session store across instances. JWTs are self-contained "
        "and scale statelessly but can't be revoked before expiry without an extra denylist "
        "check, which erodes the statelessness benefit. Short expiry + refresh tokens is the "
        "common middle ground.",
    },
    {
        "id": "webhook-signature-verification",
        "title": "Webhook Signature Verification",
        "dimension_hint": "security",
        "tags": ["auth", "integration"],
        "text": "An endpoint that accepts inbound webhooks from a third party must verify a "
        "cryptographic signature (typically HMAC over the payload with a shared secret) on "
        "every request, not just trust the source IP or a static bearer token — otherwise "
        "anyone who discovers the URL can forge events.",
    },
    {
        "id": "pii-tokenization",
        "title": "Tokenization of Sensitive Data",
        "dimension_hint": "security",
        "tags": ["privacy", "compliance"],
        "text": "Tokenization replaces sensitive values (card numbers, SSNs) with a non-sensitive "
        "reference token, storing the real value only in a tightly-scoped vault. Downstream "
        "systems operate on tokens and never touch raw sensitive data, shrinking the compliance "
        "and breach-impact surface compared to encrypting the value everywhere it flows.",
    },
    {
        "id": "dependency-confusion",
        "title": "Dependency / Namespace Confusion",
        "dimension_hint": "security",
        "tags": ["supply-chain"],
        "text": "Dependency confusion attacks publish a malicious public package with the same "
        "name as an internal private package; if the package manager resolves the public "
        "registry first, the malicious version gets pulled into a build. Mitigated by scoped "
        "package namespaces, explicit registry pinning, and internal-registry-first resolution.",
    },

    # --- feedback / cross-cutting (added) ---
    {
        "id": "deployment-strategies",
        "title": "Deployment Strategies: Blue-Green vs Canary",
        "dimension_hint": "feedback",
        "tags": ["deployment", "resilience"],
        "text": "Blue-green deployment runs two full environments and switches traffic "
        "atomically, giving instant rollback but doubling infra cost during the switch. Canary "
        "deployment shifts a small traffic percentage to the new version first, catching "
        "regressions with limited blast radius before a full rollout, at the cost of running "
        "mixed versions simultaneously and needing good metrics to judge canary health.",
    },
    {
        "id": "bulkhead-pattern",
        "title": "Bulkhead Pattern",
        "dimension_hint": "feedback",
        "tags": ["resilience"],
        "text": "The bulkhead pattern isolates resources (thread pools, connection pools) per "
        "downstream dependency so that one failing or slow dependency can't exhaust resources "
        "shared by unrelated calls — named after ship compartments that contain flooding to one "
        "section rather than sinking the whole vessel.",
    },
    {
        "id": "cost-observability",
        "title": "Cost as an Observability Signal",
        "dimension_hint": "feedback",
        "tags": ["cost", "observability"],
        "text": "Cloud cost should be monitored like latency or error rate, with per-service or "
        "per-feature attribution (tagging) and alerts on anomalous spend. A design proposal that "
        "adds significant infra without a cost estimate or attribution plan is missing a "
        "feedback loop that matters as much as performance metrics for most teams.",
    },
    {
        "id": "chaos-engineering",
        "title": "Chaos Engineering",
        "dimension_hint": "feedback",
        "tags": ["resilience", "process"],
        "text": "Chaos engineering deliberately injects failures (killing instances, adding "
        "network latency, exhausting resources) in a controlled way to verify a system's "
        "resilience claims hold in practice, rather than trusting them on paper. Especially "
        "valuable for validating failover and circuit-breaker behavior that rarely triggers "
        "naturally.",
    },
    {
        "id": "dual-write-problem",
        "title": "The Dual-Write Problem",
        "dimension_hint": "feedback",
        "tags": ["consistency", "messaging"],
        "text": "Writing to two systems (e.g. a database and a message queue, or two "
        "databases) in sequence without a shared transaction risks partial failure — the first "
        "write succeeds, the second fails, leaving the systems inconsistent. Solved via the "
        "outbox pattern, change-data-capture, or a saga, not by 'just retry the second write' "
        "which doesn't handle process crashes between the two calls.",
    },
    {
        "id": "define-done-metrics",
        "title": "Defining Success Metrics Up Front",
        "dimension_hint": "feedback",
        "tags": ["process"],
        "text": "A design proposal should state the metric that will determine whether it "
        "worked (e.g. p99 latency under 200ms, error rate under 0.1%) before implementation, "
        "not after. Without a stated target, 'is this design good enough' has no answer and "
        "review debate has nothing concrete to converge on.",
    },
]
