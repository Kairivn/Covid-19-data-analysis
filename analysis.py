from typing import Union

"""
COVID-19 India Cases Explorer — Streamlit Dashboard
====================================================
An interactive dashboard for exploring COVID-19 case data across India
and its states/union territories.

Features
--------
* National & region-level KPI cards
* Daily new-case trends with 7-day rolling averages
* Recovery rate & case fatality rate analysis
* Top-states comparison bar / pie / line charts
* Choropleth-style heatmap of states by selected metric
* Downloadable filtered data

Data source: ``covid_india_cases.csv`` (bundled with the repo).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="COVID-19 India Explorer",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetric"] label {
        color: #a0aec0 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
    }
    /* sidebar polish */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141422 0%, #1a1a2e 100%);
    }
    /* Expander headers */
    details summary {
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header ──────────────────────────────────────────────────────────────────
st.title("🦠 COVID-19 India Cases Explorer")
st.caption(
    "Interactive dashboard tracking confirmed, active, recovered, and death "
    "cases across India and its states/UTs.  Use the sidebar controls to "
    "filter by region, metric, date range, and chart type."
)

# ─── Data loading ────────────────────────────────────────────────────────────
DATA_FILE = Path(__file__).parent / "covid_india_cases.csv"


@st.cache_data(show_spinner="Loading dataset …")
def load_data(path: Path) -> pd.DataFrame:
    """Read the CSV, clean columns, parse dates, and filter garbage rows."""
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date", "Region"]).copy()

    # Drop obviously wrong dates (e.g. 1970, pre-COVID rows before 2020-01-01)
    df = df[df["Date"] >= "2020-01-01"]

    numeric_cols = ["Confirmed Cases", "Active Cases", "Cured/Discharged", "Death"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df = df.sort_values(["Region", "Date"]).reset_index(drop=True)
    return df


df = load_data(DATA_FILE)
if df.empty:
    st.error("Dataset is empty or could not be loaded.  Please check `covid_india_cases.csv`.")
    st.stop()


# ─── Helper functions ────────────────────────────────────────────────────────
def fmt(value: Union[int, float]) -> str:
    """Comma-formatted integer string."""
    return f"{int(value):,}"


def get_latest_snapshot(data: pd.DataFrame) -> pd.DataFrame:
    """Return one row per region — the row with the latest date."""
    idx = data.groupby("Region")["Date"].idxmax()
    return data.loc[idx].reset_index(drop=True)


def compute_daily_new(data: pd.DataFrame, col: str) -> pd.DataFrame:
    """Compute daily new values and a 7-day rolling average for *col*."""
    data = data.sort_values("Date").copy()
    data[f"New {col}"] = data[col].diff().clip(lower=0)
    data[f"7d Avg {col}"] = data[f"New {col}"].rolling(7, min_periods=1).mean()
    return data


# ─── Sidebar controls ────────────────────────────────────────────────────────
latest_date = df["Date"].max().date()
earliest_date = df["Date"].min().date()
regions = sorted(df["Region"].unique())

st.sidebar.header("🎛️ Controls")

selected_region = st.sidebar.selectbox(
    "Region",
    regions,
    index=regions.index("India") if "India" in regions else 0,
)

METRIC_MAP = {
    "Confirmed": "Confirmed Cases",
    "Active": "Active Cases",
    "Recovered": "Cured/Discharged",
    "Deaths": "Death",
}
selected_metric = st.sidebar.radio("Case metric", list(METRIC_MAP.keys()))
metric_col = METRIC_MAP[selected_metric]

chart_type = st.sidebar.selectbox("Chart type", ["Bar", "Line", "Pie"])

date_range = st.sidebar.date_input(
    "Date range",
    value=(earliest_date, latest_date),
    min_value=earliest_date,
    max_value=latest_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range if not isinstance(date_range, tuple) else date_range[0]
if start_date > end_date:
    start_date, end_date = end_date, start_date

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset info**")
st.sidebar.write(f"Date range: **{earliest_date}** → **{latest_date}**")
st.sidebar.write(f"Rows: **{len(df):,}**")
st.sidebar.write(f"Regions: **{len(regions)}**")

# ─── Filtered data ───────────────────────────────────────────────────────────
mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
filtered_df = df[mask].copy()
latest_snapshot = get_latest_snapshot(df)

# ─── 1. National KPI cards ──────────────────────────────────────────────────
india_row = latest_snapshot[latest_snapshot["Region"] == "India"]
if india_row.empty:
    st.warning("No national-level (India) row found in the dataset.")
    st.stop()
india = india_row.squeeze()

confirmed = int(india["Confirmed Cases"])
active = int(india["Active Cases"])
recovered = int(india["Cured/Discharged"])
deaths = int(india["Death"])
cfr = round(100 * deaths / confirmed, 2) if confirmed else 0.0
recovery_rate = round(100 * recovered / confirmed, 2) if confirmed else 0.0

st.markdown("### 🇮🇳 National Summary")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Confirmed", fmt(confirmed))
c2.metric("Active", fmt(active))
c3.metric("Recovered", fmt(recovered))
c4.metric("Deaths", fmt(deaths))
c5.metric("Recovery Rate", f"{recovery_rate}%")
c6.metric("Case Fatality Rate", f"{cfr}%")

# ─── 2. Selected region KPIs ────────────────────────────────────────────────
region_row = latest_snapshot[latest_snapshot["Region"] == selected_region]
if region_row.empty:
    st.warning(f"No data for **{selected_region}**.")
    st.stop()
region_data = region_row.squeeze()

r_confirmed = int(region_data["Confirmed Cases"])
r_active = int(region_data["Active Cases"])
r_recovered = int(region_data["Cured/Discharged"])
r_deaths = int(region_data["Death"])
r_cfr = round(100 * r_deaths / r_confirmed, 2) if r_confirmed else 0.0
r_recovery = round(100 * r_recovered / r_confirmed, 2) if r_confirmed else 0.0
share_of_india = round(100 * r_confirmed / confirmed, 2) if confirmed else 0.0

st.markdown(f"### 📍 {selected_region} — Latest Snapshot")
r1, r2, r3, r4, r5, r6 = st.columns(6)
r1.metric("Confirmed", fmt(r_confirmed))
r2.metric("Active", fmt(r_active))
r3.metric("Recovered", fmt(r_recovered))
r4.metric("Deaths", fmt(r_deaths))
r5.metric("Recovery Rate", f"{r_recovery}%")
r6.metric("Share of India", f"{share_of_india}%")

st.markdown("---")

# ─── 3. Daily new cases & 7-day rolling average ─────────────────────────────
st.markdown(f"### 📈 Daily New Cases — {selected_region}")

region_ts = filtered_df[filtered_df["Region"] == selected_region].copy()
if region_ts.empty:
    st.info("No data for the selected region & date range.")
else:
    region_ts = compute_daily_new(region_ts, "Confirmed Cases")
    region_ts = compute_daily_new(region_ts, "Death")

    tab_cases, tab_deaths = st.tabs(["New Confirmed Cases", "New Deaths"])

    with tab_cases:
        fig_new = go.Figure()
        fig_new.add_trace(
            go.Bar(
                x=region_ts["Date"],
                y=region_ts["New Confirmed Cases"],
                name="Daily new",
                marker_color="rgba(99, 110, 250, 0.5)",
            )
        )
        fig_new.add_trace(
            go.Scatter(
                x=region_ts["Date"],
                y=region_ts["7d Avg Confirmed Cases"],
                name="7-day avg",
                line=dict(color="#ff6361", width=2.5),
            )
        )
        fig_new.update_layout(
            title=f"Daily new confirmed cases — {selected_region}",
            xaxis_title="Date",
            yaxis_title="Cases",
            hovermode="x unified",
            height=450,
            template="plotly_dark",
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig_new, use_container_width=True)

    with tab_deaths:
        fig_deaths = go.Figure()
        fig_deaths.add_trace(
            go.Bar(
                x=region_ts["Date"],
                y=region_ts["New Death"],
                name="Daily deaths",
                marker_color="rgba(239, 85, 59, 0.5)",
            )
        )
        fig_deaths.add_trace(
            go.Scatter(
                x=region_ts["Date"],
                y=region_ts["7d Avg Death"],
                name="7-day avg",
                line=dict(color="#ffa600", width=2.5),
            )
        )
        fig_deaths.update_layout(
            title=f"Daily new deaths — {selected_region}",
            xaxis_title="Date",
            yaxis_title="Deaths",
            hovermode="x unified",
            height=450,
            template="plotly_dark",
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig_deaths, use_container_width=True)

st.markdown("---")

# ─── 4. Cumulative trend (all case types) ───────────────────────────────────
st.markdown(f"### 📊 Cumulative Trend — {selected_region}")

if not region_ts.empty:
    trend_df = region_ts.melt(
        id_vars=["Date"],
        value_vars=["Confirmed Cases", "Active Cases", "Cured/Discharged", "Death"],
        var_name="Case Type",
        value_name="Count",
    )
    trend_df["Case Type"] = trend_df["Case Type"].replace(
        {
            "Confirmed Cases": "Confirmed",
            "Active Cases": "Active",
            "Cured/Discharged": "Recovered",
            "Death": "Deaths",
        }
    )
    color_map = {
        "Confirmed": "#636efa",
        "Active": "#ffa15a",
        "Recovered": "#00cc96",
        "Deaths": "#ef553b",
    }
    trend_fig = px.line(
        trend_df,
        x="Date",
        y="Count",
        color="Case Type",
        color_discrete_map=color_map,
        title=f"Cumulative cases — {selected_region}",
    )
    trend_fig.update_layout(
        hovermode="x unified",
        height=500,
        template="plotly_dark",
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(trend_fig, use_container_width=True)
else:
    st.info("No trend data for this selection.")

st.markdown("---")

# ─── 5. Top regions comparison chart ─────────────────────────────────────────
st.markdown(f"### 🏆 Regional Comparison — {selected_metric}")

states_only = latest_snapshot[~latest_snapshot["Region"].isin(["India", "World"])]
top_states = states_only.sort_values(metric_col, ascending=False).head(15).reset_index(drop=True)

if chart_type == "Bar":
    fig_comp = px.bar(
        top_states,
        x="Region",
        y=metric_col,
        color=metric_col,
        color_continuous_scale="Viridis",
        title=f"Top 15 states/UTs by {selected_metric.lower()} cases",
    )
elif chart_type == "Pie":
    fig_comp = px.pie(
        top_states,
        names="Region",
        values=metric_col,
        title=f"Share of {selected_metric.lower()} among top 15 states/UTs",
        hole=0.4,
    )
else:
    fig_comp = px.line(
        top_states,
        x="Region",
        y=metric_col,
        markers=True,
        title=f"Top 15 states/UTs by {selected_metric.lower()} cases",
    )

fig_comp.update_layout(height=500, template="plotly_dark")
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")

# ─── 6. State-level heatmap ──────────────────────────────────────────────────
st.markdown("### 🗺️ State-Level Heatmap")
st.caption("Monthly aggregated view of selected metric across all states.")

states_ts = filtered_df[~filtered_df["Region"].isin(["India", "World"])].copy()
if not states_ts.empty:
    states_ts["Month"] = states_ts["Date"].dt.to_period("M").astype(str)
    heatmap_data = (
        states_ts.groupby(["Region", "Month"])[metric_col]
        .max()
        .reset_index()
    )
    heatmap_pivot = heatmap_data.pivot(index="Region", columns="Month", values=metric_col).fillna(0)

    # Show only top 20 states for readability
    top20 = states_only.sort_values(metric_col, ascending=False).head(20)["Region"].tolist()
    heatmap_pivot = heatmap_pivot[heatmap_pivot.index.isin(top20)]

    fig_heat = px.imshow(
        heatmap_pivot,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        title=f"{selected_metric} cases over time — Top 20 states",
        labels=dict(x="Month", y="State", color=selected_metric),
    )
    fig_heat.update_layout(height=600, template="plotly_dark")
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("No state-level data in the selected date range.")

st.markdown("---")

# ─── 7. Recovery rate & CFR across states ────────────────────────────────────
st.markdown("### 💊 Recovery Rate & Case Fatality Rate by State")

states_rates = states_only.copy()
states_rates["Recovery Rate (%)"] = (
    100 * states_rates["Cured/Discharged"] / states_rates["Confirmed Cases"]
).round(2)
states_rates["CFR (%)"] = (
    100 * states_rates["Death"] / states_rates["Confirmed Cases"]
).round(2)
states_rates = states_rates.replace([np.inf, -np.inf], 0).fillna(0)

col_left, col_right = st.columns(2)

with col_left:
    fig_rr = px.bar(
        states_rates.sort_values("Recovery Rate (%)", ascending=False).head(15),
        x="Region",
        y="Recovery Rate (%)",
        color="Recovery Rate (%)",
        color_continuous_scale="Greens",
        title="Top 15 states by recovery rate",
    )
    fig_rr.update_layout(height=420, template="plotly_dark", showlegend=False)
    st.plotly_chart(fig_rr, use_container_width=True)

with col_right:
    fig_cfr = px.bar(
        states_rates.sort_values("CFR (%)", ascending=False).head(15),
        x="Region",
        y="CFR (%)",
        color="CFR (%)",
        color_continuous_scale="Reds",
        title="Top 15 states by case fatality rate",
    )
    fig_cfr.update_layout(height=420, template="plotly_dark", showlegend=False)
    st.plotly_chart(fig_cfr, use_container_width=True)

st.markdown("---")

# ─── 8. Growth rate (week-over-week) ─────────────────────────────────────────
st.markdown(f"### 📉 Weekly Growth Rate — {selected_region}")

if not region_ts.empty:
    weekly = region_ts.set_index("Date")["Confirmed Cases"].resample("W").max()
    growth = weekly.pct_change().dropna() * 100
    growth_df = growth.reset_index()
    growth_df.columns = ["Week", "Growth Rate (%)"]

    fig_growth = px.area(
        growth_df,
        x="Week",
        y="Growth Rate (%)",
        title=f"Week-over-week growth in confirmed cases — {selected_region}",
        color_discrete_sequence=["#ab63fa"],
    )
    fig_growth.update_layout(
        height=400,
        template="plotly_dark",
        hovermode="x unified",
    )
    st.plotly_chart(fig_growth, use_container_width=True)
else:
    st.info("Insufficient data for growth rate calculation.")

st.markdown("---")

# ─── 9. Data table with download ─────────────────────────────────────────────
st.markdown("### 📋 Region-Level Data Table")

table_data = (
    states_only[["Region", "Confirmed Cases", "Active Cases", "Cured/Discharged", "Death"]]
    .rename(columns={"Cured/Discharged": "Recovered"})
    .sort_values("Confirmed Cases", ascending=False)
    .reset_index(drop=True)
)
st.dataframe(table_data, use_container_width=True, height=400)

csv_export = table_data.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download table as CSV",
    data=csv_export,
    file_name="covid19_india_states_summary.csv",
    mime="text/csv",
)

st.markdown("---")

# ─── 10. Key insights panel ─────────────────────────────────────────────────
with st.expander("🔍 Key Insights", expanded=True):
    top = states_only.sort_values(metric_col, ascending=False).iloc[0]
    bottom = states_only.sort_values(metric_col, ascending=True).iloc[0]

    st.markdown(
        f"""
| Insight | Value |
|---------|-------|
| **Highest {selected_metric.lower()} cases** | {top['Region']} — {fmt(top[metric_col])} |
| **Lowest {selected_metric.lower()} cases** | {bottom['Region']} — {fmt(bottom[metric_col])} |
| **Total states/UTs tracked** | {len(states_only)} |
| **National recovery rate** | {recovery_rate}% |
| **National case fatality rate** | {cfr}% |
"""
    )

    if selected_region not in ("India", "World") and confirmed:
        share = round(100 * r_confirmed / confirmed, 2)
        st.info(
            f"**{selected_region}** accounts for **{share}%** of India's "
            f"total confirmed cases."
        )

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    ---
    <div style="text-align:center; color:#888; font-size:0.85rem;">
        Built with <a href="https://streamlit.io" target="_blank">Streamlit</a> &
        <a href="https://plotly.com/python/" target="_blank">Plotly</a> ·
        <a href="https://github.com" target="_blank">View on GitHub</a>
    </div>
    """,
    unsafe_allow_html=True,
)
