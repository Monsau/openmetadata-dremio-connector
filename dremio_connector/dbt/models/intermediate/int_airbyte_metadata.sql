{{
  config(
    materialized='table',
    tags=['intermediate', 'metadata', 'airbyte']
  )
}}

WITH airbyte_customers AS (
    SELECT
        'customers' AS table_name,
        COUNT(*) AS record_count,
        MIN(airbyte_synced_at) AS earliest_sync,
        MAX(airbyte_synced_at) AS latest_sync,
        COUNT(CASE WHEN data_quality_flag != 'complete' THEN 1 END) AS quality_issues_count
    FROM {{ ref('stg_airbyte_customers') }}
),

airbyte_orders AS (
    SELECT
        'orders' AS table_name,
        COUNT(*) AS record_count,
        MIN(airbyte_synced_at) AS earliest_sync,
        MAX(airbyte_synced_at) AS latest_sync,
        COUNT(CASE WHEN data_quality_flag != 'valid' THEN 1 END) AS quality_issues_count
    FROM {{ ref('stg_airbyte_orders') }}
),

combined AS (
    SELECT * FROM airbyte_customers
    UNION ALL
    SELECT * FROM airbyte_orders
)

SELECT
    table_name,
    record_count,
    earliest_sync,
    latest_sync,
    quality_issues_count,
    ROUND(
        (record_count - quality_issues_count) * 100.0 / NULLIF(record_count, 0),
        2
    ) AS data_quality_percentage,
    CURRENT_TIMESTAMP AS calculated_at
FROM combined
