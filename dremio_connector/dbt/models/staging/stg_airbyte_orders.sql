{{
  config(
    materialized='view',
    tags=['staging', 'airbyte', 'orders']
  )
}}

WITH source AS (
    SELECT * FROM {{ source('airbyte_staging', 'data_orders') }}
),

renamed AS (
    SELECT
        id AS order_id,
        customer_id,
        order_date,
        total_amount,
        status,
        
        -- Airbyte metadata
        _airbyte_ab_id AS airbyte_record_id,
        _airbyte_emitted_at AS airbyte_synced_at,
        
        -- Data quality flags
        CASE 
            WHEN total_amount < 0 THEN 'invalid_amount'
            WHEN status NOT IN ('pending', 'completed', 'cancelled') THEN 'invalid_status'
            ELSE 'valid'
        END AS data_quality_flag,
        
        -- Sync metadata
        'airbyte' AS source_system,
        CURRENT_TIMESTAMP AS dbt_loaded_at

    FROM source
)

SELECT * FROM renamed
