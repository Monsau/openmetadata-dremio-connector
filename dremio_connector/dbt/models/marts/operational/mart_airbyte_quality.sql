{{
  config(
    materialized='table',
    tags=['mart', 'operational', 'quality', 'airbyte']
  )
}}

WITH metadata AS (
    SELECT * FROM {{ ref('int_airbyte_metadata') }}
),

comparison AS (
    SELECT
        COUNT(*) AS total_records,
        COUNT(CASE WHEN sync_status = 'match' THEN 1 END) AS matched_records,
        COUNT(CASE WHEN sync_status = 'data_mismatch' THEN 1 END) AS mismatched_records,
        COUNT(CASE WHEN sync_status = 'only_in_postgres' THEN 1 END) AS missing_in_airbyte,
        COUNT(CASE WHEN sync_status = 'only_in_airbyte' THEN 1 END) AS extra_in_airbyte
    FROM {{ ref('int_customer_comparison') }}
),

quality_report AS (
    SELECT
        'Airbyte Data Quality Report' AS report_name,
        
        -- Metadata metrics
        (SELECT SUM(record_count) FROM metadata) AS total_airbyte_records,
        (SELECT AVG(data_quality_percentage) FROM metadata) AS avg_quality_percentage,
        (SELECT MAX(latest_sync) FROM metadata) AS last_sync_timestamp,
        
        -- Comparison metrics
        c.total_records AS comparison_total,
        c.matched_records,
        c.mismatched_records,
        c.missing_in_airbyte,
        c.extra_in_airbyte,
        
        -- Calculated metrics
        ROUND(c.matched_records * 100.0 / NULLIF(c.total_records, 0), 2) AS match_percentage,
        
        -- Quality score (0-100)
        ROUND(
            (
                (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) * 0.6 +
                ((SELECT AVG(data_quality_percentage) FROM metadata) * 0.4)
            ),
            2
        ) AS overall_quality_score,
        
        -- Status
        CASE
            WHEN (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) > 95 THEN 'excellent'
            WHEN (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) > 90 THEN 'good'
            WHEN (c.matched_records * 100.0 / NULLIF(c.total_records, 0)) > 80 THEN 'acceptable'
            ELSE 'needs_attention'
        END AS quality_status,
        
        CURRENT_TIMESTAMP AS report_generated_at
    
    FROM comparison c
)

SELECT * FROM quality_report
