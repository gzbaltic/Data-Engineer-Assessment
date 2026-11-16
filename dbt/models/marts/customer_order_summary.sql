with fct_order_items as (

    select order_id, customer_id, order_date, status, line_total
    from {{ ref('fct_order_items') }}

),

per_order as (

    select
        order_id,
        customer_id,
        order_date,
        status,
        sum(line_total) as order_total
    from fct_order_items
    group by order_id, customer_id, order_date, status

)

select
    customers.customer_id,
    customers.first_name,
    customers.last_name,
    customers.country,
    count(per_order.order_id) as total_orders,
    coalesce(sum(per_order.order_total), 0) as lifetime_value,
    min(per_order.order_date) as first_order_date,
    max(per_order.order_date) as most_recent_order_date
from {{ ref('dim_customers') }} as customers
left join per_order on customers.customer_id = per_order.customer_id
group by
    customers.customer_id,
    customers.first_name,
    customers.last_name,
    customers.country
