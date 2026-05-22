"""Streamlit dashboard for the Smart Energy Optimization Platform."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboards.charts import bar_chart, efficiency_matplotlib_chart, heatmap, line_chart, pie_chart
from database.db_manager import create_tables, fetch_energy_data, load_csv_to_database, run_query
from models.anomaly_detection import anomaly_summary, combined_anomaly_detection
from models.forecasting import combined_forecast
from models.optimization import generate_recommendations, savings_summary
from utils.config import DATA_PATH, DB_PATH
from utils.data_generator import generate_energy_dataset
from utils.data_processing import (
    calculate_kpis,
    category_cost_analysis,
    daily_aggregation,
    device_analytics,
    engineer_features,
    monthly_aggregation,
    peak_usage_by_hour,
)


st.set_page_config(
    page_title="Smart Energy Optimization Platform",
    page_icon=":zap:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .main .block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
        [data-testid="stSidebar"] { background: #0f172a; }
        [data-testid="stSidebar"] * { color: #f8fafc; }
        .metric-card {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        }
        .metric-label { color: #64748b; font-size: 0.86rem; margin-bottom: 0.25rem; }
        .metric-value { color: #0f172a; font-size: 1.65rem; font-weight: 750; }
        .metric-note { color: #64748b; font-size: 0.8rem; margin-top: 0.35rem; }
        .alert-card {
            border-left: 5px solid #e11d48;
            border-radius: 8px;
            padding: 14px 16px;
            background: #fff1f2;
            margin-bottom: 12px;
        }
        .rec-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
            margin-bottom: 12px;
        }
        .priority-high { color: #b91c1c; font-weight: 700; }
        .priority-medium { color: #b45309; font-weight: 700; }
        .priority-low { color: #047857; font-weight: 700; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_data_exists() -> None:
    csv_path = Path(DATA_PATH)
    db_path = Path(DB_PATH)
    if not csv_path.exists():
        generate_energy_dataset(csv_path, days=150)
    if not db_path.exists():
        create_tables(db_path)
        load_csv_to_database(csv_path, db_path, replace=True)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    ensure_data_exists()
    return fetch_energy_data(DB_PATH)


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("Smart Energy")
    st.sidebar.caption("Monitoring, forecasting, anomaly detection, and optimization")
    data = engineer_features(df)
    categories = sorted(data["device_category"].unique())
    locations = sorted(data["room_location"].unique())
    selected_categories = st.sidebar.multiselect("Device categories", categories, default=categories)
    selected_locations = st.sidebar.multiselect("Locations", locations, default=locations)
    min_date = data["timestamp"].min().date()
    max_date = data["timestamp"].max().date()
    start_date, end_date = st.sidebar.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    filtered = data[
        data["device_category"].isin(selected_categories)
        & data["room_location"].isin(selected_locations)
        & (data["timestamp"].dt.date >= start_date)
        & (data["timestamp"].dt.date <= end_date)
    ]
    return filtered


def home_dashboard(df: pd.DataFrame) -> None:
    st.title("Smart Energy Optimization Platform")
    st.caption("Portfolio-grade energy intelligence dashboard powered by Python, SQL, forecasting, and REST APIs.")
    kpis = calculate_kpis(df)
    cols = st.columns(4)
    with cols[0]:
        metric_card("Total Energy", f"{kpis['total_energy_kwh']:,.0f} kWh", "All selected readings")
    with cols[1]:
        metric_card("Latest Monthly Cost", f"${kpis['monthly_cost']:,.2f}", "Based on tariff model")
    with cols[2]:
        metric_card("Active Devices", f"{kpis['active_devices']}", "Devices currently observed ON")
    with cols[3]:
        metric_card("Peak Alerts", f"{kpis['peak_alerts']}", "Anomalies during 6 PM-10 PM")

    daily = daily_aggregation(df)
    monthly = monthly_aggregation(df)
    hourly = peak_usage_by_hour(df)
    cost = category_cost_analysis(df).head(10)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(line_chart(daily, "timestamp", "power_consumption_kwh", "Daily Energy Usage"), use_container_width=True)
    with col2:
        st.plotly_chart(pie_chart(cost, "device_category", "energy_cost", "Cost by Category"), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(bar_chart(hourly, "hour", "power_consumption_kwh", "Peak Usage by Hour"), use_container_width=True)
    with col4:
        st.plotly_chart(bar_chart(monthly, "month", "energy_cost", "Monthly Cost Trend"), use_container_width=True)


def device_dashboard(df: pd.DataFrame) -> None:
    st.title("Device Analytics")
    analytics = device_analytics(df)
    top = analytics.head(15)
    col1, col2 = st.columns([1.4, 1])
    with col1:
        st.plotly_chart(bar_chart(top, "device_name", "total_kwh", "Top Devices by Energy Usage", "device_category"), use_container_width=True)
    with col2:
        st.pyplot(efficiency_matplotlib_chart(analytics), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(bar_chart(top, "device_name", "efficiency_score", "Efficiency Score by Device"), use_container_width=True)
    with col4:
        category = category_cost_analysis(df)
        st.plotly_chart(bar_chart(category, "device_category", "energy_cost", "Category Cost Analysis"), use_container_width=True)

    st.subheader("Device Performance Table")
    st.dataframe(analytics, use_container_width=True, hide_index=True)


def forecast_dashboard(df: pd.DataFrame) -> None:
    st.title("Forecast Dashboard")
    forecasts = combined_forecast(df)
    daily = daily_aggregation(df)
    daily["timestamp"] = pd.to_datetime(daily["timestamp"])

    col1, col2 = st.columns(2)
    with col1:
        next_day = forecasts["next_day"]
        st.metric("Next-Day Forecast", f"{next_day['forecast_kwh'].sum():,.0f} kWh")
        st.plotly_chart(line_chart(next_day, "timestamp", "forecast_kwh", "Next-Day Hourly Prediction"), use_container_width=True)
    with col2:
        weekly = forecasts["weekly"]
        st.metric("Weekly Forecast", f"{weekly['forecast_kwh'].sum():,.0f} kWh")
        st.plotly_chart(line_chart(weekly, "timestamp", "forecast_kwh", "7-Day Moving Average Forecast"), use_container_width=True)

    monthly = forecasts["monthly"]
    history = daily.tail(45).rename(columns={"power_consumption_kwh": "kwh"})
    future = monthly.rename(columns={"forecast_kwh": "kwh"})
    history["series"] = "Actual"
    future["series"] = "Forecast"
    combined = pd.concat([history[["timestamp", "kwh", "series"]], future[["timestamp", "kwh", "series"]]])
    fig = px.line(combined, x="timestamp", y="kwh", color="series", title="Monthly Trend Forecast", markers=True)
    st.plotly_chart(fig, use_container_width=True)


def anomaly_dashboard(df: pd.DataFrame) -> None:
    st.title("Anomaly Detection")
    anomalies = combined_anomaly_detection(df)
    detected = anomalies[anomalies["detected_anomaly"]].sort_values("timestamp", ascending=False)
    summary = anomaly_summary(df)
    cols = st.columns(3)
    cols[0].metric("Detected Anomalies", f"{len(detected):,}")
    cols[1].metric("High Severity", f"{(detected['severity'] == 'High').sum():,}")
    cols[2].metric("Affected Devices", f"{detected['device_id'].nunique():,}")

    recent_alerts = detected.head(5)
    for _, row in recent_alerts.iterrows():
        st.markdown(
            f"""
            <div class="alert-card">
                <strong>{row['device_name']}</strong> in {row['room_location']} used
                <strong>{row['power_consumption_kwh']:.2f} kWh</strong> at {row['timestamp']}.
                Severity: <strong>{row['severity']}</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([1.6, 1])
    with col1:
        sample = anomalies.groupby("timestamp", as_index=False).agg(
            power_consumption_kwh=("power_consumption_kwh", "sum"),
            detected_anomaly=("detected_anomaly", "sum"),
        )
        fig = line_chart(sample.tail(400), "timestamp", "power_consumption_kwh", "Recent Consumption with Spike Context")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.plotly_chart(bar_chart(summary.head(12), "device_name", "anomaly_count", "Anomalies by Device"), use_container_width=True)

    heat = engineer_features(anomalies)
    heat_table = heat.pivot_table(index="day_name", columns="hour", values="detected_anomaly", aggfunc="sum").fillna(0)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat_table = heat_table.reindex(day_order)
    st.plotly_chart(heatmap(heat_table, "Anomaly Heatmap by Day and Hour"), use_container_width=True)
    st.dataframe(detected.head(100), use_container_width=True, hide_index=True)


def optimization_dashboard(df: pd.DataFrame) -> None:
    st.title("Optimization Recommendations")
    recommendations = generate_recommendations(df)
    summary = savings_summary(df)
    cols = st.columns(4)
    cols[0].metric("Estimated Monthly Savings", f"${summary['total_estimated_monthly_savings']:,.2f}")
    cols[1].metric("Average Savings", f"{summary['average_savings_percent']:.1f}%")
    cols[2].metric("High Priority Actions", f"{summary['high_priority_actions']}")
    cols[3].metric("Highest Usage Hour", f"{summary['highest_usage_hour']}:00")

    for _, row in recommendations.head(12).iterrows():
        priority_class = f"priority-{str(row['priority']).lower()}"
        st.markdown(
            f"""
            <div class="rec-card">
                <div><strong>{row['device_name']}</strong> | {row['device_category']} | {row['room_location']}</div>
                <div class="{priority_class}">{row['priority']} Priority | {row['estimated_savings_percent']}% estimated savings</div>
                <p>{row['recommendation']}</p>
                <strong>Estimated monthly savings:</strong> ${row['estimated_monthly_savings']:.2f}
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.dataframe(recommendations, use_container_width=True, hide_index=True)


def sql_dashboard() -> None:
    st.title("SQL Analytics")
    predefined = {
        "Top 10 energy consuming devices": """
            SELECT d.device_name, d.device_category, ROUND(SUM(r.power_consumption_kwh), 2) AS total_kwh
            FROM energy_readings r
            JOIN devices d ON d.device_id = r.device_id
            GROUP BY d.device_name, d.device_category
            ORDER BY total_kwh DESC
            LIMIT 10;
        """,
        "Monthly cost by category": """
            SELECT strftime('%Y-%m', r.timestamp) AS month, d.device_category,
                   ROUND(SUM(r.energy_cost), 2) AS total_cost
            FROM energy_readings r
            JOIN devices d ON d.device_id = r.device_id
            GROUP BY month, d.device_category
            ORDER BY month, total_cost DESC;
        """,
        "Peak-hour anomaly alerts": """
            SELECT r.timestamp, d.device_name, d.room_location, r.power_consumption_kwh, r.energy_cost
            FROM energy_readings r
            JOIN devices d ON d.device_id = r.device_id
            WHERE CAST(strftime('%H', r.timestamp) AS INTEGER) BETWEEN 18 AND 22
              AND r.anomaly_flag = 1
            ORDER BY r.timestamp DESC
            LIMIT 50;
        """,
    }
    selected = st.selectbox("Predefined query", list(predefined.keys()))
    query = st.text_area("SQL query", predefined[selected], height=180)
    if st.button("Run query", type="primary"):
        try:
            result = run_query(query, DB_PATH)
            st.success(f"Returned {len(result):,} rows")
            st.dataframe(result, use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Query failed: {exc}")


def main() -> None:
    apply_styles()
    df = load_data()
    filtered = sidebar_filters(df)
    page = st.sidebar.radio(
        "Dashboard pages",
        [
            "Home Dashboard",
            "Device Analytics",
            "Forecast",
            "Anomaly Detection",
            "Optimization Recommendations",
            "SQL Analytics",
        ],
    )
    if filtered.empty and page != "SQL Analytics":
        st.warning("No data available for the selected filters.")
        return
    if page == "Home Dashboard":
        home_dashboard(filtered)
    elif page == "Device Analytics":
        device_dashboard(filtered)
    elif page == "Forecast":
        forecast_dashboard(filtered)
    elif page == "Anomaly Detection":
        anomaly_dashboard(filtered)
    elif page == "Optimization Recommendations":
        optimization_dashboard(filtered)
    else:
        sql_dashboard()


if __name__ == "__main__":
    main()
