-- Top energy consuming devices.
SELECT
    d.device_name,
    d.device_category,
    ROUND(SUM(r.power_consumption_kwh), 2) AS total_kwh,
    ROUND(SUM(r.energy_cost), 2) AS total_cost
FROM energy_readings r
JOIN devices d ON d.device_id = r.device_id
GROUP BY d.device_name, d.device_category
ORDER BY total_kwh DESC
LIMIT 10;

-- Monthly cost by device category.
SELECT
    strftime('%Y-%m', r.timestamp) AS month,
    d.device_category,
    ROUND(SUM(r.energy_cost), 2) AS total_cost
FROM energy_readings r
JOIN devices d ON d.device_id = r.device_id
GROUP BY month, d.device_category
ORDER BY month, total_cost DESC;

-- Peak hour usage profile.
SELECT
    CAST(strftime('%H', r.timestamp) AS INTEGER) AS hour,
    ROUND(SUM(r.power_consumption_kwh), 2) AS total_kwh,
    ROUND(SUM(r.energy_cost), 2) AS total_cost
FROM energy_readings r
GROUP BY hour
ORDER BY hour;

-- Anomaly alerts during peak hours.
SELECT
    r.timestamp,
    d.device_name,
    d.room_location,
    r.power_consumption_kwh,
    r.energy_cost
FROM energy_readings r
JOIN devices d ON d.device_id = r.device_id
WHERE CAST(strftime('%H', r.timestamp) AS INTEGER) BETWEEN 18 AND 22
  AND r.anomaly_flag = 1
ORDER BY r.timestamp DESC
LIMIT 50;

-- Room-level cost ranking.
SELECT
    d.room_location,
    ROUND(SUM(r.power_consumption_kwh), 2) AS total_kwh,
    ROUND(SUM(r.energy_cost), 2) AS total_cost,
    SUM(r.anomaly_flag) AS anomaly_count
FROM energy_readings r
JOIN devices d ON d.device_id = r.device_id
GROUP BY d.room_location
ORDER BY total_cost DESC;
