with raw_products as (

    select
        product_id,
        product_name,
        category,
        cast(unit_price as decimal(10, 2)) as unit_price
    from {{ ref('raw_products') }}

)

select
    product_id,
    product_name,
    category,
    unit_price
from raw_products
-- A negative unit_price is a known data-entry error upstream, not a valid price.
where unit_price >= 0
