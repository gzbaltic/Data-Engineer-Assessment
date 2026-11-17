with order_items as (

    select order_item_id, order_id, product_id, quantity
    from {{ ref('stg_order_items') }}

),

orders as (

    select order_id, customer_id, order_date, status
    from {{ ref('stg_orders') }}

)

select
    order_items.order_item_id,
    order_items.order_id,
    orders.customer_id,
    orders.order_date,
    orders.status,
    order_items.product_id,
    order_items.quantity
from order_items
inner join orders on order_items.order_id = orders.order_id