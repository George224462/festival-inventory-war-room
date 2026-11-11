-- ============================================================
-- FESTIVAL INVENTORY WAR ROOM: OPERATIONAL SQL ANALYTICS
-- Database: C:\Users\pc\festival-inventory-war-room\data\festival_inventory.db
-- Table: inventory_analytics
-- ============================================================

-- Query 1: Critical Stockout Risk (High-Value, High-Volatility SKUs under Reorder Point)
-- These are Class 'AZ' items: High financial spend + volatile demand + low stock.
SELECT 
    item_id,
    item_name,
    category,
    vendor_name,
    current_stock_units,
    reorder_point_units,
    safety_stock_units,
    annual_spend_usd,
    abc_xyz_matrix
FROM inventory_analytics
WHERE reorder_flag = 'CRITICAL: REORDER'
  AND abc_class = 'A'
ORDER BY annual_spend_usd DESC;

-- Query 2: ABC-XYZ 3x3 Matrix Summary (Distribution of Inventory Capital)
SELECT 
    abc_xyz_matrix,
    COUNT(*) AS total_skus,
    ROUND(SUM(annual_spend_usd), 2) AS total_annual_spend_usd,
    ROUND(AVG(cv_demand), 4) AS avg_volatility_cv,
    SUM(CASE WHEN reorder_flag = 'CRITICAL: REORDER' THEN 1 ELSE 0 END) AS skus_to_reorder
FROM inventory_analytics
GROUP BY abc_xyz_matrix
ORDER BY total_annual_spend_usd DESC;

-- Query 3: Category Financial & Volatility Overview
SELECT 
    category,
    COUNT(*) AS sku_count,
    ROUND(SUM(annual_spend_usd), 2) AS category_spend_usd,
    ROUND(AVG(unit_cost_usd), 2) AS avg_unit_cost,
    SUM(safety_stock_units) AS total_safety_stock_needed,
    SUM(eoq_units) AS total_economic_order_volume
FROM inventory_analytics
GROUP BY category
ORDER BY category_spend_usd DESC;

-- Query 4: Vendor Operational Risk Breakdown (Which suppliers have the most critical items?)
SELECT 
    vendor_name,
    COUNT(*) AS total_items_supplied,
    SUM(CASE WHEN reorder_flag = 'CRITICAL: REORDER' THEN 1 ELSE 0 END) AS critical_reorders_pending,
    ROUND(SUM(annual_spend_usd), 2) AS total_vendor_spend_usd
FROM inventory_analytics
GROUP BY vendor_name
ORDER BY critical_reorders_pending DESC, total_vendor_spend_usd DESC;