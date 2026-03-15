# Postgres Best Practices — Section Index

## Priority 1: Query Performance (CRITICAL)
- [query-missing-indexes.md](query-missing-indexes.md) — Detect and add missing indexes
- [query-select-star.md](query-select-star.md) — Avoid SELECT * in production queries
- [query-n-plus-one.md](query-n-plus-one.md) — Eliminate N+1 query patterns

## Priority 2: Connection Management (CRITICAL)
- [conn-pooling.md](conn-pooling.md) — Use connection pooling (PgBouncer/Supavisor)
- [conn-idle-timeout.md](conn-idle-timeout.md) — Set appropriate idle timeouts

## Priority 3: Security & RLS (CRITICAL)
- [security-rls-performance.md](security-rls-performance.md) — RLS policies that don't kill performance
- [security-rls-indexes.md](security-rls-indexes.md) — Index columns used in RLS policies

## Priority 4: Schema Design (HIGH)
- [schema-partial-indexes.md](schema-partial-indexes.md) — Use partial indexes for filtered queries
- [schema-data-types.md](schema-data-types.md) — Choose correct data types
- [schema-normalization.md](schema-normalization.md) — Balance normalization vs. denormalization

## Priority 5: Concurrency & Locking (MEDIUM-HIGH)
- [lock-long-transactions.md](lock-long-transactions.md) — Avoid long-running transactions
- [lock-advisory.md](lock-advisory.md) — Use advisory locks for application-level coordination

## Priority 6: Data Access Patterns (MEDIUM)
- [data-pagination.md](data-pagination.md) — Use cursor-based pagination over OFFSET
- [data-batch-operations.md](data-batch-operations.md) — Batch inserts and updates

## Priority 7: Monitoring & Diagnostics (LOW-MEDIUM)
- [monitor-slow-queries.md](monitor-slow-queries.md) — Enable and review pg_stat_statements
- [monitor-index-usage.md](monitor-index-usage.md) — Track index usage and bloat

## Priority 8: Advanced Features (LOW)
- [advanced-materialized-views.md](advanced-materialized-views.md) — Materialized views for expensive aggregations
- [advanced-partitioning.md](advanced-partitioning.md) — Table partitioning for large tables
