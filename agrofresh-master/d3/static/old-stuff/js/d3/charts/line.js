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

  const margin = {left: 40, right: 10, top: 40, bottom: 40};
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const innerG = selection.selectAll('g')
    .data([null])
    .join('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

  const xValue = (_, i) => i;
  const yValue = d => d;

  // TODO: const xScale = d3.scaleTime()
  const xScale = d3.scaleLinear()
    .domain(d3.extent(data, xValue))
    .range([0, innerW]);

  const yScale = d3.scaleLinear()
    .domain(d3.extent(data, yValue))
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


  const chartG = innerG.append('g')
    .classed('chart', true);

  const lineGenerator = d3.line()
      .x((_, i) => xScale(xValue(_, i)))
      .y(d => yScale(yValue(d)))
      // .curve(d3.curveBasis);

  chartG.selectAll('path')
    .data([null])
    .join('path')
      .attr('d', lineGenerator(data))
      .classed('line-path', true);

  // const points = chartG.selectAll('circle')
  //   .data(data, (_, i) => i)
  //   .join('circle')
  //     .classed('line-point', true)
  //     .attr('cx', (_, i) => xScale(xValue(_, i)))
  //     .attr('cy', d => yScale(yValue(d)))
  //     .attr('r', 5)
};

// let idx = 0;
// const N = 1000;
// const buffer = Array.from(Array(N), _ => 0);
// const renderLoop = () => {
//   const data = d3.range(N)
//     .map(k => (idx + k) % N)
//     .map(k => buffer[k]);

//   //renderBarChart(svg, data);
//   renderLineChart(svg, data);
//   setTimeout(renderLoop, 100);

//   for(let i = 0; i < 100; i++){
//     buffer[idx] = rndInt(1000);
//     idx += 1;
//     idx %= N;
//   }
// }
// renderLoop();
