-- One row per state / territory (FIPS code), from the reference seed.
select
    state_code as state_key,
    state_code,
    state_abbr,
    state_name
from {{ ref('state_codes') }}
