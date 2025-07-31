import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="🌍 Global Erosion Analysis Dashboard",
    page_icon="🌍",
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
        background-color: #e8f4fd;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess erosion data"""
    try:
        df = pd.read_csv('data/erosion_data.csv')
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found. Please ensure 'data/erosion_data.csv' exists.")
        return pd.DataFrame()

def create_educational_note(title, content):
    """Create educational information boxes"""
    st.markdown(f"""
    <div class="education-box">
        <h4>📚 {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def filter_data(df, countries, years, erosion_types, severity_levels):
    """Apply filters to the dataset"""
    filtered_df = df.copy()
    
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    if years:
        filtered_df = filtered_df[(filtered_df['Time'] >= years[0]) & (filtered_df['Time'] <= years[1])]
    if erosion_types:
        filtered_df = filtered_df[filtered_df['Types of Erosion'].isin(erosion_types)]
    if severity_levels:
        filtered_df = filtered_df[filtered_df['EROSION_LEVEL'].isin(severity_levels)]
    
    return filtered_df

def create_time_series_chart(df):
    """Create interactive time series chart"""
    if df.empty:
        return go.Figure()
    
    # Aggregate data for total erosion by country and year
    total_data = df[df['EROSION_LEVEL'] == '_T'].groupby(['Country', 'Time', 'Types of Erosion'])['OBS_VALUE'].sum().reset_index()
    
    fig = px.line(
        total_data, 
        x='Time', 
        y='OBS_VALUE',
        color='Country',
        facet_col='Types of Erosion',
        title='📈 Erosion Trends Over Time (Total Erosion %)',
        labels={'OBS_VALUE': 'Percentage of Agricultural Land (%)', 'Time': 'Year'}
    )
    
    fig.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=6))
    fig.update_layout(
        height=500,
        showlegend=True,
        hovermode='x unified',
        font=dict(size=12)
    )
    
    return fig

def create_erosion_comparison_chart(df):
    """Create wind vs water erosion comparison"""
    if df.empty:
        return go.Figure()
    
    # Get total erosion data
    total_data = df[df['EROSION_LEVEL'] == '_T'].groupby(['Country', 'Types of Erosion'])['OBS_VALUE'].mean().reset_index()
    
    fig = px.bar(
        total_data,
        x='Country',
        y='OBS_VALUE',
        color='Types of Erosion',
        title='🌪️ Wind vs Water Erosion Comparison (Average %)',
        labels={'OBS_VALUE': 'Average Percentage of Agricultural Land (%)'},
        barmode='group'
    )
    
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45,
        showlegend=True,
        font=dict(size=12)
    )
    
    return fig

def create_severity_breakdown_chart(df):
    """Create severity level breakdown chart"""
    if df.empty:
        return go.Figure()
    
    # Filter out total values and aggregate by severity
    severity_data = df[~df['EROSION_LEVEL'].isin(['_T', 'TOL'])].groupby(['EROSION_LEVEL', 'Erosion risk level'])['OBS_VALUE'].mean().reset_index()
    
    # Create a mapping for better labels
    severity_mapping = {
        'LW': 'Low',
        'MD': 'Moderate', 
        'HG': 'High',
        'SV': 'Severe'
    }
    
    severity_data['Severity_Label'] = severity_data['EROSION_LEVEL'].map(severity_mapping)
    
    fig = px.pie(
        severity_data,
        values='OBS_VALUE',
        names='Severity_Label',
        title='🎯 Global Erosion Severity Distribution',
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500, font=dict(size=12))
    
    return fig

def create_country_ranking_chart(df):
    """Create country ranking chart"""
    if df.empty:
        return go.Figure()
    
    # Get average total erosion by country
    country_avg = df[df['EROSION_LEVEL'] == '_T'].groupby('Country')['OBS_VALUE'].mean().reset_index()
    country_avg = country_avg.sort_values('OBS_VALUE', ascending=True).tail(15)  # Top 15 countries
    
    fig = px.bar(
        country_avg,
        x='OBS_VALUE',
        y='Country',
        orientation='h',
        title='🏆 Top 15 Countries by Average Total Erosion',
        labels={'OBS_VALUE': 'Average Percentage of Agricultural Land (%)'},
        color='OBS_VALUE',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(height=600, font=dict(size=12))
    
    return fig



# Main application
def main():
    st.title("🌍 Global Erosion Analysis Dashboard")
    st.markdown("### *Understanding Water and Wind Erosion Patterns Across Countries and Time*")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Educational introduction
    create_educational_note(
        "About This Dashboard",
        "This dashboard analyzes global erosion patterns using OECD data. Erosion is measured as the percentage of agricultural land affected by wind and water erosion at different severity levels. Use the filters below to explore specific patterns and trends."
    )
    
    # Sidebar filters
    st.sidebar.header("🎛️ Dashboard Filters")
    
    # Get unique values for filters
    countries = sorted(df['Country'].unique())
    min_year, max_year = int(df['Time'].min()), int(df['Time'].max())
    erosion_types = df['Types of Erosion'].unique()
    severity_levels = df['EROSION_LEVEL'].unique()
    
    # Filter controls
    selected_countries = st.sidebar.multiselect(
        "Select Countries", 
        countries, 
        default=countries[:5],
        help="Choose countries to analyze"
    )
    
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_year, max_year,
        (min_year, max_year),
        help="Filter data by time period"
    )
    
    selected_erosion_types = st.sidebar.multiselect(
        "Select Erosion Types",
        erosion_types,
        default=erosion_types,
        help="Choose between wind and water erosion"
    )
    
    selected_severity = st.sidebar.multiselect(
        "Select Severity Levels",
        severity_levels,
        default=severity_levels,
        help="Filter by erosion severity (LW=Low, MD=Moderate, HG=High, SV=Severe, _T=Total)"
    )
    
    # Apply filters
    filtered_df = filter_data(df, selected_countries, selected_years, selected_erosion_types, selected_severity)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_countries = len(filtered_df['Country'].unique()) if not filtered_df.empty else 0
        st.metric("Countries Analyzed", total_countries)
    
    with col2:
        year_span = selected_years[1] - selected_years[0] + 1
        st.metric("Years Covered", year_span)
    
    with col3:
        avg_erosion = filtered_df[filtered_df['EROSION_LEVEL'] == '_T']['OBS_VALUE'].mean() if not filtered_df.empty else 0
        st.metric("Average Total Erosion", f"{avg_erosion:.1f}%")
    
    with col4:
        total_records = len(filtered_df)
        st.metric("Data Points", total_records)
    
    # Main visualizations
    st.markdown("---")
    
    # Row 1: Time Series Analysis
    st.subheader("📈 Temporal Analysis")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(create_time_series_chart(filtered_df), use_container_width=True)
    
    with col2:
        create_educational_note(
            "Temporal Trends",
            "This chart shows how erosion patterns change over time. Look for increasing or decreasing trends, seasonal patterns, and sudden changes that might indicate policy interventions or climate events."
        )
    
    # Row 2: Erosion Type Comparison
    st.subheader("🌪️ Wind vs Water Erosion Analysis")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(create_erosion_comparison_chart(filtered_df), use_container_width=True)
    
    with col2:
        create_educational_note(
            "Erosion Types",
            "Wind erosion typically occurs in arid regions with strong winds and sparse vegetation. Water erosion is more common in areas with heavy rainfall and steep slopes. Compare how different countries are affected by each type."
        )
    
    # Row 3: Severity and Country Analysis
    st.subheader("🎯 Severity Distribution & Country Rankings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_severity_breakdown_chart(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_country_ranking_chart(filtered_df), use_container_width=True)
    
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
            file_name="filtered_erosion_data.csv",
            mime="text/csv"
        )
    
    # Footer with additional information
    st.markdown("---")
    st.markdown("""
    ### 📚 Additional Information
    
    **Data Source**: OECD Environmental Data  
    **Measurement**: Percentage of agricultural land area affected by erosion  
    **Update Frequency**: Varies by country and indicator  
    
    **Key Definitions**:
    - **Low (LW)**: Minimal erosion impact
    - **Moderate (MD)**: Some erosion but manageable
    - **High (HG)**: Significant erosion requiring intervention
    - **Severe (SV)**: Critical erosion levels
    - **Tolerable (TOL)**: Within acceptable limits
    - **Total (_T)**: Overall erosion percentage
    """)

if __name__ == "__main__":
    main()