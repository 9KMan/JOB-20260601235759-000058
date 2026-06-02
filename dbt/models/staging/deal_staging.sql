-- Deal staging model
{{ config(materialized="view") }}

SELECT
    id,
    name,
    description,
    deal_value,
    deal_type,
    status,
    created_at,
    updated_at
FROM {{ source("deal_analysis", "deals") }}