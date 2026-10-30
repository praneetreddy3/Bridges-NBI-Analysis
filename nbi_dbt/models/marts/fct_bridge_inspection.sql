-- Fact table. Grain: one bridge (state + structure number) per inspection year.
-- Measures are the inspected numbers; descriptive attributes live in the dimensions.

with bridges as (
    select * from {{ ref('stg_bridges') }}
    where reject_reason is null
)

select
    md5(concat_ws('|', b.inspection_year, b.state_code, b.structure_number))
                                as bridge_inspection_key,
    b.inspection_year,
    b.structure_number,
    b.state_code                as state_key,
    m.material_key,
    o.owner_key,
    b.main_span_design,
    b.design_load_code,
    b.is_movable,
    b.year_built,
    b.bridge_age,
    b.max_span_ft,
    b.avg_daily_traffic,
    b.adt_year,
    b.truck_pct,
    b.posting_code,
    b.is_posted
from bridges b
left join {{ ref('dim_material') }} m on b.main_span_material = m.main_span_material
left join {{ ref('dim_owner') }}    o on b.owner_agency      = o.owner_agency
