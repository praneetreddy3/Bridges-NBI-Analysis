-- Quality report: raw rows kept out of the fact table, and why.
select
    reject_reason,
    inspection_year,
    count(*) as rejected_rows
from {{ ref('stg_bridges') }}
where reject_reason is not null
group by all
