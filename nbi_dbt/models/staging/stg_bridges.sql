-- Staging: rename, cast and decode the raw NBI columns. One row per raw row.
-- Rows that can't be trusted are kept but flagged with a reject_reason, so the
-- marts can drop them and the quality report can count them.

with source as (
    select * from {{ source('raw', 'nbi_bridges') }}
),

renamed as (
    select
        cast("Year" as integer)                                          as inspection_year,
        cast("1 - State Code" as integer)                                as state_code,
        trim("8 - Structure Number")                                     as structure_number,
        -- 21 records have no owner; NBI already has an "Other or Unknown" owner
        -- category, so use it instead of dropping otherwise-valid bridges.
        coalesce(nullif(trim("22 - Owner Agency"), ''), 'Other or Unknown') as owner_agency,
        try_cast("27 - Year Built" as integer)                           as year_built,
        trim("43A - Main Span Material")                                 as main_span_material,
        trim("43B - Main Span Design")                                   as main_span_design,
        try_cast("48 - Length of Maximum Span (ft.)" as double)          as max_span_ft,
        try_cast("29 - Average Daily Traffic" as integer)                as avg_daily_traffic,
        try_cast("30 - Year of Average Daily Traffic" as integer)        as adt_year,
        try_cast("109 - Average Daily Truck Traffic (Percent ADT)" as double) as truck_pct,
        nullif(trim("31 - Design Load Descriptor"), '')                  as design_load_code,
        try_cast(trim("70 - Bridge Posting Code") as integer)            as posting_code,
        _source_file
    from source
),

decoded as (
    select
        r.*,
        r.inspection_year - r.year_built                                 as bridge_age,
        -- NBI Item 70: code 5 = carries legal loads; 0-4 = load posted (restricted)
        r.posting_code < 5                                               as is_posted,
        p.posting_description,
        d.design_load_description,
        regexp_matches(lower(r.main_span_design), 'bascule|swing|lift|movable|draw')
                                                                         as is_movable,
        count(*) over (partition by r.inspection_year, r.state_code, r.structure_number)
                                                                         as rows_with_same_key
    from renamed r
    left join {{ ref('posting_codes') }} p      on r.posting_code = p.posting_code
    left join {{ ref('design_load_codes') }} d  on r.design_load_code = d.design_load_code
)

select
    *,
    case
        when posting_code is null    then 'missing_posting_code'
        -- Two different physical bridges reported under one ID in the same year:
        -- we can't tell which record is which, so neither goes into the fact table.
        when rows_with_same_key > 1  then 'duplicate_bridge_key'
        when year_built is null      then 'missing_year_built'
    end as reject_reason
from decoded
