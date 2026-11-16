with order_items as (

    select order_item_id, order_id, product_id, quantity
    from {{ ref('stg_order_items') }}

),

orders as (

    select order_id, customer_id, order_date, status
    from {{ ref('stg_orders') }}

),

products as (

    select product_id, product_name, category, unit_price
    from {{ ref('stg_products') }}

)

select
    order_items.order_item_id,
    order_items.order_id,
    orders.customer_id,
    orders.order_date,
    orders.status,
    order_items.product_id,
    products.product_name,
    products.category,
    order_items.quantity,
    products.unit_price,
    order_items.quantity * products.unit_price as line_total
from order_items
-- Inner joins intentionally drop the orphaned order_items (no matching order)
-- and any items for the filtered-out negative-price product.
inner join orders on order_items.order_id = orders.order_id
inner join products on order_items.product_id = products.product_id
