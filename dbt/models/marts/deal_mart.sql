-- Deal analysis mart model
{{ config(materialized="table") }}

WITH deal_analysis AS (
    SELECT
        d.id,
        d.name,
        d.deal_value,
        d.deal_type,
        d.status,
        da.analysis_type,
        da.score,
        da.summary,
        da.processed_at
    FROM {{ ref("deal_staging") }} d
    LEFT JOIN deal_analyses da ON d.id = da.deal_id
)
SELECT
    id,
    name,
    deal_value,
    deal_type,
    status,
    analysis_type,
    score,
    summary,
    processed_at
FROM deal_analysis