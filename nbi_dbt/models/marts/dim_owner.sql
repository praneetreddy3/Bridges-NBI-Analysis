-- One row per owning agency (NBI Item 22), grouped into a government level.
with owners as (
    select distinct owner_agency
    from {{ ref('stg_bridges') }}
    where owner_agency is not null
)

select
    md5(owner_agency) as owner_key,
    owner_agency,
    case
        when owner_agency in ('State Highway Agency', 'State Toll Authority',
                              'Other State Agencies',
                              'State Park, Forest, or Reservation Agency') then 'State'
        when owner_agency in ('County Highway Agency', 'City or Municipal Highway Agency',
                              'Town or Township Highway Agency', 'Local Toll Authority',
                              'Other Local Agencies',
                              'Local Park, Forest, or Reservation Agency') then 'Local'
        when owner_agency in ('Private (Not railroad)', 'Railroad')       then 'Private'
        when owner_agency in ('Indian Tribal Government')                 then 'Tribal'
        when owner_agency in ('Other or Unknown', 'Other Public Entity')  then 'Other'
        else 'Federal'
    end as owner_level
from owners
