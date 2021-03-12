import '/static/d3.v6.min.js';

export const cursor = (selection, props) => {
    const {
        innerW,
        innerH,
        xScale,
        yScale,
        setCursorFn,
    } = props;

    const moveCursor = event => {
        const point = d3.pointer(event);
        const x = xScale.invert(point[0]);
        const y = yScale?.invert
            ? yScale.invert(point[1])
            : 0;
        setCursorFn({x, y});
    };

    selection.selectAll('.interaction-rect')
        .data([null])
        .join('rect')
            .classed('interaction-rect', true)
            .attr('width', innerW)
            .attr('height', innerH)
            .attr('fill', 'none')
            .attr('pointer-events', 'all')
            .on('mousemove', moveCursor);
};
