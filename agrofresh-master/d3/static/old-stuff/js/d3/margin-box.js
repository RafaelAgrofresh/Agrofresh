
// import '/static/d3.v6.min.js';

export const marginBox = (selection, margin) => {
    const width = +selection.attr('width');
    const height = +selection.attr('height');
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;
    const innerG = selection.selectAll('g')
        .data([null])
        .join('g')
            .classed('margin-box', true)
            .attr('transform', `translate(${margin.left}, ${margin.top})`);

    return { innerW, innerH, innerG };
};
