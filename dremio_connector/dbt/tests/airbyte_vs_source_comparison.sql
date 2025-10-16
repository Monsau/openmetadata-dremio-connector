-- Test: Ensure Airbyte has synced at least 90% of source records

WITH comparison AS (
    SELECT
        COUNT(CASE WHEN sync_status IN ('match', 'data_mismatch') THEN 1 END) AS synced_records,
        COUNT(CASE WHEN sync_status = 'only_in_postgres' THEN 1 END) AS missing_records,
        COUNT(*) AS total_records
    FROM {{ ref('int_customer_comparison') }}
),

sync_percentage AS (
    SELECT
        synced_records,
        missing_records,
        total_records,
        ROUND(synced_records * 100.0 / NULLIF(total_records, 0), 2) AS sync_percentage
    FROM comparison
)

SELECT *
FROM sync_percentage
WHERE sync_percentage < 90
