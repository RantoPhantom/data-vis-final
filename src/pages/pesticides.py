import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json

st.set_page_config(
    page_title="Pesticides Sales Dashboard",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FILE_PATH = "./src/dataset/cleaned_data.csv"

class PesticidesDashboard:
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
    
    def render_pesticides_page(self):
        st.title("🐛 OECD's Pesticides Sales Dashboard (Make with D3 JS)")
        st.write("")
        st.write("")

        filtered_data = self.data[
            (self.data['TIME_PERIOD'] >= self.year_range[0]) & 
            (self.data['TIME_PERIOD'] <= self.year_range[1])
        ]

        if 'All areas' not in self.selected_areas:
            filtered_data = filtered_data[filtered_data['Reference area'].isin(self.selected_areas)]

        st.subheader(f"Pesticides Sales Ranking in {self.year_range[0]} - {self.year_range[1]} (Tonnes)")
        self.render_d3_bar_chart(filtered_data)

        st.subheader(f"Pesticides Sales Trend in {self.year_range[0]} - {self.year_range[1]} (Tonnes)")
        self.render_d3_line(filtered_data)

        return
    
    def render_d3_line(self, data):
        pesticides_list = ["Sales of fungicides", "Sales of herbicides", "Sales of insecticides", "Sales of other pesticides"]
        data = data[data["Measure"].isin(pesticides_list)]

        data = data.groupby(["Measure", "TIME_PERIOD"], as_index=False)["OBS_VALUE"].sum()
        data = data.sort_values(["Measure", "TIME_PERIOD"])

        data_json = data.to_json(orient='records')

        html_code = f"""
            <div id="chart" style="text-align:center;"></div>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script>

                const data = {data_json};
                data.forEach(d => {{
                    d.TIME_PERIOD = +d.TIME_PERIOD;
                    d.OBS_VALUE = +d.OBS_VALUE;
                }});

                
                const margin = {{top: 40, right: 150, bottom: 50, left: 60}}  
                const width = 1000 - margin.left - margin.right
                const height = 400 - margin.top - margin.bottom;

                    
                const svg = d3.select("#chart")
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .style("display", "block")
                    .style("margin", "0 auto")
                    .append("g")
                    .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

                
                const x = d3.scaleLinear()
                    .domain(d3.extent(data, d => d.TIME_PERIOD))
                    .range([0, width]);

                const y = d3.scaleLinear()
                    .domain([0, d3.max(data, d => d.OBS_VALUE)]).nice()
                    .range([height, 0]);
                

                svg.append("g")
                .attr("transform", `translate(0,${{height}})`)
                .call(d3.axisBottom(x).tickFormat(d3.format("d")));

                svg.append("g").call(d3.axisLeft(y));


                const measures = Array.from(
                    d3.group(data, d => d.Measure),
                    ([key, values]) => ({{
                        key,
                        values: values.sort((a, b) => a.TIME_PERIOD - b.TIME_PERIOD)
                    }})
                );


                const color = d3.scaleOrdinal(d3.schemeCategory10)
                    .domain(measures.map(d => d.key));


                const line = d3.line()
                    .x(d => x(d.TIME_PERIOD))
                    .y(d => y(d.OBS_VALUE));


                measures.forEach(measure => {{
                    svg.append("path")
                        .datum(measure.values)
                        .attr("fill", "none")
                        .attr("stroke", color(measure.key))
                        .attr("stroke-width", 2)
                        .attr("d", line);
                }});

                const legend = svg.append("g")
                    .attr("transform", `translate(${{width + 20}}, 0)`); // Position legend to the right

                measures.forEach((measure, i) => {{
                    const legendRow = legend.append("g")
                        .attr("transform", `translate(0, ${{i * 20}})`);

                    legendRow.append("rect")
                    .attr("width", 10)
                    .attr("height", 10)
                    .attr("fill", color(measure.key));

                    legendRow.append("text")
                        .attr("x", 15)
                        .attr("y", 10)
                        .text(measure.key)
                        .style("font-size", "12px")
                        .attr("alignment-baseline", "middle");
                }});


                const tooltip = d3.select("#chart")
                    .append("div")
                    .style("position", "absolute")
                    .style("padding", "6px 10px")
                    .style("background", "white")
                    .style("border", "1px solid #ccc")
                    .style("border-radius", "4px")
                    .style("pointer-events", "none")
                    .style("font-size", "12px")
                    .style("box-shadow", "0px 0px 5px rgba(0,0,0,0.2)")
                    .style("display", "none");


                measures.forEach(measure => {{
                    svg.selectAll(`.dot-${{measure.key}}`)
                        .data(measure.values)
                        .enter()
                        .append("circle")
                        .attr("cx", d => x(d.TIME_PERIOD))
                        .attr("cy", d => y(d.OBS_VALUE))
                        .attr("r", 4)
                        .attr("fill", color(measure.key))
                        .on("mouseover", (event, d) => {{
                            tooltip
                                .style("left", (event.pageX + 10) + "px")
                                .style("top", (event.pageY - 30) + "px")
                                .style("display", "block")
                                .html(`<strong>${{d.Measure}}</strong><br>Year: ${{d.TIME_PERIOD}}<br>Value: ${{d.OBS_VALUE}}`);
                        }})
                        .on("mouseout", () => {{
                            tooltip.style("display", "none");
                        }});
                }});
            </script>
            """
        components.html(html_code, height=480)
        return

    
    def render_d3_bar_chart(self, data):
        pesticides_list = ["Sales of fungicides", "Sales of herbicides", "Sales of insecticides", "Sales of other pesticides"]
        data = data[data["Measure"].isin(pesticides_list)]

        grouped = data.groupby(['Measure'], as_index=False)['OBS_VALUE'].sum()

        data_json = json.dumps(grouped.to_dict(orient="records"))

        html_code = f"""
            <script src="https://d3js.org/d3.v7.min.js"></script>

            <div id="chart" style="text-align: center;"></div>
            <div id="tooltip" style="
                position: absolute;
                background: white;
                border: 1px solid #ccc;
                padding: 6px 10px;
                font-size: 12px;
                border-radius: 4px;
                pointer-events: none;
                display: none;
                box-shadow: 0px 0px 5px rgba(0,0,0,0.2);
                z-index: 10;
            "></div>

            <script>
                const data = {data_json};

                const width = 800;
                const height = 300;
                const margin = {{ top: 20, right: 20, bottom: 30, left: 100 }};

                const svg = d3.select("#chart")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);

                const x = d3.scaleBand()
                    .domain(data.map(d => d.Measure))
                    .range([margin.left, width - margin.right])
                    .padding(0.1);

                const y = d3.scaleLinear()
                    .domain([0, d3.max(data, d => d.OBS_VALUE)])
                    .nice()
                    .range([height - margin.bottom, margin.top]);

                const tooltip = d3.select("#tooltip");

                svg.selectAll("rect")
                    .data(data)
                    .enter()
                    .append("rect")
                    .attr("x", d => x(d.Measure))
                    .attr("y", d => y(d.OBS_VALUE))
                    .attr("width", x.bandwidth())
                    .attr("height", d => height - margin.bottom - y(d.OBS_VALUE))
                    .attr("fill", "steelblue")
                    .on("mouseover", (event, d) => {{
                        tooltip
                            .style("display", "block")
                            .html(`<strong>${{d.Measure}}</strong><br/>${{d.OBS_VALUE}} Tonnes`);
                    }})
                    .on("mousemove", (event) => {{
                        tooltip
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 30) + "px");
                    }})
                    .on("mouseout", () => {{
                        tooltip.style("display", "none");
                    }});

                svg.append("g")
                    .attr("transform", `translate(0,${{height - margin.bottom}})`)
                    .call(d3.axisBottom(x));

                svg.append("g")
                    .attr("transform", `translate(${{margin.left}},0)`)
                    .call(d3.axisLeft(y));

                svg.append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("x", -height / 2)
                    .attr("y", margin.left - 50)
                    .attr("dy", "-2em")
                    .style("text-anchor", "middle")
                    .style("font-size", "12px")
                    .text("Tonnes");
            </script>
            """

        components.html(html_code, height=350)
        return
    
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

        self.render_pesticides_page()



def main():
    dashboard = PesticidesDashboard()
    dashboard.run()
    
        

if __name__ == "__main__":
    main()    



