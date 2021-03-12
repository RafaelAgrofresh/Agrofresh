const floatFmt = d3.format(".1f");

const synoptic = d3.select("#synoptic svg")
const door_open = synoptic.select("#door_open");
const door_closed = synoptic.select("#door_closed");
const humidity_active = synoptic.select("#humidity_active");
const c2h4_active = synoptic.select("#c2h4_active");
const airtherm_active = synoptic.select("#airtherm_active");
const heater_active = synoptic.select("#heater_active");
const cooler_active = synoptic.select("#cooler_active");

const ac_on = synoptic.select("#ac_on");
const airtherm_on = synoptic.select("#airtherm_on");
const fanin_on  = synoptic.select("#fanin_on");
const fanout_on = synoptic.select("#fanout_on");

// CO2ControlSelection
// C2H4ControlSelection
// hr338.2  -> velocidad ventilador entrada [fanIn1Activated]
// hr338.3  -> velocidad ventilador sailda  [fanOut1Activated]
// hr250.12 -> frio                         [fridgeRequest]
// hr250.13 -> calor                        [heaterRequest]
// hr339.7  -> aerotermo                    [aeroheatersGeneralState] airHeater1??
// hr339.9  -> humedad                      [humidityValvesActivated]
// hr338.1  -> c2h4                         [ethyleneValvesActivated]
// hr256.14 -> puerta                       [door1Open] ??
// hr256.11 -> selector modo                [autoTelSelectorState]

// hr270 -> temperatura                     [temperatureInside]
// hr266 -> humedad                         [humidityInside]
// hr274 -> co2                             [CO2Measure]
// hr276 -> c2h4                            [C2H4Measure]

// window['synoptic'] = {
//     door_open: false,
//     humidity_active: false,
//     c2h4_active: false,
//     cooler_active: false,
//     heater_active: false,
//     airtherm_active: false,
//     fanin_active: false,
//     fanout_active: false,
//     warning: false,
//     selector: false,
// };

export function updateSynoptic(data, options) {
    options = {
        // Defaults
        ...{
            enable_selector: true,
        },
        // settings
        ...options
    };

    // const state = { ...window['synoptic'] };
    // window['data'] = data;
    const state = {
        door_open: data.door1Open,
        humidity_active: data.humidityValvesActivated,
        c2h4_active: data.ethyleneValvesActivated,
        cooler_active: data.fridgeRequest,
        heater_active: data.heaterRequest,
        airtherm_active: data.aeroheatersGeneralState,
        fanin_active: data.fanIn1Activated,
        fanout_active: data.fanOut1Activated,
        warning: data.anyAlarm,
        selector: data.autoTelSelectorState
    };

    updateSynopticMeasurements(data);
    updateSynopticFans(state);
    updateSymbols(state, options);

    door_open.style("opacity", state.door_open ? 1 : 0);
    door_closed.style("opacity", state.door_open ? 0 : 1);
    humidity_active.style("opacity", state.humidity_active ? 1 : 0);
    c2h4_active.style("opacity", state.c2h4_active ? 1 : 0);
    cooler_active.style("opacity", state.cooler_active ? 1 : 0);
    heater_active.style("opacity", state.heater_active ? 1 : 0);
    airtherm_active.style("opacity", state.airtherm_active ? 1 : 0);

    ac_on.classed("glow-active", state.cooler_active || state.heater_active);
    airtherm_on.classed("glow-active", state.airtherm_active);
    fanin_on.classed("glow-active", state.fanin_active);
    fanout_on.classed("glow-active", state.fanout_active);

    humidity_active.classed("fade-opacity", state.humidity_active);
    c2h4_active.classed("fade-opacity", state.c2h4_active);
}

function updateSynopticMeasurements(data) {
    const measurements = synoptic.selectAll(".measurement");
    if (!measurements) return;

    measurements.each((_, i, nodes) => {
        const property = nodes[i].dataset.src;
        const value = floatFmt(data[property]);
        d3.select(nodes[i]).select("tspan").text(value);
    });
}

function updateSynopticFans(data) {
    const fans = [
        { id: 'fanin',    size: 20, x: 77.5, y: 10, predicate: d => d.fanin_active },
        { id: 'fanout',   size: 16, x: 220, y: 90, predicate: d => d.fanout_active },
        { id: 'airtherm', size: 20, x: 202.5, y: 10, predicate: d => d.airtherm_active },
        { id: 'ac_fan1',  size: 16, x: 131.5, y: 10, predicate: d => d.cooler_active || d.heater_active },
        { id: 'ac_fan2',  size: 16, x: 154, y: 10, predicate: d => d.cooler_active || d.heater_active },
    ];

    synoptic.selectAll('.fan')
        .data(fans)
        .join(enter => enter.append("image")
            .classed('fan', true)
            .attr("xlink:href", "/static/svg/fan.svg")
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("width", d => d.size)
            .attr("height", d => d.size)
            .style("opacity", "0.8")
            .style("transform-origin", d => `${d.x + d.size / 2}px ${d.y + d.size / 2}px`))
         .classed("fa-spin", d => d.predicate(data));
}

function updateSymbols(data, options) {
    const symbols = [
        { url:"/static/svg/warning.svg", size: 30, x: 5, y: 5, predicate: d => d.warning },
        { url:"/static/svg/switch-knob-on.svg", size: 30, x: 255, y: 5, predicate: d => options.enable_selector && d.selector },
        { url:"/static/svg/switch-knob-off.svg", size: 30, x: 255, y: 5, predicate: d => options.enable_selector && !d.selector },
    ];

    synoptic.selectAll('.svg-symbol')
        .data(symbols)
        .join(enter => enter.append("image")
            .classed('svg-symbol', true)
            .attr("xlink:href", d => d.url)
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("width", d => d.size)
            .attr("height", d => d.size)
            .style("transform-origin", d => `${d.x + d.size / 2}px ${d.y + d.size / 2}px`))
        .style("opacity", d => d.predicate(data) ? 1 : 0);
}
