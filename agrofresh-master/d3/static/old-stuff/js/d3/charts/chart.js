import { getUUID } from '/static/comms/js/jsobject.js';
// https://bost.ocks.org/mike/chart/
// https://bost.ocks.org/mike/chart/time-series-chart.js

const setPos = (selection, {x, y}) => selection
    .attr("x", x)
    .attr("y", y);

const setSize = (selection, {width, height}) => selection
    .attr("width", width)
    .attr("height", height);


export function timeSeriesChart() {
    // Defaults
    let margin = {top: 20, right: 20, bottom: 20, left: 20},
        width  = 720,
        height = 80,
        xValue = d => d.x,
        yValue = d => d.y,
        xScale = d3.scaleTime(),
        yScale = d3.scaleLinear(),
        xAxis  = d3.axisBottom(xScale).tickPadding(15),
        yAxis  = d3.axisLeft(yScale).tickPadding(15),
        drawFn = _ => {};

    function chart(selection) {
        selection.each((data, i, nodes) => {
            if (!data) {
                console.error("no data bound to selection", selection);
                return;
            }

            const parent = nodes[i];
            width  = +parent.clientWidth;
            // height = +parent.clientHeight;
            height = width / 4;

            const innerW = width - margin.left - margin.right;
            const innerH = height - margin.top - margin.bottom;
            const X = d => xScale(xValue(d)); // The x-accessor; xScale ∘ xValue.
            const Y = d => yScale(yValue(d)); // The y-accessor; yScale ∘ yValue.
            const areaFn = d3.area().x(X).y1(Y);
            const lineFn = d3.line().x(X).y(Y);

            // Update the scales.
            xScale.domain(d3.extent(data, xValue))
            if (xScale.range)       xScale.range([0, innerW]);
            if (xScale.rangeRound)  xScale.rangeRound([0, innerW]);

            yScale.domain(d3.extent(data, yValue));
            if (yScale.range)       yScale.range([0, innerW]);
            if (yScale.rangeRound)  yScale.rangeRound([0, innerW]);


            const createChartLayout = enter => {
                const clipID = getUUID();
                enter.append("svg").call(g => g
                    .append("defs")
                        .append("clipPath").attr("id", clipID)
                            .append("rect").call(setPos, {x: 0, y: 0}))
                    .append("g").classed("margin-box", true)
                        .call(g => g.append("g").classed("data", true).attr("clip-path", `url(#${clipID})`))
                        .call(g => g.append("g").classed("axis-x", true))
                        .call(g => g.append("g").classed("axis-y", true))
                        .call(g => g.append("g").classed("legend", true))
                        .call(g => g.append("line").classed("cursor-rule", true))
                        .call(g => g.append("rect").classed("interaction-rect", true));
            };

            const svg = d3.select(parent)
                .selectAll("svg")
                .data([data])
                .join(enter => createChartLayout(enter));

            // Update the outer dimensions
            svg.attr("viewBox", `0 0 ${width} ${height}`)
                .attr("preserveAspectRatio", "xMinYMin meet")
                .call(setSize, { width, height });

            // Update the clipRect dimensions
            svg.select("defs > clipPath > rect")
                .call(setSize, { width: innerW, height: innerH });

            // Update the inner dimensions
            const innerG = svg.select(".margin-box")
               .attr("transform",  `translate(${margin.left}, ${margin.top})`)

            // Update axes.
            svg.select(".axis-x")
                .attr('transform', `translate(0, ${innerH})`)
                .call(xAxis.tickSize(-innerH));

            svg.select(".axis-y")
                .call(yAxis.tickSize(-innerW));

            drawFn({
                svg,
                margin,
                innerG, innerW, innerH,
                xValue, xScale, xAxis, X,
                yValue, yScale, yAxis, Y,
                areaFn, lineFn,
            });
        });
    }

    chart.margin = function (...args) {
        if (!args.length) return margin;
        margin = args[0];
        return chart;
    }

    chart.width = function (...args) {
        if (!args.length) return width;
        width = args[0];
        return chart;
    }

    chart.height = function (...args) {
        if (!args.length) return height;
        height = args[0];
        return chart;
    }

    chart.xValue = function (...args) {
        if (!args.length) return xValue;
        xValue = args[0];
        return chart;
    }

    chart.yValue = function (...args) {
        if (!args.length) return yValue;
        yValue = args[0];
        return chart;
    }

    chart.xScale = function (...args) {
        if (!args.length) return xScale;
        xScale = args[0];
        return chart;
    }

    chart.yScale = function (...args) {
        if (!args.length) return yScale;
        yScale = args[0];
        return chart;
    }

    chart.drawFn = function (...args) {
        if (!args.length) return drawFn;
        drawFn = args[0].bind(chart);
        return chart;
    }

    return chart;
}

/*
export class timeSeriesChart {
    constructor(options) {
        // Object.setPrototypeOf(smth, Smth.prototype);
        options     = options        || {};
        this.margin = options.margin || {top: 20, right: 20, bottom: 20, left: 20};
        this.width  = options.width  || 720;
        this.height = options.height || 80;
        this.xValue = options.xValue || (d => d.x);
        this.yValue = options.yValue || (d => d.y);
        this.zValue = options.zValue || (d => d.z);
        this.xScale = options.xScale || d3.scaleTime();
        this.yScale = options.yScale || d3.scaleLinear();
        this.colors = options.colors || d3.scaleOrdinal(d3.schemeCategory10);
        this.xAxis  = options.xAxis  || d3.axisBottom(this.xScale).tickPadding(15);
        this.yAxis  = options.yAxis  || d3.axisLeft(this.yScale).tickPadding(15);
        this.render = options.render || (_ => {});
        return this.draw.bind(this);
    }

    get innerW () { return this.width - this.margin.left - this.margin.right; }
    get innerH () { return this.height - this.margin.top - this.margin.bottom; }

    areaFn = d3.area().x(this.X).y1(this.Y);
    lineFn = d3.line().x(this.X).y(this.Y);

    X = d => this.xScale(this.xValue(d)); // The x-accessor; xScale ∘ xValue.
    Y = d => this.yScale(this.yValue(d)); // The y-accessor; yScale ∘ yValue.
    Z = d => this.colors(this.zValue(d)); // The z-accessor; colors ∘ zValue.

    draw(selection) {
        selection.each((data, i, nodes) => {
            // data = data.map((d, i) => ({
            //     x: xValue.call(data, d, i),
            //     y: yValue.call(data, d, i),
            // }));
            if (!data) {
                console.error("no data bound to selection", selection);
                return;
            }

            // Update the scales.
            this.xScale.domain(d3.extent(data, this.xValue)).range([0, this.innerW]).nice();
            this.yScale.domain(d3.extent(data, this.yValue)).range([this.innerH, 0]).nice();
            this.colors.domain(d3.extent(data, this.zValue));

            // Update axes.
            this.xAxis.tickSize(-this.innerH);
            this.yAxis.tickSize(-this.innerW);

            const svg = d3.select(nodes[i]).selectAll("svg")
                .data([data])
                .join("svg")
                    // Update the outer dimensions
                    .attr("width", this.width)
                    .attr("height", this.height);

            this.innerG = svg.selectAll(".margin-box")
                .data([null])
                .join("g")
                    .classed("margin-box", true)
                    // Update the inner dimensions. TODO null binding
                    .attr("transform",  `translate(${this.margin.left}, ${this.margin.top})`);

            this.innerG
                .call(this.xAxis, this.xScale)
                .call(this.yAxis, this.yScale)

            this.render(this);
        });
    }
}
*/
/*
export function timeSeriesChart() {
    // Defaults
    let margin = {top: 20, right: 20, bottom: 20, left: 20},
        width  = 720,
        height = 80,
        xValue = d => d.x,
        yValue = d => d.y,
        zValue = d => d.z,
        xScale = d3.scaleTime(),
        yScale = d3.scaleLinear(),
        colors = d3.scaleOrdinal(d3.schemeCategory10),
        xAxis  = d3.axisBottom(xScale).tickPadding(15),
        yAxis  = d3.axisLeft(yScale).tickPadding(15),
        render = _ => {};

    const areaFn = d3.area().x(X).y1(Y);
    const lineFn = d3.line().x(X).y(Y);

    function chart(selection) {
        // TODO generate chart
        selection.each(function(data) {
            // data = data.map((d, i) => ({
            //     x: xValue.call(data, d, i),
            //     y: yValue.call(data, d, i),
            // }));
            if (!data) {
                console.error("no data bound to selection", selection);
                return;
            }

            const innerW = width - margin.left - margin.right;
            const innerH = height - margin.top - margin.bottom;

            // Update the scales.
            xScale.domain(d3.extent(data, xValue)).range([0, innerW]).nice();
            yScale.domain(d3.extent(data, yValue)).range([innerH, 0]).nice();
            colors.domain(d3.extent(data, zValue));

            // Update axes.
            xAxis.tickSize(-innerH);
            yAxis.tickSize(-innerW);

            const svg = d3.select(this).selectAll("svg")
                .data([data])
                .join("svg")
                    // Update the outer dimensions
                    .attr("width", width)
                    .attr("height", height);

            const innerG = svg.selectAll(".margin-box")
                .data([null])
                .join("g")
                    .classed("margin-box", true)
                    // Update the inner dimensions. TODO null binding
                    .attr("transform",  `translate(${margin.left}, ${margin.top})`);

            render(innerG);
        });
    }

    function X (d) { return xScale(xValue(d)); } // The x-accessor; xScale ∘ xValue.
    function Y (d) { return yScale(yValue(d)); } // The y-accessor; yScale ∘ yValue.
    function Z (d) { return colors(zValue(d)); } // The z-accessor; colors ∘ zValue.

    chart.margin = function (...args) {
        if (!args.length) return margin;
        margin = args[0];
        return chart;
    }

    chart.width = function (...args) {
        if (!args.length) return width;
        width = args[0];
        return chart;
    }

    chart.height = function (...args) {
        if (!args.length) return height;
        height = args[0];
        return chart;
    }

    chart.xScale = function (...args) {
        if (!args.length) return xScale;
        xScale = args[0];
        return chart;
    }

    chart.yScale = function (...args) {
        if (!args.length) return yScale;
        yScale = args[0];
        return chart;
    }

    chart.render = function (...args) {
        if (!args.length) return render;
        render = args[0];
        return chart;
    }

    return chart;
}
*/


// const chart = timeSeriesChart(g)
//     .width(600)
//     .height(400)

// d3.select("#example")
//       .datum(data)
//       .call(timeSeriesChart);