with raw_customers as (

    select
        customer_id,
        first_name,
        last_name,
        nullif(trim(email), '') as email,
        cast(signup_date as date) as signup_date,
        country
    from {{ ref('raw_customers') }}

)

select distinct
    customer_id,
    first_name,
    last_name,
    email,
    signup_date,
    country
from raw_customers
