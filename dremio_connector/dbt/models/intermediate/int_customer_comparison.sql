{{
  config(
    materialized='table',
    tags=['intermediate', 'comparison', 'airbyte']
  )
}}

WITH postgres_customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

airbyte_customers AS (
    SELECT * FROM {{ ref('stg_airbyte_customers') }}
),

comparison AS (
    SELECT
        COALESCE(p.customer_id, a.customer_id) AS customer_id,
        
        -- Source presence flags
        CASE WHEN p.customer_id IS NOT NULL THEN TRUE ELSE FALSE END AS in_postgres,
        CASE WHEN a.customer_id IS NOT NULL THEN TRUE ELSE FALSE END AS in_airbyte,
        
        -- Data comparison
        CASE 
            WHEN p.customer_id IS NULL THEN 'only_in_airbyte'
            WHEN a.customer_id IS NULL THEN 'only_in_postgres'
            WHEN p.email != a.email THEN 'data_mismatch'
            ELSE 'match'
        END AS sync_status,
        
        -- PostgreSQL data
        p.first_name AS postgres_first_name,
        p.last_name AS postgres_last_name,
        p.email AS postgres_email,
        
        -- Airbyte data
        a.first_name AS airbyte_first_name,
        a.last_name AS airbyte_last_name,
        a.email AS airbyte_email,
        a.airbyte_synced_at,
        
        CURRENT_TIMESTAMP AS comparison_timestamp
    
    FROM postgres_customers p
    FULL OUTER JOIN airbyte_customers a
        ON p.customer_id = a.customer_id
)

SELECT * FROM comparison
