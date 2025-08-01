import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

FILE_PATH = "./src/dataset/cleaned_data.csv"

STYLE_PATH = "./src/styles/nutrients.css"

st.set_page_config(
    page_title="Nutrients Balance Dashboard",
    page_icon=":seedling:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open(STYLE_PATH) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

class NutrientDashboard:
    def __init__(self):
        self.data = self.load_data()
        self.selected_areas = []
        self.year_range = []

        self.load_data()

        

    def load_data(self):
        try:
            data = pd.read_csv(FILE_PATH)
        except FileNotFoundError:
            st.error(f"Data file not found: {FILE_PATH}")
            st.stop()

        return data
    
    def render_nutrient_page(self):
        st.title(":seedling: OECD's Nutrients balance in Agriculture Dashboard")
        st.write("")
        st.write("")

        filtered_data = self.data[
            (self.data['TIME_PERIOD'] >= self.year_range[0]) & 
            (self.data['TIME_PERIOD'] <= self.year_range[1])
        ]

        if 'All areas' not in self.selected_areas:
            filtered_data = filtered_data[filtered_data['Reference area'].isin(self.selected_areas)]

        col1, col2, col3 = st.columns([0.38, 0.01, 0.61], gap="small")

        with col1:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                n_input = filtered_data[filtered_data['Measure'] == 'Nutrient inputs']
                n_input = n_input['OBS_VALUE'].sum() 
                st.metric("Nutrient Input", self.format_number(n_input))

            with sub_col2:
                n_output = filtered_data[filtered_data['Measure'] == 'Nutrient outputs']
                n_output = n_output['OBS_VALUE'].sum() 
                st.metric("Nutrient Output", self.format_number(n_output))
            
            with sub_col3:
                n_balance = filtered_data[filtered_data['Measure'] == 'Balance (inputs minus outputs)']
                n_balance = n_balance['OBS_VALUE'].sum() 
                st.metric("Nutrient Balance", self.format_number(n_balance))

            st.markdown("""
                <hr style="margin-top: 0.3rem; margin-bottom: 1.4rem; border: none; border-top: 2px solid #ccc;" />
                """, unsafe_allow_html=True)

            n_input = filtered_data[filtered_data['Measure'] == 'Nutrient inputs']
            self.render_nitphos("Nitrogen/Phosphorus in Nutrient Inputs", n_input)

            n_output = filtered_data[filtered_data['Measure'] == 'Nutrient outputs']
            self.render_nitphos("Nitrogen/Phosphorus in Nutrient Outputs", n_output)

            n_balance = filtered_data[filtered_data['Measure'] == 'Balance (inputs minus outputs)']
            self.render_nitphos("Nitrogen/Phosphorus in Nutrient Balance", n_balance)
        
        with col2:
            st.html(
                '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 28rem;
                            margin: auto;
                        }
                    </style>
                '''
            )
        
        with col3:
            st.sidebar.markdown("""
                    <hr style="margin-top: 0.3rem; margin-bottom: 0.3rem; border: none; border-top: 1px solid #ccc;" />
                    """, unsafe_allow_html=True)
            st.sidebar.subheader('Nutrient Trend Filter:')
            
            n_meas = st.sidebar.radio(key="n_meas", label="Nutrient Measure:",
                    options=["Input", "Output", "Balance"])
            
            n_type = st.sidebar.radio(key="n_type", label="Nutrient Type:",
                    options=["Nitrogen", "Phosphorus"])

            self.render_line_plot(n_meas, n_type, filtered_data)
                
        
        st.markdown("""
                <hr style="margin-top: 1rem; margin-bottom: 1rem; border: none; border-top: 2px solid #ccc;" />
                """, unsafe_allow_html=True)
        
        st.sidebar.markdown("""
                    <hr style="margin-top: 0.3rem; margin-bottom: 0.3rem; border: none; border-top: 1px solid #ccc;" />
                    """, unsafe_allow_html=True)
        
        st.sidebar.subheader("Output Category Filter")
        cat_type = st.sidebar.radio(key="cat_type", label="Nutrient Type:",
                options=["Nitrogen", "Phosphorus"])
        
        nutrient_output_cat = [
            "Cereals", "Dried pulses and beans", "Harvested crops", 
            "Harvested fodder crops", "Industrial crops", "Oil crops",
            "Other crops", "Forage"
        ]

        filtered_output_cat = filtered_data[filtered_data['Measure'].isin(nutrient_output_cat)]
        self.render_stacked_bar_plot(filtered_output_cat, cat_type)

        st.markdown("""
                <hr style="margin-top: 1rem; margin-bottom: 1.7rem; border: none; border-top: 2px solid #ccc;" />
                """, unsafe_allow_html=True)
        
        col4, col5, col6 = st.columns([0.6, 0.01, 0.39])

        with col4:
            filtered_input_cat = filtered_data[filtered_data['Measure'].isin(['Organic fertilisers (excluding livestock manure)', 'Inorganic fertilisers'])]
            self.render_hori_stacked_plot(filtered_input_cat)

        with col5:
            st.html(
                '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 28rem;
                            margin: auto;
                        }
                    </style>
                '''
            )

        with col6:
            st.sidebar.markdown("""
                    <hr style="margin-top: 0.3rem; margin-bottom: 0.3rem; border: none; border-top: 1px solid #ccc;" />
                    """, unsafe_allow_html=True)
        
            st.sidebar.subheader("Livestock Fertilisers Filter")
            live_type = st.sidebar.radio(key="live_type", label="Nutrient Type:",
                    options=["Nitrogen", "Phosphorus"])
            
            livestock_list = {
                'Cattle', 'Pigs', 'Poultry', 'Sheep and goats', 'Other livestock'
            }

            filtered_output_cat = filtered_data[filtered_data['Measure'].isin(livestock_list)]
            self.render_pie_plot(filtered_output_cat, live_type)
        
        st.markdown("""
            <hr style="margin-top: 1rem; margin-bottom: 1.7rem; border: none; border-top: 2px solid #ccc;" />
            """, unsafe_allow_html=True)
        
        choro_data = self.data[
            (self.data['TIME_PERIOD'] >= self.year_range[0]) & 
            (self.data['TIME_PERIOD'] <= self.year_range[1])
        ]
        bal_per_hec = choro_data[choro_data['Measure'] == 'Balance per hectare']
        self.render_choropleth_map(bal_per_hec)
        
    def render_choropleth_map(self, data):
        grouped = data.groupby(['REF_AREA'], as_index=False)['OBS_VALUE'].sum()

        fig = px.choropleth(
            grouped,
            locations='REF_AREA',
            locationmode='ISO-3',
            color='OBS_VALUE',
            color_continuous_scale='sunsetdark',
            labels={'OBS_VALUE': 'Kilogramme'},
            title='Choropleth Map of Nutrient Balance per hectare'
        )

        fig.update_layout(
            height=800,
            geo=dict(showframe=False, showcoastlines=False),
        )

        st.plotly_chart(fig, use_container_width=True)
            
        
    def render_hori_stacked_plot(self, data):
        grouped = data.groupby(['Reference area', 'Measure'], as_index=False)['OBS_VALUE'].sum()
        total = grouped.groupby('Reference area', as_index=False)['OBS_VALUE'].sum()
        total = total.rename(columns={'OBS_VALUE': 'Total'})

        grouped = grouped.merge(total, on='Reference area')

        grouped['Proportion'] = grouped['OBS_VALUE'] / grouped['Total']
        

        fig = px.bar(
            grouped,
            x='Proportion',
            y='Reference area',
            color='Measure',
            orientation='h',
            hover_data=['OBS_VALUE'],
            title=f'Organic / Inorganic Fertilisers Proportional Composition in {self.year_range[0]} - {self.year_range[1]}',
            color_discrete_map={
                'Organic': 'green',
                'Inorganic': 'gray'
            }
        )

        fig.update_layout(
            barmode='stack',
            xaxis_tickformat='.0%',
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(
                orientation="v", 
                x=1,              
                y=-0.5,             
                xanchor="right",   
                yanchor="bottom"   
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_pie_plot(self, data, live_type):
        data = data[data['Nutrients'] == live_type]
        grouped = data.groupby('Measure', as_index=False)['OBS_VALUE'].sum()

        fig = px.pie(grouped, names='Measure', values='OBS_VALUE', hole=0.5)
        fig.update_layout(
            title=f"Nutrient Livestock Input contriubtion in {self.year_range[0]} - {self.year_range[1]}",
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(
                orientation="v",   
                x=1,               
                y=0,              
                xanchor="right",   
                yanchor="bottom"   
            ))

        fig.update_traces(
            domain=dict(x=[0.2, 0.8], y=[0.2, 0.8]),
            textinfo='percent+label',  # show % and label on chart
            hovertemplate='%{label}: %{value:,} (%{percent})<extra></extra>',
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def render_stacked_bar_plot(self, data, cat_type):
        data = data[data['Nutrients'] == cat_type]
        grouped = data.groupby(['Reference area', 'Measure'], as_index=False)['OBS_VALUE'].sum()

        fig = px.bar(
            grouped,
            x = 'Reference area',
            y = 'OBS_VALUE',
            color = 'Measure',
            barmode = 'stack',
            labels={'OBS_VALUE': 'Tonnes'},
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )

        fig.update_layout(title=f"Nutrient Output contributions across Areas in {self.year_range[0]} - {self.year_range[1]}", 
                          xaxis_title="Area", 
                          yaxis_title="Tonnes",
                          margin=dict(l=0, r=0, t=50, b=0))
        
        st.plotly_chart(fig, use_container_width=True)

    def render_line_plot(self, n_meas, n_type, data):
        if n_meas == 'Input':
            data = data[data['Measure'] == 'Nutrient inputs']
        elif n_meas == 'Output':
            data = data[data['Measure'] == 'Nutrient outputs']
        elif n_meas == 'Balance':
            data = data[data['Measure'] == 'Balance (inputs minus outputs)']

        data = data[data['Nutrients'] == n_type]

        fig = px.line(
            data,
            x ='TIME_PERIOD',
            y ='OBS_VALUE',
            color = 'Reference area',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title=f"{n_type} {n_meas} Trend in {self.year_range[0]} - {self.year_range[1]}",
            labels={'OBS_VALUE': 'Tonnes', 'TIME_PERIOD': 'Year', 'area': 'Areas'}
        )

        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), legend_title_text='Area')
        fig.update_traces(mode="lines+markers")

        st.plotly_chart(fig, use_container_width=True)

    def format_number(self, num):
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)

    def render_nitphos(self, name, data):
        nit_in = data[data['Nutrients'] == 'Nitrogen']
        phos_in = data[data['Nutrients'] == 'Phosphorus']
        nit_in = nit_in['OBS_VALUE'].sum() 
        phos_in = phos_in['OBS_VALUE'].sum()

        self.draw_proportion_bar(name, nit_in, phos_in)

    def draw_proportion_bar(self, name, value1, value2):
        total = value1 + value2
        # Create the figure
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=["Proportion"],  # y is used because we're rotating it to horizontal
            x=[value1],
            name="Nitrogen",
            orientation='h',
            marker=dict(color='#A7C1A8'),
            text=[f"{(value1/total)*100:.1f}%"],
            textposition='inside'
        ))

        fig.add_trace(go.Bar(
            y=["Proportion"],
            x=[value2],
            name="Phosphorus",
            orientation='h',
            marker=dict(color='#FFF9BD'),
            text=[f"{(value2/total)*100:.1f}%"],
            textposition='inside'
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=f"<span style='font-weight:500'>{name}</span>",
            ),
            barmode='stack',
            height=90,
            showlegend=True,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
        )

        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            

    def run(self):
        with st.sidebar:
            st.subheader("Dashboard Main Filter:")
            area = ['All areas'] + sorted(self.data['Reference area'].unique().tolist())
            self.selected_areas = st.multiselect(
                "Select Areas:",
                options=area,
                default=['All areas'],
                help="Choose area(s) or select all for global view"
            )

            min_year, max_year = int(self.data['TIME_PERIOD'].min()), int(self.data['TIME_PERIOD'].max())
            self.year_range = st.slider(
                "Year Range:",
                min_year, max_year,
                (min_year, max_year),
                help="Filter data by year range"
            )
        self.render_nutrient_page()



def main():
    dashboard = NutrientDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()


        



