-- Cloud Data Warehouse Project - dbt Models

-- ======================== STAGING LAYER ========================
-- Models to clean and standardize raw data

{{ config(
    materialized='view',
    schema='staging'
) }}

-- stg_customers.sql
SELECT
    customer_id,
    LOWER(TRIM(customer_name)) as customer_name,
    LOWER(TRIM(email)) as email,
    TRIM(city) as city,
    TRIM(state) as state,
    TRIM(country) as country,
    CAST(signup_date AS DATE) as signup_date,
    CASE 
        WHEN customer_status = 'active' THEN 1
        ELSE 0
    END as is_active,
    CURRENT_TIMESTAMP as dbt_loaded_at
FROM {{ source('raw', 'customers') }}
WHERE customer_id IS NOT NULL

-- ======================== INTERMEDIATE LAYER ========================
-- Models for complex transformations

{{ config(
    materialized='table',
    schema='intermediate'
) }}

-- int_customer_transactions.sql
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(DISTINCT t.transaction_id) as total_transactions,
    SUM(t.transaction_amount) as total_spent,
    AVG(t.transaction_amount) as avg_transaction,
    MIN(t.transaction_date) as first_purchase_date,
    MAX(t.transaction_date) as last_purchase_date,
    DATEDIFF(day, MIN(t.transaction_date), MAX(t.transaction_date)) as days_active
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ source('raw', 'transactions') }} t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name

-- ======================== MARTS LAYER ========================
-- Analytics-ready fact and dimension tables

{{ config(
    materialized='table',
    schema='marts',
    indexes=[{'columns': ['customer_id', 'date'], 'type': 'btree'}]
) }}

-- fct_sales.sql (Fact Table)
SELECT
    {{ dbt_utils.generate_surrogate_key(['transaction_id']) }} as transaction_sk,
    c.customer_id,
    p.product_id,
    DATE_TRUNC('month', t.transaction_date) as transaction_month,
    t.transaction_amount,
    t.quantity,
    t.discount_percent,
    t.transaction_amount * (1 - t.discount_percent/100) as net_amount,
    CASE 
        WHEN t.transaction_amount > 100 THEN 'High Value'
        WHEN t.transaction_amount > 50 THEN 'Medium Value'
        ELSE 'Low Value'
    END as value_segment
FROM {{ source('raw', 'transactions') }} t
JOIN {{ ref('stg_customers') }} c ON t.customer_id = c.customer_id
JOIN {{ ref('stg_products') }} p ON t.product_id = p.product_id

-- dim_customers.sql (Dimension Table)
{{ config(
    materialized='table',
    schema='marts',
    unique_key='customer_id'
) }}

SELECT
    c.customer_id,
    c.customer_name,
    c.email,
    c.city,
    c.state,
    c.country,
    c.signup_date,
    c.is_active,
    ct.total_transactions,
    ct.total_spent,
    ct.avg_transaction,
    CASE 
        WHEN ct.total_spent > 1000 THEN 'VIP'
        WHEN ct.total_spent > 500 THEN 'Premium'
        WHEN ct.total_spent > 100 THEN 'Standard'
        ELSE 'Bronze'
    END as customer_segment,
    CURRENT_TIMESTAMP as last_updated
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('int_customer_transactions') }} ct ON c.customer_id = ct.customer_id

-- ======================== MACROS ========================
-- Reusable transformation logic

-- macros/get_customer_lifetime_value.sql
{% macro get_customer_lifetime_value(customer_id) %}
    SELECT 
        SUM(transaction_amount) as clv
    FROM {{ source('raw', 'transactions') }}
    WHERE customer_id = {{ customer_id }}
{% endmacro %}

-- macros/generate_date_dimension.sql
{% macro generate_date_dimension(start_date, end_date) %}
    WITH date_spine AS (
        SELECT 
            CAST(date_column AS DATE) as date_key,
            EXTRACT(YEAR FROM date_column) as year,
            EXTRACT(MONTH FROM date_column) as month,
            EXTRACT(DAY FROM date_column) as day,
            EXTRACT(QUARTER FROM date_column) as quarter,
            DAYNAME(date_column) as day_name
        FROM dbt_utils.generate_series({{ start_date }}, {{ end_date }}, '1 day'::INTERVAL)
    )
    SELECT * FROM date_spine
{% endmacro %}
