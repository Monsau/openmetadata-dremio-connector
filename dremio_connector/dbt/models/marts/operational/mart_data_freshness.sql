{{
  config(
    materialized='table',
    tags=['mart', 'operational', 'freshness', 'airbyte']
  )
}}

WITH airbyte_tables AS (
    SELECT * FROM {{ ref('int_airbyte_metadata') }}
),

freshness_report AS (
    SELECT
        table_name,
        record_count,
        latest_sync,
        
        -- Freshness status
        CASE
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '1' HOUR THEN 'very_fresh'
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '6' HOUR THEN 'fresh'
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '12' HOUR THEN 'acceptable'
            WHEN latest_sync > CURRENT_TIMESTAMP - INTERVAL '24' HOUR THEN 'stale'
            ELSE 'very_stale'
        END AS freshness_status,
        
        -- Expected next sync (assuming 6-hour schedule)
        latest_sync + INTERVAL '6' HOUR AS expected_next_sync,
        
        CURRENT_TIMESTAMP AS report_generated_at
    
    FROM airbyte_tables
)

SELECT * FROM freshness_report
