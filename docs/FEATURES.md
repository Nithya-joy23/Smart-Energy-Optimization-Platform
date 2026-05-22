# Feature Documentation

## Dataset Generation

The generator creates hourly consumption for 24 devices across HVAC, lighting, IT equipment, industrial machines, kitchen equipment, charging, security, and other categories.

It models:

- Peak-hour consumption.
- Weekend and workday behavior.
- Temperature influence.
- Device ON/OFF status.
- Voltage, current, and cost.
- Random spikes and anomaly flags.

## Data Processing

Processing functions clean missing values, normalize timestamps, engineer date and peak-hour features, and calculate:

- Daily usage.
- Monthly usage.
- Device-level analytics.
- Category costs.
- Efficiency scores.
- Peak-hour profiles.

## Forecasting

The project includes three lightweight forecasting methods:

- Hourly profile forecast for next-day predictions.
- Moving average forecast for weekly predictions.
- Linear regression trend forecast for monthly projections.

## Anomaly Detection

Anomaly detection combines:

- Dataset anomaly flags.
- Z-score outliers.
- IQR outliers.
- Device-specific percentile thresholds.

## Optimization Engine

Recommendations are generated from peak-hour load, efficiency score, anomalies, category behavior, and device cost. Each recommendation includes priority, estimated savings percentage, and estimated monthly savings.
