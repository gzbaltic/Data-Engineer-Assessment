select
    order_item_id,
    order_id,
    product_id,
    quantity
from {{ ref('raw_order_items') }}
-- Zero/negative quantities are known bad records from an upstream glitch, not real line items.
where quantity > 0
