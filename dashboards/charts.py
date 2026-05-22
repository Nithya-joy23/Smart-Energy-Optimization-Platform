"""Reusable Plotly and Matplotlib charts for the Streamlit app."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PLOTLY_TEMPLATE = "plotly_white"


def line_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, title=title, template=PLOTLY_TEMPLATE, markers=True)
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20), hovermode="x unified")
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, title=title, template=PLOTLY_TEMPLATE)
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20))
    return fig


def pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    fig = px.pie(df, names=names, values=values, title=title, hole=0.42, template=PLOTLY_TEMPLATE)
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20))
    return fig


def heatmap(df: pd.DataFrame, title: str) -> go.Figure:
    fig = px.imshow(df, color_continuous_scale="Viridis", aspect="auto", title=title)
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20))
    return fig


def efficiency_matplotlib_chart(df: pd.DataFrame):
    """Return a Matplotlib figure showing efficiency score distribution."""
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.hist(df["efficiency_score"], bins=12, color="#2f80ed", edgecolor="white")
    ax.set_title("Device Efficiency Score Distribution")
    ax.set_xlabel("Efficiency Score")
    ax.set_ylabel("Device Count")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig
