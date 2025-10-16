-- Test: Airbyte metadata columns must be present and not null

WITH airbyte_customers AS (
    SELECT
        airbyte_record_id,
        airbyte_synced_at
    FROM {{ ref('stg_airbyte_customers') }}
    WHERE airbyte_record_id IS NULL
       OR airbyte_synced_at IS NULL
),

airbyte_orders AS (
    SELECT
        airbyte_record_id,
        airbyte_synced_at
    FROM {{ ref('stg_airbyte_orders') }}
    WHERE airbyte_record_id IS NULL
       OR airbyte_synced_at IS NULL
)

SELECT * FROM airbyte_customers
UNION ALL
SELECT * FROM airbyte_orders
