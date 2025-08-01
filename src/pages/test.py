import streamlit.components.v1 as components

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
