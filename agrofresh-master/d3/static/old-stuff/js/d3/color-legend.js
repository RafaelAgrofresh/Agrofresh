//import '/static/d3.v6.min.js';

export const colorLegend = (selection, props) => {
    const {
        spacing,
        colorScale,
    } = Object.assign({
        spacing: 20,
        // DEFAULTS
    }, props);

    // TODO ? selection = svg.selectAll('g').data([series]).classed('legend')

     const items = selection.selectAll('.legend-item')
        // .data(d => d)
        .data(colorScale.domain())
        .join(enter => enter.append("g").classed('legend-item', true)
            .call(item => item.append('rect'))
            .call(item => item.append('text')))

    items.select('rect')
        .attr('x', 0)
        .attr('y', (_, i) => i * 20)
        .attr('width', 10)
        .attr('height', 10)
        .style('fill', colorScale);

    items.select('text')
        .attr('x', 12)
        .attr('y', (_, i) => (i * 20) + 9)
        .text(d => d);
}
