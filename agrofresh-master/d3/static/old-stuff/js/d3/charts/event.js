import '/static/d3.v6.min.js';

// TODO fix & clean
export const render = (selection, props) => {
    // const parseDate = d3.timeFormat("%m/%d/%Y %H:%M").parse;
    const data = [
        { time: '1/1/2020 10:12',type:'inc_call' },
        { time: '1/2/2020 10:12',type:'inc_call' },
        { time: '1/2/2020 10:12', type: 'out_text' },
        { time: '1/3/2020 10:12', type: 'out_call' },
        { time: '1/4/2020 10:12', type: 'inc_text' },
        { time: '1/5/2020 10:12', type: 'inc_text' },
    ].map(d => ({
        time: new Date(d.time),
        type: d.type
    }));

    const margin = {top: 20, right: 20, bottom: 30, left: 60},
        width = 960 - margin.left - margin.right,
        height = 200 - margin.top - margin.bottom;

    const colorOf = d3.scaleOrdinal(d3.schemeCategory10)
        .domain(data.map(d => d.type));

    const y = d3.scaleBand()
        .rangeRound([height, 0])
        .domain(data.map(d => d.type));

    const x = d3.scaleTime()
        .range([5, width])
        .domain(d3.extent(data, d => d.time));

    const yAxis = g => g
        .call(d3.axisLeft(y)
            .ticks(null, x => +x.toFixed(6) + "×"))
        .call(g => g.selectAll(".tick line").clone()
            .attr("stroke-opacity", d => d === 1 ? null : 0.2)
            .attr("x2", width - margin.left - margin.right))
        .call(g => g.select(".domain").remove())

    const xAxis = g => g
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x)
        .ticks(width / 80)
        .tickSizeOuter(0)
        .tickFormat(d3.timeFormat("%m/%d/%Y %Hh")))
        .call(g => g.select(".domain").remove())


    // TODO selection
    const svg = d3.select("body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)

    const innerG = svg.append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    innerG.append("g").call(xAxis);
    innerG.append("g").call(yAxis);

    innerG.selectAll(".bar")
        .data(data)
        .join("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.time))
            .attr("y", d => y(d.type))
            .attr("height", y.bandwidth() - 4)
            .attr("width", d => d.duration || 10)
            .style("fill", d => colorOf(d.type));
};