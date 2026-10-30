-- is_posted must agree with the NBI rule: posted means posting code 0-4.
select bridge_inspection_key, posting_code, is_posted
from {{ ref('fct_bridge_inspection') }}
where is_posted != (posting_code < 5)
