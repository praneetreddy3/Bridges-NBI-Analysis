-- Databricks SQL Queries for Bridge Data Visualization
-- Table Name: cleaned_bridge_dataset_2024_and_2025
--
-- Instructions:
-- 1. Upload CSV to Databricks Data section
-- 2. Create table with same name as above
-- 3. Copy each query below into Databricks SQL Editor
-- 4. Execute one by one
-- 5. Click "Plot Options" button after each query to create visualizations
-- 6. Save/download visualization images to results/visualizations/ folder

-- ============================================================================
-- QUERY 1: Top 10 States by Bridge Count
-- Output: Bar Chart
-- Description: Shows which states have the most bridges in the dataset
-- ============================================================================
SELECT
    state_name,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY state_name
ORDER BY bridge_count DESC
LIMIT 10;

-- Save as: topstateswithhighestbridgecount.png


-- ============================================================================
-- QUERY 2: Distribution of Bridges by Year Built
-- Output: Histogram
-- Description: Shows when bridges were constructed (filtered from 1900)
-- ============================================================================
SELECT
    year_built,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
WHERE year_built >= 1900
GROUP BY year_built
ORDER BY year_built ASC;

-- Save as: Distributionofbridgesbyyearbuilt.png


-- ============================================================================
-- QUERY 3: Top 10 States by Average Daily Traffic
-- Output: Bar Chart
-- Description: Shows states with highest overall bridge traffic
-- ============================================================================
SELECT
    state_name,
    ROUND(AVG(avg_daily_traffic), 0) as avg_traffic,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY state_name
ORDER BY avg_traffic DESC
LIMIT 10;

-- Save as: top10stateswithhighestdailytraffic.png


-- ============================================================================
-- QUERY 4: Most Common Main Span Material
-- Output: Bar Chart
-- Description: Shows distribution of bridge materials across dataset
-- ============================================================================
SELECT
    main_material,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY main_material
ORDER BY bridge_count DESC;

-- Save as: MostcommonMainSpanMaterial.png


-- ============================================================================
-- QUERY 5: Top 10 States by Average Truck Traffic Percentage
-- Output: Pie Chart
-- Description: Shows states with highest truck traffic as percentage of total
-- ============================================================================
SELECT
    state_name,
    ROUND(AVG(truck_pct), 2) as avg_truck_percentage,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY state_name
ORDER BY avg_truck_percentage DESC
LIMIT 10;

-- Save as: top10statesbytrucktraffic.png


-- ============================================================================
-- QUERY 6: Distribution of Bridges by Top 10 Owner Agencies
-- Output: Pie Chart
-- Description: Shows which agencies own/manage the most bridges
-- ============================================================================
SELECT
    owner_agency,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY owner_agency
ORDER BY bridge_count DESC
LIMIT 10;

-- Save as: Distributionofbridgesbytop10owneragencies.png


-- ============================================================================
-- ADDITIONAL ANALYSIS QUERIES (Optional)
-- ============================================================================

-- Query A: Posted vs Non-Posted Bridges by State
SELECT
    state_name,
    posting_code,
    COUNT(*) as bridge_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY state_name), 2) as percentage
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY state_name, posting_code
ORDER BY state_name, posting_code;

-- Query B: Average Bridge Age by State
SELECT
    state_name,
    ROUND(AVG(bridge_age), 1) as avg_age,
    MIN(bridge_age) as min_age,
    MAX(bridge_age) as max_age,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY state_name
ORDER BY avg_age DESC;

-- Query C: Correlation Between Truck Traffic and Posting Status
SELECT
    posting_code,
    ROUND(AVG(truck_pct), 2) as avg_truck_pct,
    ROUND(STDDEV(truck_pct), 2) as stddev_truck_pct,
    COUNT(*) as bridge_count
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY posting_code;

-- Query D: Movable Bridges Analysis
SELECT
    is_movable,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM cleaned_bridge_dataset_2024_and_2025), 2) as percentage,
    COUNT(*) as bridge_count,
    ROUND(AVG(bridge_age), 1) as avg_age,
    ROUND(AVG(avg_daily_traffic), 0) as avg_traffic
FROM cleaned_bridge_dataset_2024_and_2025
GROUP BY is_movable;

-- Query E: Bridges with High Traffic and Truck Percentage
SELECT
    state_name,
    COUNT(*) as high_traffic_bridges,
    ROUND(AVG(avg_daily_traffic), 0) as avg_traffic,
    ROUND(AVG(truck_pct), 2) as avg_truck_pct
FROM cleaned_bridge_dataset_2024_and_2025
WHERE avg_daily_traffic > (SELECT PERCENTILE(avg_daily_traffic, 0.75) FROM cleaned_bridge_dataset_2024_and_2025)
  AND truck_pct > (SELECT PERCENTILE(truck_pct, 0.75) FROM cleaned_bridge_dataset_2024_and_2025)
GROUP BY state_name
ORDER BY high_traffic_bridges DESC;

-- ============================================================================
-- VISUALIZATION TIPS FOR DATABRICKS
-- ============================================================================
-- 1. After executing each query, click "Plot Options" button at bottom right
-- 2. Select chart type:
--    - Queries 1, 3, 4: Bar Chart (X: state_name/main_material, Y: count/percentage)
--    - Query 2: Histogram (X: year_built, Y: bridge_count)
--    - Queries 5, 6: Pie Chart (Label: state_name/owner_agency, Value: bridge_count)
-- 3. Click "Display" to render visualization
-- 4. Click download/export button to save as PNG
-- 5. Save with appropriate filename to results/visualizations/ folder

-- ============================================================================
-- Last Updated: April 2026
-- For issues, verify table name matches: cleaned_bridge_dataset_2024_and_2025
