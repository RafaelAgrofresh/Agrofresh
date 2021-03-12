// import '/static/d3.v6.min.js';
// import { cursor } from '../../js/d3/cursor.js';
// import { getUUID, getParentSvg } from './jsobject.js';


// export const nullJoin = (selection, { tag , cls }) => {
//     const selector = cls ? `.${cls}` : tag;
//     const join = selection.selectAll(selector).data([null]).join(tag);
//     if (cls) join.classed(cls, true);
//     return join;
// }

// export const defineClipRect = (selection, innerW, innerH) => {
//     const svg = getParentSvg(selection);

//     const defs = svg.selectAll("defs")
//         .data([null])
//         .join("defs");

//     const clipPath = defs.selectAll("clipPath")
//         .data([null])
//         .join(enter => enter.append("clipPath")
//             .attr("id", _ => getUUID()));

//     const rect = clipPath.selectAll("rect")
//         .data([null])
//         .join("rect")
//         .attr("width", innerW)
//         .attr("height", innerH)
//         .attr("x", 0)
//         .attr("y", 0);

//     return svg.select("defs clipPath").node().id;
// };

// // export const defineClipRect = (selection, innerW, innerH) => {
// //     const svg = getParentSvg(selection);
// //     const defs = svg.selectAll("defs")
// //         .data([null])
// //         .join(enter => enter.append("defs")
// //             .append("clipPath")
// //             .attr("id", _ => getUUID())
// //             .append("rect")
// //             .attr("width", innerW)
// //             .attr("height", innerH)
// //             .attr("x", 0)
// //             .attr("y", 0));

// //     return svg.select("defs clipPath").node().id
// // };

// export const createXCursor = (innerG, { innerW, innerH, xScale }) => {
//     // TODO move to d3/cursor.js
//     const rule = nullJoin(innerG, { tag: "line", cls: "cursor-rule"})
//        .attr("y1", innerH)
//        .attr("y2", 0)
//        .attr("stroke", "black")
//        .raise();

//    const setCursorFn = ({ x, y }) => {
//        x = xScale(x);
//        d3.selectAll('.cursor-rule')
//            .attr("x1", x)
//            .attr("x2", x);
//    };

//    cursor(innerG, { innerW, innerH, xScale, setCursorFn });
// }

// export const preProcessData = data => {
//     data.forEach(d => {
//         d.ts = new Date(d.ts);
//         numericFields.forEach(col => d[col] = +d[col]);
//         booleanFields.forEach(col => d[col] = !!d[col]);
//     });
//     return data;
// }

// export const checkedFields = checks => checks.nodes()
//     .filter(c => c.checked)
//     .map(c => c.value);

// export const zoomBehavior = (g, { innerW, innerH, zoomFn }) => g.call(
//     d3.zoom()
//         .scaleExtent([1, 32])  // zoom from x1 to x32
//         .extent([[0, 0], [innerW, innerH]])
//         .translateExtent([[0, 0], [innerW, innerH]])
//         .on("zoom", zoomFn));

// export const yLabel = (selection, { innerH, margin, text }) =>
//     selection.call(g => nullJoin(g, {tag: "text", cls: "label-y"})
//         .attr("transform", "rotate(-90)")
//         .attr("y", 0 - margin.left)
//         .attr("x", 0 - (innerH / 2))
//         .attr("dy", "1em")
//         .style("text-anchor", "middle")
//         .text(text));

// export const resize = (selection, {width, height}) =>
//     selection
//         .attr('width', width)
//         .attr('height', height);

// export const resizeSVG = (selection, {width, height}) =>
//     selection.call(resize, {width, height})
//         .attr("viewBox", [0, 0, width, height]);