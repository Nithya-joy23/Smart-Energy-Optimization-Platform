# Power BI Integration Guide

## Recommended Data Source

Use `data/energy_consumption.csv` for the simplest import. Use `database/smart_energy.db` if you want a relational model with separate `devices` and `energy_readings` tables.

## Option 1: Connect Power BI to CSV

1. Open Power BI Desktop.
2. Select **Get Data > Text/CSV**.
3. Choose `data/energy_consumption.csv`.
4. Select **Transform Data**.
5. Set `timestamp` to Date/Time.
6. Set numeric columns to Decimal Number.
7. Load the table and create visuals.

## Option 2: Connect Power BI to SQLite

Power BI does not include native SQLite support in every installation.

1. Install a SQLite ODBC driver.
2. Open **Get Data > ODBC**.
3. Create or select a DSN pointing to `database/smart_energy.db`.
4. Import `devices` and `energy_readings`.
5. Create a relationship from `devices[device_id]` to `energy_readings[device_id]`.

## Suggested Dashboard Pages

1. Executive Overview: total kWh, total cost, active devices, anomaly count.
2. Energy Trends: daily and monthly consumption line charts.
3. Device Comparison: device and category rankings by kWh and cost.
4. Peak Usage: hour-of-day usage heatmap and peak-hour cost.
5. Forecast Insights: import the forecast API output or use Power BI trend visuals.
6. Anomaly Monitoring: anomaly table with device, location, timestamp, and severity.

## DAX Measures

```DAX
Total Energy kWh = SUM(energy_consumption[power_consumption_kwh])

Total Energy Cost = SUM(energy_consumption[energy_cost])

Average kWh per Reading = AVERAGE(energy_consumption[power_consumption_kwh])

Anomaly Count = SUM(energy_consumption[anomaly_flag])

Active Device Count =
CALCULATE(
    DISTINCTCOUNT(energy_consumption[device_id]),
    energy_consumption[status] = "ON"
)

Peak Hour Energy =
CALCULATE(
    [Total Energy kWh],
    HOUR(energy_consumption[timestamp]) >= 18,
    HOUR(energy_consumption[timestamp]) <= 22
)

Peak Hour Cost =
CALCULATE(
    [Total Energy Cost],
    HOUR(energy_consumption[timestamp]) >= 18,
    HOUR(energy_consumption[timestamp]) <= 22
)

Cost per kWh = DIVIDE([Total Energy Cost], [Total Energy kWh])

Anomaly Rate = DIVIDE([Anomaly Count], COUNTROWS(energy_consumption))

Estimated Savings 10 Percent = [Total Energy Cost] * 0.10
```

## Visual Suggestions

- Cards: `Total Energy kWh`, `Total Energy Cost`, `Active Device Count`, `Anomaly Count`.
- Line chart: `timestamp` by `Total Energy kWh`.
- Clustered bar chart: `device_name` by `Total Energy kWh`.
- Donut chart: `device_category` by `Total Energy Cost`.
- Matrix: `room_location` by `device_category`, values `Total Energy kWh`.
- Heatmap custom visual: day of week and hour, values `Total Energy kWh`.
- Table: timestamp, device, location, kWh, cost, anomaly flag.
