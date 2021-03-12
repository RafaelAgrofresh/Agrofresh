import '/static/d3.v6.min.js';
import { getUUID } from '/static/comms/js/jsobject.js';

export const fieldSetLegend = (selection, legend) => {
    selection
        .append('legend')
        .text(legend);
}

export const buttonGroup = (selection, props) => {
    const {
        buttons,
    } = props;

    return selection
        .selectAll('button')
        .data(buttons)
        .join('button')
            .text(d => d.name)
            .classed("btn", true)
            .classed("btn-sm", true)
            .classed("btn-secondary", true);
}

export const dropDown = (selection, props) => {
    // TODO multiple  .attr('multiple', 'multiple');
    const {
        options,
        valueFn,
        textFn,
    } = props;

    const select = selection.append('select');
    select.selectAll('option')
        .data(options)
        .join('option')
            .attr('value', valueFn || (d => d))
            .text(textFn || (d => d));

    return select;
};

export const checkBoxes = (selection, props) => {
    const {
        options,
        valueFn,
        textFn,
    } = props;

    const buttons = [
        { name: 'all', fn: _ => true},
        { name: 'none', fn: _ => false},
        { name: 'toggle', fn: (_, i, node) => !node[i].checked },
    ];

    buttonGroup(selection, { buttons })
        .on('click', d => {
            d3.event.preventDefault();
            const checkboxes = selection.selectAll('input[type=checkbox]');
            checkboxes.property('checked', d.fn);
            checkboxes.dispatch('change');
            return false;
        });

    const valueGetter = valueFn || (d => d);
    const textGetter = textFn || (d => d);

    const div = selection.selectAll('div')
        .data(options)
        .join('div')
            .classed("custom-control", true)
            .classed("custom-checkbox", true);

    const uuid = getUUID();
    const idGenerator = (_, i) => `checkbox-${uuid}-${i}`;

    const checks = div.append('input')
        .attr('type', 'checkbox')
        .attr('id', idGenerator)
        .attr('name', valueGetter)
        .attr('value', valueGetter)
        .classed("custom-control-input", true);

    div.append('label')
        .attr('for', idGenerator)
        .text(textGetter)
        .classed("custom-control-label", true);

    return checks;
};

export const radioButtons = (selection, props) => {
    const {
        options,
        valueFn,
        textFn,
    } = props;

    const valueGetter = valueFn || (d => d);
    const textGetter = textFn || (d => d);

    const div = selection.selectAll('div')
        .data(options)
        .join('div')
            .classed("custom-control", true)
            .classed("custom-radio", true);

    const uuid = getUUID();
    const idGenerator = (_, i) => `radio-${uuid}-${i}`;

    const radios = div.append('input')
        .attr('type', 'radio')
        .attr('id', idGenerator)
        .attr('name', uuid)
        .attr('value', valueGetter)
        .classed("custom-control-input", true);

    div.append('label')
        .attr('for', idGenerator)
        .text(textGetter)
        .classed("custom-control-label", true);

    return radios;
};

 export const dateTime = (selection) => {
    const div = selection.append('div');

//     const date = div.append('input')
//             .attr('type', 'date')
//             .attr('name', 'date')
//             // .attr('min', '2018-12-31')
//             // .attr('max', '2020-12-31');

//     const time = div.append('input')
//             .attr('type', 'time')
//             .attr('name', 'time')
//             // .attr('min', '9:00')
//             // .attr('max', '18:00');

//     function change() {
//         const dateValue = date.node().value;
//         const timeValue = time.node().value;

//         const dateTime = new Date(timeValue
//                 ?`${dateValue}T${timeValue}`
//                 : dateValue);

//         console.log(dateTime.toISOString());
//     }

//     date.on('change', change);
//     time.on('change', change);
    return div;
}
