"""
Inventory Wastage Dashboard
---------------------------
Visualizes weekly opening stock, purchases, consumption, and closing stock
for individual inventory items across 2025 (53 weekly data points), to help
assess whether purchasing is consistently outpacing consumption (wastage signal).

Run with:
    streamlit run app.py
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Inventory Wastage Dashboard", layout="wide")

DATA_PATH = "consolidated_2025_with_metrics.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["week_start", "week_end"])
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Sidebar - filters
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")

suppliers = sorted(df["supplier"].dropna().unique())
selected_supplier = st.sidebar.selectbox("Supplier", ["All"] + suppliers)

if selected_supplier != "All":
    item_pool = df[df["supplier"] == selected_supplier]
else:
    item_pool = df

items = sorted(item_pool["item"].unique())
selected_item = st.sidebar.selectbox("Item", items)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: 53 weekly snapshots (week 1 starts 30 Dec 2024). "
    "purchase_surplus = purchased − consumed. "
    "cumulative_surplus tracks running drift over the year — "
    "a sustained upward trend suggests over-ordering relative to consumption."
)

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------
item_df = df[df["item"] == selected_item].sort_values("week").reset_index(drop=True)

st.title("Inventory Wastage Dashboard")
st.subheader(selected_item.replace("_", " ").title())

supplier_name = item_df["supplier"].mode().iat[0] if not item_df.empty else "—"
st.caption(f"Supplier: {supplier_name} | Weeks of data: {len(item_df)}")

# --- KPI cards -------------------------------------------------------------
total_purchased = item_df["total_purchased"].sum()
total_consumed = item_df["consumption"].sum()
net_surplus = total_purchased - total_consumed
pct_surplus = (net_surplus / total_consumed * 100) if total_consumed else float("nan")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Purchased (2025)", f"{total_purchased:,.1f}")
col2.metric("Total Consumed (2025)", f"{total_consumed:,.1f}")
col3.metric("Net Surplus", f"{net_surplus:,.1f}")
col4.metric("Surplus as % of Consumption",
            f"{pct_surplus:,.1f}%" if pd.notna(pct_surplus) else "n/a")

# --- Main chart: opening / closing stock + purchased / consumed (line chart) ---
fig = go.Figure()

series_specs = [
    ("opening_stock", "Opening Stock", "#54A24B"),
    ("total_purchased", "Purchased", "#4C78A8"),
    ("consumption", "Consumed", "#F58518"),
    ("closing_stock", "Closing Stock", "#B279A2"),
]

for col, label, color in series_specs:
    fig.add_trace(go.Scatter(
        x=item_df["week"], y=item_df[col],
        name=label, mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(size=4)
    ))

fig.update_layout(
    title="Weekly Purchased, Consumed, Opening & Closing Stock — 2025",
    xaxis_title="Week (1–53)",
    yaxis_title="Quantity",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=480,
    margin=dict(t=80),
)
fig.update_xaxes(dtick=2)

st.plotly_chart(fig, use_container_width=True)

# --- Secondary chart: cumulative surplus / drift ----------------------------
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=item_df["week"], y=item_df["cumulative_surplus"],
    mode="lines+markers", name="Cumulative Surplus",
    line=dict(color="#E45756", width=2),
    fill="tozeroy"
))
fig2.add_hline(y=0, line_dash="dash", line_color="gray")
fig2.update_layout(
    title="Cumulative Purchase Surplus (Drift) — Running Total Over 2025",
    xaxis_title="Week (1–53)",
    yaxis_title="Cumulative Surplus (Purchased − Consumed)",
    height=350,
    margin=dict(t=60),
)
fig2.update_xaxes(dtick=2)

st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "A persistently rising cumulative surplus suggests purchasing has "
    "structurally outpaced consumption (potential over-ordering / wastage risk). "
    "A persistently falling line indicates stock is being run down faster than "
    "it's replenished."
)

# --- Data quality flags -----------------------------------------------------
flagged = item_df[item_df["balance_diff"].abs() > 0.5]
if not flagged.empty:
    with st.expander(f"⚠ {len(flagged)} week(s) with stock-balance inconsistencies"):
        st.dataframe(
            flagged[["week", "week_start", "opening_stock", "total_purchased",
                     "consumption", "closing_stock", "expected_closing", "balance_diff"]],
            use_container_width=True,
            hide_index=True,
        )

# --- Raw data table ----------------------------------------------------------
with st.expander("View weekly data table"):
    st.dataframe(
        item_df[["week", "week_start", "week_end", "opening_stock",
                 "total_purchased", "consumption", "closing_stock",
                 "purchase_surplus", "stock_change", "cumulative_surplus"]],
        use_container_width=True,
        hide_index=True,
    )
