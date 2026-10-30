-- Reconciliation: no row may be silently lost between staging and the marts.
-- Returns a row (= test fails) if fact rows + quarantined rows != staging rows.
with counts as (
    select
        (select count(*) from {{ ref('stg_bridges') }})                         as staging_rows,
        (select count(*) from {{ ref('fct_bridge_inspection') }})               as fact_rows,
        (select coalesce(sum(rejected_rows), 0) from {{ ref('rejected_bridge_records') }}) as rejected_rows
)
select * from counts
where fact_rows + rejected_rows != staging_rows
