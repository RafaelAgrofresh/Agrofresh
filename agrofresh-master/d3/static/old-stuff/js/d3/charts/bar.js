import '/static/d3.v6.min.js';

export const render = (selection, data, props) => {
  const {
    width,
    height,
  } = props;

  // const width = document.body.clientWidth;
  // const height = document.body.clientHeight;

  selection
    .attr('width', width)
    .attr('height', height);

  const margin = {left: 10, right: 10, top: 10, bottom: 10};
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const innerG = selection.selectAll('g')
    .data([null])
    .join('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

  const xValue = (_, i) => i;
  const yValue = d => d;

  const xScale = d3.scaleBand()
    .domain(data.map(xValue))
    .range([0, innerW])
    .padding(0.1);

  const yScale = d3.scaleLinear()
    // .domain([0, d3.max(data, yValue)])
    .domain([0, 1000])
    .range([innerH, 0]);

  innerG.append('g').call(d3.axisBottom(xScale))
    .attr('transform', `translate(0, ${innerH})`)
    .classed('x-axis', true)
    .selectAll('.domain, .tick line')
      .remove();

  const yAxis = d3.axisLeft(yScale)
    .tickFormat(d3.format('.2s'))
    .tickSize(-innerW);

  innerG.append('g').call(yAxis)
    .classed('y-axis', true)
    .selectAll('.domain')
      .remove();

  const barsG = innerG.append('g')
    .classed('bars', true)
    .attr('transform', `translate(0, ${innerH}) scale(1, -1)`);

  const rects = barsG.selectAll('rect')
    .data(data, (_, i) => i);
    // .join('rect')
    rects.enter().append('rect')
      .attr('fill', 'steelblue')
      .attr('x', (_, i) => xScale(xValue(_, i)))
      .attr('width', xScale.bandwidth())
      .attr('height', d => yScale(yValue(d)));

    rects.transition().attr('height', d => yScale(yValue(d)));
};

// const rndInt = max => Math.floor(Math.random() * Math.floor(max));
// const rndData = () => d3.range(10).map(_ => rndInt(1000));
// // const data = d3.range(10).map(_ => rndInt(1000));

// const svg = d3.select('svg');
// const renderLoop = () => {
//   render(svg, rndData());
//    setTimeout(renderLoop, 1000);
// }
// renderLoop();