import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="🌾 Global Land Use Analysis Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme
st.markdown("""
<style>
    .stApp {
        background-color: white;
        color: black;
    }
    .stSidebar {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .education-box {
        background-color: #e8f5e8;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess land data"""
    try:
        df = pd.read_csv('dataset/land_data.csv')
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        df['Actual area (ha)'] = pd.to_numeric(df['Actual area (ha)'], errors='coerce')
        
        # Clean up land types (remove any malformed entries)
        df = df[df['Types of Land'].notna()]
        df = df[~df['Types of Land'].isin(['Types of Land', 'HA'])]
        
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found. Please ensure 'data/land_data.csv' exists.")
        return pd.DataFrame()

def create_educational_note(title, content):
    """Create educational information boxes"""
    st.markdown(f"""
    <div class="education-box">
        <h4>🌱 {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def filter_data(df, countries, years, land_types):
    """Apply filters to the dataset"""
    filtered_df = df.copy()
    
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    if years:
        filtered_df = filtered_df[(filtered_df['Time'] >= years[0]) & (filtered_df['Time'] <= years[1])]
    if land_types:
        filtered_df = filtered_df[filtered_df['Types of Land'].isin(land_types)]
    
    return filtered_df

def create_stacked_area_chart(df):
    """Create stacked area chart for land composition over time"""
    if df.empty:
        return go.Figure()
    
    # Aggregate data by land type and time
    area_data = df.groupby(['Time', 'Types of Land'])['Actual area (ha)'].sum().reset_index()
    area_data = area_data.pivot(index='Time', columns='Types of Land', values='Actual area (ha)').fillna(0)
    
    fig = go.Figure()
    
    # Add area traces for each land type
    for land_type in area_data.columns:
        fig.add_trace(go.Scatter(
            x=area_data.index,
            y=area_data[land_type],
            mode='lines',
            stackgroup='one',
            name=land_type,
            line=dict(width=0.5),
            fillcolor=px.colors.qualitative.Set3[len(fig.data) % len(px.colors.qualitative.Set3)]
        ))
    
    fig.update_layout(
        title='🌾 Land Use Composition Over Time (Stacked Area)',
        xaxis_title='Year',
        yaxis_title='Area (Hectares)',
        hovermode='x unified',
        height=500,
        showlegend=True,
        font=dict(size=12)
    )
    
    return fig

def create_temporal_trends_chart(df):
    """Create line chart for temporal trends"""
    if df.empty:
        return go.Figure()
    
    # Aggregate data by country, land type, and time
    trend_data = df.groupby(['Country', 'Types of Land', 'Time'])['Actual area (ha)'].sum().reset_index()
    
    fig = px.line(
        trend_data,
        x='Time',
        y='Actual area (ha)',
        color='Types of Land',
        facet_col='Country',
        facet_col_wrap=3,
        title='📈 Land Use Trends by Country and Type',
        labels={'Actual area (ha)': 'Area (Hectares)', 'Time': 'Year'}
    )
    
    fig.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=5))
    fig.update_layout(height=600, font=dict(size=10))
    
    return fig

def create_country_comparison_chart(df):
    """Create bar chart for country comparisons"""
    if df.empty:
        return go.Figure()
    
    # Get average land area by country and type
    country_data = df.groupby(['Country', 'Types of Land'])['Actual area (ha)'].mean().reset_index()
    
    fig = px.bar(
        country_data,
        x='Country',
        y='Actual area (ha)',
        color='Types of Land',
        title='🏆 Average Land Use by Country and Type',
        labels={'Actual area (ha)': 'Average Area (Hectares)'},
        barmode='group'
    )
    
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45,
        showlegend=True,
        font=dict(size=12)
    )
    
    return fig

def create_land_composition_pie_chart(df):
    """Create pie chart for land type proportions"""
    if df.empty:
        return go.Figure()
    
    # Aggregate total area by land type
    pie_data = df.groupby('Types of Land')['Actual area (ha)'].sum().reset_index()
    pie_data = pie_data[pie_data['Actual area (ha)'] > 0]  # Remove zero values
    
    fig = px.pie(
        pie_data,
        values='Actual area (ha)',
        names='Types of Land',
        title='🥧 Global Land Use Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500, font=dict(size=12))
    
    return fig

def create_heatmap_chart(df):
    """Create heatmap for country vs land type analysis"""
    if df.empty:
        return go.Figure()
    
    # Create pivot table for heatmap
    heatmap_data = df.groupby(['Country', 'Types of Land'])['Actual area (ha)'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Country', columns='Types of Land', values='Actual area (ha)').fillna(0)
    
    # Limit to top 20 countries with most total agricultural land
    country_totals = heatmap_pivot.sum(axis=1).sort_values(ascending=False).head(20)
    heatmap_pivot = heatmap_pivot.loc[country_totals.index]
    
    fig = px.imshow(
        heatmap_pivot,
        title='🔥 Land Use Intensity Heatmap (Country vs Land Type)',
        labels=dict(x="Land Type", y="Country", color="Area (ha)"),
        color_continuous_scale='Greens',
        aspect='auto'
    )
    
    fig.update_layout(height=600, font=dict(size=10))
    
    return fig

def create_map_chart(df):
    """Create world map showing total agricultural land by country"""
    if df.empty:
        return go.Figure()
    
    # Aggregate total land area by country
    map_data = df.groupby('Country')['Actual area (ha)'].sum().reset_index()
    map_data = map_data[map_data['Actual area (ha)'] > 0]
    
    # Map country names to ISO codes for better mapping
    country_mapping = {
        'United States': 'USA',
        'United Kingdom': 'GBR',
        'China (People\'s Republic of)': 'CHN',
        'Korea': 'KOR',
        'Türkiye': 'TUR',
        'European Union (27 countries from 01/02/2020)': None,  # Skip EU aggregate
        'European Union (28 countries)': None,  # Skip EU aggregate
    }
    
    # Apply country name mapping
    map_data['Country_Clean'] = map_data['Country'].replace(country_mapping)
    map_data = map_data[map_data['Country_Clean'].notna()]
    
    fig = px.choropleth(
        map_data,
        locations='Country_Clean',
        color='Actual area (ha)',
        hover_name='Country',
        color_continuous_scale='Greens',
        title='🗺️ Global Agricultural Land Distribution',
        labels={'Actual area (ha)': 'Total Area (Hectares)'}
    )
    
    fig.update_layout(height=500, font=dict(size=12))
    
    return fig

def create_top_countries_chart(df):
    """Create horizontal bar chart of top countries by total agricultural land"""
    if df.empty:
        return go.Figure()
    
    # Get top 15 countries by total agricultural land
    top_countries = df.groupby('Country')['Actual area (ha)'].sum().sort_values(ascending=True).tail(15)
    
    fig = px.bar(
        x=top_countries.values,
        y=top_countries.index,
        orientation='h',
        title='🏆 Top 15 Countries by Total Agricultural Land',
        labels={'x': 'Total Area (Hectares)', 'y': 'Country'},
        color=top_countries.values,
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(height=600, font=dict(size=12))
    
    return fig

# Main application
def main():
    st.title("🌾 Global Land Use Analysis Dashboard")
    st.markdown("### *Understanding Agricultural Land Distribution and Composition Across Countries*")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Educational introduction
    create_educational_note(
        "About This Dashboard",
        "This dashboard analyzes global agricultural land use patterns. It covers different types of agricultural land including arable land, permanent crops, irrigation areas, organic farming, and more. Use the filters to explore land use composition and compare patterns across countries."
    )
    
    # Sidebar filters
    st.sidebar.header("🎛️ Dashboard Filters")
    
    # Get unique values for filters
    countries = sorted(df['Country'].unique())
    min_year, max_year = int(df['Time'].min()), int(df['Time'].max())
    land_types = sorted(df['Types of Land'].unique())
    
    # Filter controls
    selected_countries = st.sidebar.multiselect(
        "Select Countries", 
        countries, 
        default=countries[:8],
        help="Choose countries to analyze"
    )
    
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_year, max_year,
        (min_year, max_year),
        help="Filter data by time period"
    )
    
    selected_land_types = st.sidebar.multiselect(
        "Select Land Types",
        land_types,
        default=land_types,
        help="Choose specific types of agricultural land"
    )
    
    # Apply filters
    filtered_df = filter_data(df, selected_countries, selected_years, selected_land_types)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_countries = len(filtered_df['Country'].unique()) if not filtered_df.empty else 0
        st.metric("Countries Analyzed", total_countries)
    
    with col2:
        year_span = selected_years[1] - selected_years[0] + 1
        st.metric("Years Covered", year_span)
    
    with col3:
        total_area = filtered_df['Actual area (ha)'].sum() / 1_000_000 if not filtered_df.empty else 0
        st.metric("Total Area", f"{total_area:.1f}M ha")
    
    with col4:
        land_type_count = len(filtered_df['Types of Land'].unique()) if not filtered_df.empty else 0
        st.metric("Land Types", land_type_count)
    
    # Main visualizations
    st.markdown("---")
    
    # Row 1: Land Composition Analysis
    st.subheader("🌾 Land Use Composition Analysis")
    
    tab1, tab2 = st.tabs(["📊 Stacked Area Chart", "🥧 Composition Breakdown"])
    
    with tab1:
        st.plotly_chart(create_stacked_area_chart(filtered_df), use_container_width=True)
        create_educational_note(
            "Land Composition Over Time",
            "This stacked area chart shows how different types of agricultural land have evolved over time. Each colored area represents a different land type, and the total height shows the overall agricultural land area."
        )
    
    with tab2:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.plotly_chart(create_land_composition_pie_chart(filtered_df), use_container_width=True)
        with col2:
            create_educational_note(
                "Land Type Distribution",
                "This pie chart shows the relative proportions of different agricultural land types. Arable land is typically used for crop production, while permanent crops include orchards and vineyards. Permanent pasture is used for livestock grazing."
            )
    
    # Row 2: Temporal Trends
    st.subheader("📈 Temporal Trends Analysis")
    st.plotly_chart(create_temporal_trends_chart(filtered_df), use_container_width=True)
    
    create_educational_note(
        "Understanding Trends",
        "These line charts show how land use has changed over time for each country and land type. Look for increasing trends (agricultural expansion), decreasing trends (urbanization or land conversion), or stable patterns (sustainable land management)."
    )
    
    # Row 3: Country Comparisons
    st.subheader("🏆 Country Comparison Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_country_comparison_chart(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_top_countries_chart(filtered_df), use_container_width=True)
    
    # Row 4: Geographic and Advanced Analysis
    st.subheader("🗺️ Geographic and Pattern Analysis")
    
    tab1, tab2 = st.tabs(["🗺️ World Map", "🔥 Intensity Heatmap"])
    
    with tab1:
        st.plotly_chart(create_map_chart(filtered_df), use_container_width=True)
        create_educational_note(
            "Global Distribution",
            "This world map shows the geographic distribution of agricultural land. Darker colors indicate countries with larger agricultural land areas. This helps identify major agricultural producers and regions."
        )
    
    with tab2:
        st.plotly_chart(create_heatmap_chart(filtered_df), use_container_width=True)
        create_educational_note(
            "Pattern Analysis",
            "This heatmap reveals patterns between countries and land types. It helps identify which countries specialize in certain types of agriculture and reveals regional agricultural patterns."
        )
    
    # Data Explorer Section
    st.markdown("---")
    st.subheader("📊 Data Explorer")
    
    if st.checkbox("Show filtered data"):
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name="filtered_land_data.csv",
            mime="text/csv"
        )
    
    # Footer with additional information
    st.markdown("---")
    st.markdown("""
    ### 📚 Additional Information
    
    **Data Source**: OECD Agricultural Land Use Data  
    **Measurement**: Area in hectares for different agricultural land types  
    **Update Frequency**: Annual data where available  
    
    **Key Land Types**:
    - **Arable Land**: Land suitable for crop production
    - **Permanent Crops**: Orchards, vineyards, tree plantations
    - **Irrigation Area**: Land equipped with irrigation systems
    - **Organic Farming**: Certified organic agricultural land
    - **Permanent Pasture**: Land used for livestock grazing
    - **Total Agricultural Land**: Sum of all agricultural land types
    """)

if __name__ == "__main__":
    main()
