# schema-partial-indexes

**Priority:** 4 — HIGH
**Category:** Schema Design

## Why It Matters

Partial indexes only index rows matching a WHERE condition, making them smaller, faster to update, and more efficient for filtered queries. A partial index can be 10-100x smaller than a full index while serving the same queries.

## Incorrect

```sql
-- Full index on orders.status, but 95% of rows are 'completed'
-- and queries only filter for 'pending' or 'processing'
CREATE INDEX idx_orders_status ON orders (status);

SELECT * FROM orders WHERE status = 'pending';
```

The full index includes all 1M rows, but only 50k are ever queried (pending/processing).

## Correct

```sql
-- Partial index: only index the rows we actually query
CREATE INDEX idx_orders_active_status
  ON orders (status)
  WHERE status IN ('pending', 'processing');

SELECT * FROM orders WHERE status = 'pending';
```

**EXPLAIN output:**
```
Index Scan using idx_orders_active_status on orders  (cost=0.29..8.31 rows=25000 width=80)
  Index Cond: (status = 'pending'::text)
Planning Time: 0.1 ms
Execution Time: 12.3 ms
```

## Common Use Cases

### Soft deletes
```sql
-- Only index non-deleted rows
CREATE INDEX idx_items_active ON items (created_at)
  WHERE deleted_at IS NULL;
```

### Boolean flags
```sql
-- Only index the rare case
CREATE INDEX idx_users_unverified ON users (created_at)
  WHERE is_verified = false;
```

### Status workflows
```sql
-- Only index actionable statuses
CREATE INDEX idx_jobs_pending ON jobs (priority, created_at)
  WHERE status = 'pending';
```

## Rules

1. Use partial indexes when queries consistently filter on a fixed condition
2. Use partial indexes when the filtered subset is <20% of the table
3. The WHERE clause in the query must match (or be a subset of) the index WHERE clause
4. Partial indexes reduce index size, write amplification, and vacuum overhead
5. Combine with composite indexes for maximum effect

## Supabase Notes

- Partial indexes work with RLS — index the columns your RLS policies filter on
- Combine with `pg_stat_user_indexes` to verify the partial index is being used
- Dashboard > Database > Indexes shows index sizes — compare full vs. partial
