{{
  config(
    materialized='view',
    tags=['staging', 'airbyte', 'customers']
  )
}}

WITH source AS (
    SELECT * FROM {{ source('airbyte_staging', 'data_customers') }}
),

renamed AS (
    SELECT
        id AS customer_id,
        first_name,
        last_name,
        email,
        created_at,
        
        -- Airbyte metadata
        _airbyte_ab_id AS airbyte_record_id,
        _airbyte_emitted_at AS airbyte_synced_at,
        
        -- Data quality flags
        CASE 
            WHEN first_name IS NULL OR last_name IS NULL THEN 'incomplete'
            WHEN email IS NULL THEN 'missing_email'
            ELSE 'complete'
        END AS data_quality_flag,
        
        -- Sync metadata
        'airbyte' AS source_system,
        CURRENT_TIMESTAMP AS dbt_loaded_at

    FROM source
)

SELECT * FROM renamed
