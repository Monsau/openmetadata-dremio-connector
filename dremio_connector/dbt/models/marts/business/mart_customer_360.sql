{{
  config(
    materialized='table',
    tags=['mart', 'business', 'customer-360']
  )
}}

WITH postgres_customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

airbyte_customers AS (
    SELECT * FROM {{ ref('stg_airbyte_customers') }}
),

customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        SUM(total_amount) AS total_spent,
        MAX(order_date) AS last_order_date
    FROM {{ ref('stg_orders') }}
    GROUP BY customer_id
),

unified AS (
    SELECT
        COALESCE(p.customer_id, a.customer_id) AS customer_id,
        
        -- Use PostgreSQL as primary, Airbyte as fallback
        COALESCE(p.first_name, a.first_name) AS first_name,
        COALESCE(p.last_name, a.last_name) AS last_name,
        COALESCE(p.email, a.email) AS email,
        
        -- Data source tracking
        CASE 
            WHEN p.customer_id IS NOT NULL AND a.customer_id IS NOT NULL THEN 'both'
            WHEN p.customer_id IS NOT NULL THEN 'postgres_only'
            ELSE 'airbyte_only'
        END AS data_source,
        
        -- Airbyte sync info
        a.airbyte_synced_at,
        
        -- Order aggregations
        COALESCE(o.total_orders, 0) AS total_orders,
        COALESCE(o.total_spent, 0) AS total_spent,
        o.last_order_date,
        
        -- Customer segments
        CASE
            WHEN COALESCE(o.total_orders, 0) = 0 THEN 'no_orders'
            WHEN o.total_orders = 1 THEN 'one_time'
            WHEN o.total_orders BETWEEN 2 AND 5 THEN 'occasional'
            WHEN o.total_orders > 5 THEN 'frequent'
        END AS customer_segment,
        
        CASE
            WHEN COALESCE(o.total_spent, 0) = 0 THEN 'no_spend'
            WHEN o.total_spent < 100 THEN 'low_value'
            WHEN o.total_spent BETWEEN 100 AND 500 THEN 'medium_value'
            WHEN o.total_spent > 500 THEN 'high_value'
        END AS value_segment,
        
        CURRENT_TIMESTAMP AS loaded_at
    
    FROM postgres_customers p
    FULL OUTER JOIN airbyte_customers a
        ON p.customer_id = a.customer_id
    LEFT JOIN customer_orders o
        ON COALESCE(p.customer_id, a.customer_id) = o.customer_id
)

SELECT * FROM unified
