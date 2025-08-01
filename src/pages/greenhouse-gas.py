import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

df_ghg = pd.read_csv("./src/dataset/greenhouse.csv")
import streamlit.components.v1 as components


# Configure page
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Inject CSS
st.markdown(
    """
    <style>
        footer, .stDeployButton {
            visibility: hidden;
            height: 0;
        }

        .spacer { height: 2.5rem; }

        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }

        h3 {
            margin-top: 0;
            margin-bottom: 0.5rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Spacer & title
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center;'>Greenhouse gas emission dashboard</h3>",
    unsafe_allow_html=True,
)
st.divider()

# Sample data
np.random.seed(42)
df = pd.DataFrame(
    {"Category": ["A", "B", "C", "D"], "Values": np.random.randint(10, 100, size=4)}
)
df_line = pd.DataFrame(np.random.randn(20, 3), columns=["A", "B", "C"])


# -- COMPONENTS using Plotly --
def kpi_and_line_tab():
    st.title("📊 Emission Insights Dashboard")

    # === Shared Filters ===
    measures = sorted(df_ghg["MEASURE"].dropna().unique())
    selected_measures = st.multiselect(
        "Select GHG Measures", measures, default=measures, key="combo_measures"
    )

    col_filters, col_chart = st.columns([1, 3])
    with col_filters:
        min_year = int(df_ghg["TIME_PERIOD"].min())
        max_year = int(df_ghg["TIME_PERIOD"].max())
        selected_range = st.slider(
            "Select Time Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="combo_time",
        )

        all_regions = sorted(df_ghg["Reference area"].dropna().unique())
        selected_region = st.selectbox("Select Region", all_regions, key="combo_region")

    # === Filtered Data ===
    df_filtered = df_ghg[
        (df_ghg["MEASURE"].isin(selected_measures))
        & (df_ghg["Reference area"] == selected_region)
        & (df_ghg["TIME_PERIOD"] >= selected_range[0])
        & (df_ghg["TIME_PERIOD"] <= selected_range[1])
    ]

    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
        return

    # === KPI Metrics ===
    total_emissions = df_filtered["OBS_VALUE"].sum()
    annual_emissions = (
        df_filtered.groupby("TIME_PERIOD")["OBS_VALUE"].sum().sort_index()
    )
    avg_annual = annual_emissions.mean()

    if len(annual_emissions) >= 2:
        pct_change = (
            (annual_emissions.iloc[-1] - annual_emissions.iloc[0])
            / annual_emissions.iloc[0]
        ) * 100
    else:
        pct_change = 0

    # === KPI Display ===
    st.subheader(f"KPI Summary for {selected_region}")
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Emissions", f"{total_emissions:,.2f}")
    col2.metric("📈 Avg Annual Emissions", f"{avg_annual:,.2f}")
    col3.metric("🔁 % Change", f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")

    # === Line Plot ===
    st.subheader("📉 Emissions Over Time")
    df_plot = (
        df_filtered.groupby(["TIME_PERIOD", "MEASURE"])["OBS_VALUE"]
        .sum()
        .reset_index()
        .pivot(index="TIME_PERIOD", columns="MEASURE", values="OBS_VALUE")
    )

    fig = px.line(
        df_plot,
        title=f"Greenhouse Gas Measures in {selected_region} Over Time",
        labels={"value": "Emissions", "TIME_PERIOD": "Year"},
    )
    st.plotly_chart(fig, use_container_width=True)


def pie_chart_tab():
    col_chart, col_filters = st.columns([2, 1])

    with col_filters:
        # Time range filter
        time_min = int(df_ghg["TIME_PERIOD"].min())
        time_max = int(df_ghg["TIME_PERIOD"].max())
        time_range = st.slider(
            "Select Time Range",
            min_value=time_min,
            max_value=time_max,
            value=(time_min, time_max),
            key="pie_time",
        )

        # Region filter (fix TypeError by converting to string and dropping NaNs)
        regions = sorted(df_ghg["Reference area"].dropna().astype(str).unique())
        selected_region = st.selectbox("Select Region", regions, key="pie_region")

        # Measure type filter
        category_filter = st.selectbox(
            "Emission Category", ["TOTAL", "LULUCF", "AGR"], key="pie_category"
        )

    # === Filter Data ===
    df_filtered = df_ghg[
        (df_ghg["Reference area"].astype(str) == selected_region)
        & (df_ghg["TIME_PERIOD"] >= time_range[0])
        & (df_ghg["TIME_PERIOD"] <= time_range[1])
    ]

    # Remove TOTGHG measures
    df_filtered = df_filtered[~df_filtered["MEASURE"].str.contains("TOTGHG", na=False)]

    # Apply category filter
    if category_filter == "TOTAL":
        df_filtered = df_filtered[
            ~df_filtered["MEASURE"].str.contains("LULUCF|AGR", na=False)
        ]
    elif category_filter == "LULUCF":
        df_filtered = df_filtered[
            df_filtered["MEASURE"].str.contains("LULUCF", na=False)
        ]
    elif category_filter == "AGR":
        df_filtered = df_filtered[df_filtered["MEASURE"].str.contains("AGR", na=False)]

    if df_filtered.empty:
        col_chart.warning("No data available for selected filters.")
        return

    df_grouped = df_filtered.groupby("MEASURE")["OBS_VALUE"].sum().reset_index()

    # No explode effect by default
    fig = go.Figure(
        go.Pie(
            labels=df_grouped["MEASURE"],
            values=df_grouped["OBS_VALUE"],
            hoverinfo="label+percent+value",
            textinfo="label+percent",
            hole=0,
            pull=[0] * len(df_grouped),  # no explode
        )
    )

    fig.update_layout(
        title=f"Emission Distribution in {selected_region} ({time_range[0]}–{time_range[1]}) – {category_filter}"
    )

    with col_chart:
        st.plotly_chart(fig, use_container_width=True)


def choropleth_tab():
    col1, col2 = st.columns([1, 3])

    with col1:
        # Clean TIME_PERIOD column: drop NaN or inf
        df_years = df_ghg[
            pd.to_numeric(df_ghg["TIME_PERIOD"], errors="coerce").notnull()
        ].copy()
        df_years["TIME_PERIOD"] = df_years["TIME_PERIOD"].astype(int)

        # Colormap selector
        cmap = st.selectbox(
            "Color map", ["Viridis", "Cividis", "Plasma", "Inferno"], index=0
        )

        # Year selector
        years = sorted(df_years["TIME_PERIOD"].unique())
        selected_year = st.selectbox("Select Year", years, index=len(years) - 1)

        # Measure filter
        available_measures = sorted(df_ghg["MEASURE"].dropna().unique())
        gas_type = st.selectbox("Select Emission Measure", available_measures)

    with col2:
        # Filter and aggregate data
        df_filtered = df_ghg[
            (df_ghg["TIME_PERIOD"] == selected_year)
            & (df_ghg["MEASURE"] == gas_type)
            & (
                ~df_ghg["Reference area"]
                .astype(str)
                .str.contains("World|EU|Total", na=False)
            )
        ]

        df_grouped = (
            df_filtered.groupby("Reference area")["OBS_VALUE"].sum().reset_index()
        )

        # Create choropleth map
        fig = px.choropleth(
            df_grouped,
            locations="Reference area",
            locationmode="country names",
            color="OBS_VALUE",
            color_continuous_scale=cmap.lower(),
            labels={"OBS_VALUE": "Emissions"},
            title=f"{gas_type} Emissions by Country ({selected_year})",
        )

        fig.update_geos(projection_type="natural earth")
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

        st.plotly_chart(fig, use_container_width=True)


# Tabs
tabs = st.tabs(["📈 KPI", "📊 Pie Chart", "🌀 Heatmap"])
with tabs[0]:
    kpi_and_line_tab()
with tabs[1]:
    pie_chart_tab()
with tabs[2]:
    choropleth_tab()

st.html("<h3>Greenhouse Gas Emissions vs Economic Activity</h3>")

components.html(
    """
        <!doctype html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <meta name="author" content="Le Phan" />
        <meta name="keywords" name="HTML, CSS, D3" />
        <meta name="description" name="Data Visualization" />

        <title>Lab 3.2P</title>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    </head>
    <body>
    <script>
    const w = 1000;
const h = 700;
const padding = 100;

const dataset = [
    [13, 40, 60],
    [16, 100, 180],
    [19, 340, 252],
    [10, 200, 166],
    [22, 400, 280],
    [21, 833, 200],
    [17, 500, 200],
];

const x_scale = d3
    .scaleLinear()
    .domain([
        d3.min(dataset, function (d) {
            return d[1];
        }),
        d3.max(dataset, function (d) {
            return d[1];
        }),
    ])
    .range([padding, w - padding]);

const y_scale = d3
    .scaleLinear()
    .domain([
        d3.min(dataset, function (d) {
            return d[2];
        }),
        d3.max(dataset, function (d) {
            return d[2];
        }),
    ])
    .range([h - padding, padding]);

const svg = d3.select("body").append("svg").attr("width", w).attr("height", h);

const x_axis = d3.axisBottom().ticks(dataset.length).scale(x_scale);
const y_axis = d3.axisLeft(y_scale).ticks(dataset.length);

svg.selectAll("circle")
    .data(dataset)
    .enter()
    .append("circle")
    .attr("cx", (d, i) => x_scale(d[1]))
    .attr("cy", (d, i) => y_scale(d[2]))
    .attr("r", (d) => d[0])
    .attr("fill", "steelblue");

svg.selectAll("text")
    .data(dataset)
    .enter()
    .append("text")
    .text((d) => {
        return d[1] + "," + d[2];
    })
    .attr("x", (d, i) => x_scale(d[1]) + 25)
    .attr("y", (d) => y_scale(d[2]));

svg.append("g")
    .attr("transform", "translate(0," + (h - padding) + ")")
    .call(x_axis);

svg.append("g")
    .attr("transform", `translate(${padding}, 0)`)
    .call(y_axis);

        </script>
    </body>
</html>

        """,
    height=750,
)

