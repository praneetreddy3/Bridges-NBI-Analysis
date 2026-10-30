-- One row per main-span material (NBI Item 43A), with a coarser family for analysis.
with materials as (
    select distinct main_span_material
    from {{ ref('stg_bridges') }}
    where main_span_material is not null
)

select
    md5(main_span_material) as material_key,
    main_span_material,
    case
        when main_span_material like 'Prestressed%' then 'Prestressed concrete'
        when main_span_material like 'Concrete%'    then 'Concrete'
        when main_span_material like 'Steel%'       then 'Steel'
        when main_span_material like 'Wood%'        then 'Timber'
        else 'Other'
    end as material_family
from materials
