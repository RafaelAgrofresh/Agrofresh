// https://bost.ocks.org/mike/chart/
// https://bost.ocks.org/mike/chart/time-series-chart.js
// https://bost.ocks.org/mike/d3-plugin/

const setPos = (selection, {x, y}) => selection
    .attr("x", x)
    .attr("y", y);

const setSize = (selection, {width, height}) => selection
    .attr("width", width)
    .attr("height", height);

const getUUID = () => ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g,
    c => (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));

export default function() {
    // Defaults
    let margin = { top: 20, right: 20, bottom: 20, left: 20 },
        size   = { width: 720, height: 180 },
        drawFn = _ => {};

    const createChartLayout = svg => {
        const clipID = getUUID();
        return svg.call(g => g
            .append("defs")
                .append("clipPath").attr("id", clipID)
                    .append("rect").call(setPos, {x: 0, y: 0}))
            .append("g").classed("margin", true)
                .call(g => g.append("g").classed("data", true).attr("clip-path", `url(#${clipID})`))
                .call(g => g.append("g").classed("axis-x", true))
                .call(g => g.append("g").classed("axis-y", true))
                .call(g => g.append("g").classed("legend", true))
                .call(g => g.append("line").classed("cursor-rule", true))
                .call(g => g.append("rect").classed("interaction-rect", true));
    };

    function chart(selection) {
        selection.each((data, i, nodes) => {
            if (!data) {
                console.error("no data bound to selection", selection);
                return;
            }

            const parent = nodes[i];
            size.width  = size.width  || +parent.clientWidth;
            size.height = size.height || +parent.clientHeight; // height = width / 4;

            const innerW = size.width - margin.left - margin.right;
            const innerH = size.height - margin.top - margin.bottom;

            const svg = d3.select(parent)
                .selectAll(".chart")
                .data([data])
                .join(enter => enter.append("svg")
                    .classed("chart", true)
                    .call(createChartLayout));

            // Update the outer dimensions
            svg.attr("viewBox", `0 0 ${size.width} ${size.height}`)
                .attr("preserveAspectRatio", "xMinYMin meet")
                .call(setSize, size);

            const innerSize = { width: innerW, height: innerH };
            // Update the clipRect dimensions
            svg.select("defs > clipPath > rect")
                .call(setSize, innerSize);

            // Update the inner dimensions
            const innerG = svg.select(".margin")
               .attr("transform", `translate(${margin.left}, ${margin.top})`)

            innerG.select(".interaction-rect")
                .call(setSize, innerSize);

            // Update the scales
            // Update axes

            drawFn({
                data,
                svg,
                margin,
                innerG, innerW, innerH,
            });

            innerG.select(".cursor-rule")
                .attr("y1", innerH)
                .attr("y2", 0);
        });
    }

    chart.margin = function(_) { return arguments.length ? (margin = _, chart) : margin; }
    chart.size   = function(_) { return arguments.length ? (size   = _, chart) : size;   }
    chart.drawFn = function(_) { return arguments.length ? (drawFn = _, chart) : drawFn; }

    return chart;
}
