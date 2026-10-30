{{ config(severity = 'warn') }}
-- Warn (don't fail) on ages outside -1..350 years: usually a typo in year built.
-- Age -1 is allowed because some records list a year built one year after the
-- inspection year (the bridge was still being finished).
select bridge_inspection_key, inspection_year, year_built, bridge_age
from {{ ref('fct_bridge_inspection') }}
where bridge_age < -1 or bridge_age > 350
