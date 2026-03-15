# query-missing-indexes

**Priority:** 1 — CRITICAL
**Category:** Query Performance

## Why It Matters

Missing indexes force Postgres to perform sequential scans on large tables, turning millisecond queries into multi-second operations. This is the single most common performance issue.

## Incorrect

```sql
-- No index on users.email, table has 1M+ rows
SELECT * FROM users WHERE email = 'user@example.com';
```

**EXPLAIN output:**
```
Seq Scan on users  (cost=0.00..25432.00 rows=1 width=120)
  Filter: (email = 'user@example.com'::text)
  Rows Removed by Filter: 999999
Planning Time: 0.1 ms
Execution Time: 312.4 ms
```

## Correct

```sql
-- Create index on the filtered column
CREATE INDEX idx_users_email ON users (email);

-- Same query now uses the index
SELECT * FROM users WHERE email = 'user@example.com';
```

**EXPLAIN output:**
```
Index Scan using idx_users_email on users  (cost=0.42..8.44 rows=1 width=120)
  Index Cond: (email = 'user@example.com'::text)
Planning Time: 0.1 ms
Execution Time: 0.05 ms
```

## How to Detect Missing Indexes

```sql
-- Find sequential scans on large tables
SELECT schemaname, relname, seq_scan, seq_tup_read,
       idx_scan, idx_tup_fetch,
       seq_tup_read / GREATEST(seq_scan, 1) AS avg_tuples_per_scan
FROM pg_stat_user_tables
WHERE seq_scan > 100
  AND seq_tup_read > 10000
ORDER BY seq_tup_read DESC
LIMIT 20;
```

## Rules

1. Every column in a WHERE clause on a table with >10k rows should have an index
2. Every foreign key column should be indexed
3. Columns used in JOIN conditions should be indexed
4. Use composite indexes for multi-column WHERE clauses (most selective column first)
5. Monitor `pg_stat_user_tables` for high `seq_scan` counts

## Supabase Notes

- Supabase Dashboard > Database > Indexes shows existing indexes
- The Query Performance advisor flags missing indexes automatically
- Use `pg_stat_statements` extension (enabled by default) to find slow queries
