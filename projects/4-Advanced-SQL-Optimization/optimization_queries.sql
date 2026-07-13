-- Advanced SQL Optimization - Performance Tuning Examples
-- PostgreSQL/SQL Server syntax

-- ======================== PROBLEM 1: N+1 QUERY ========================
-- BEFORE: Inefficient (N+1 problem)
/*
SELECT * FROM customers WHERE status = 'active';
-- Then loop and execute for each customer:
SELECT * FROM orders WHERE customer_id = ?;
*/

-- AFTER: Efficient Join
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.order_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.status = 'active'
GROUP BY c.customer_id, c.customer_name;

-- ======================== PROBLEM 2: MISSING INDEXES ========================
-- Create indexes for frequently filtered columns
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);

-- Composite index for multi-column filtering
CREATE INDEX idx_orders_composite ON orders(customer_id, order_date, order_amount);

-- ======================== PROBLEM 3: INEFFICIENT AGGREGATION ========================
-- BEFORE: Full table scan
/*
SELECT 
    customer_id,
    SUM(CASE WHEN order_status = 'completed' THEN order_amount ELSE 0 END) as completed_sales
FROM orders
WHERE YEAR(order_date) = 2024;
*/

-- AFTER: Pre-aggregated view with partitioning
CREATE TABLE orders_daily_summary AS
SELECT 
    DATE_TRUNC('day', order_date) as order_date,
    customer_id,
    order_status,
    SUM(order_amount) as daily_amount,
    COUNT(*) as order_count
FROM orders
GROUP BY DATE_TRUNC('day', order_date), customer_id, order_status;

CREATE INDEX idx_summary_date_customer ON orders_daily_summary(order_date, customer_id);

-- Query pre-aggregated data
SELECT 
    customer_id,
    SUM(CASE WHEN order_status = 'completed' THEN daily_amount ELSE 0 END) as completed_sales
FROM orders_daily_summary
WHERE order_date >= '2024-01-01'
GROUP BY customer_id;

-- ======================== PROBLEM 4: SUBQUERY INEFFICIENCY ========================
-- BEFORE: Correlated subquery (executed for every row)
/*
SELECT 
    customer_id,
    customer_name,
    (SELECT COUNT(*) FROM orders WHERE customer_id = c.customer_id) as order_count
FROM customers c;
*/

-- AFTER: Window functions (single pass)
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) OVER (PARTITION BY c.customer_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- ======================== PROBLEM 5: MISSING WHERE CLAUSE ========================
-- BEFORE: Full table scan
/*
SELECT * FROM huge_transactions_table;
*/

-- AFTER: Add WHERE clause to filter partitions
SELECT 
    transaction_id,
    customer_id,
    amount,
    transaction_date
FROM transactions
WHERE transaction_date >= DATE_TRUNC('month', NOW() - INTERVAL '1 month')
    AND transaction_date < DATE_TRUNC('month', NOW())
    AND amount > 100;

-- ======================== PROBLEM 6: COMPLEX JOINS ========================
-- BEFORE: Multiple full joins
/*
SELECT *
FROM orders o
FULL JOIN customers c ON o.customer_id = c.customer_id
FULL JOIN products p ON o.product_id = p.product_id
FULL JOIN categories cat ON p.category_id = cat.category_id;
*/

-- AFTER: Optimized with inner joins and pre-filtering
SELECT 
    o.order_id,
    c.customer_id,
    c.customer_name,
    p.product_id,
    p.product_name,
    cat.category_name,
    o.order_amount,
    o.order_date
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p ON o.product_id = p.product_id
INNER JOIN categories cat ON p.category_id = cat.category_id
WHERE o.order_date >= '2024-01-01'
    AND c.status = 'active';

-- ======================== PROBLEM 7: UNION vs UNION ALL ========================
-- BEFORE: Slower with UNION (removes duplicates)
SELECT customer_id FROM active_customers
UNION
SELECT customer_id FROM premium_customers;

-- AFTER: Use UNION ALL if duplicates are acceptable
SELECT customer_id FROM active_customers
UNION ALL
SELECT customer_id FROM premium_customers;

-- ======================== PROBLEM 8: MATERIALIZED VIEWS ========================
-- Create materialized view for expensive calculations
CREATE MATERIALIZED VIEW customer_metrics_mv AS
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(DISTINCT o.order_id) as lifetime_orders,
    SUM(o.order_amount) as lifetime_value,
    MAX(o.order_date) as last_order_date,
    AVG(o.order_amount) as avg_order_value,
    DATEDIFF(day, MIN(o.order_date), MAX(o.order_date)) as customer_lifetime_days
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;

CREATE INDEX idx_mv_customer_id ON customer_metrics_mv(customer_id);

-- Query materialized view (much faster)
SELECT 
    customer_id,
    customer_name,
    lifetime_value,
    customer_lifetime_days
FROM customer_metrics_mv
WHERE lifetime_value > 1000;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW CONCURRENTLY customer_metrics_mv;

-- ======================== PROBLEM 9: QUERY PLAN ANALYSIS ========================
-- Use EXPLAIN to analyze query performance
EXPLAIN ANALYZE
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as order_count,
    SUM(o.order_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.status = 'active'
GROUP BY c.customer_id, c.customer_name;

-- ======================== PERFORMANCE TIPS ========================
-- 1. Use LIMIT for testing large datasets
-- 2. Use DISTINCT carefully (expensive operation)
-- 3. Avoid functions on WHERE clause columns (prevents index usage)
-- 4. Use EXISTS instead of IN for large lists
-- 5. Partition large tables by date ranges
-- 6. Use column lists instead of SELECT *
-- 7. Archive historical data to separate tables
-- 8. Monitor slow query logs
-- 9. Update statistics regularly
-- 10. Use pagination for large result sets
