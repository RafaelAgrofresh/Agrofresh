export function flatten(data) {
    // flatten JS object ('.' separated keys)
    var result = {};
    function recurse (cur, prop) {
        if (Object(cur) !== cur) {
            result[prop] = cur;
        } else if (Array.isArray(cur)) {
            for(var i=0, l=cur.length; i<l; i++)
                recurse(cur[i], prop + "[" + i + "]");
            if (l == 0)
                result[prop] = [];
        } else {
            var isEmpty = true;
            for (var p in cur) {
                isEmpty = false;
                recurse(cur[p], prop ? prop+"."+p : p);
            }
            if (isEmpty && prop)
                result[prop] = {};
        }
    }
    recurse(data, "");
    return result;
}

export function unflatten(data) {
    // unflatten JS object ('.' separated keys)
    if (Object(data) !== data || Array.isArray(data))
        return data;
    var regex = /\.?([^.\[\]]+)|\[(\d+)\]/g,
        resultholder = {};
    for (var p in data) {
        var cur = resultholder,
            prop = "",
            m;
        while (m = regex.exec(p)) {
            cur = cur[prop] || (cur[prop] = (m[2] ? [] : {}));
            prop = m[2] || m[1];
        }
        cur[prop] = data[p];
    }
    return resultholder[""] || resultholder;
}

export function getColumns(data) {
    // TODO: assert Array.isArray(data)
    // or handle other cases e.g.:
    // if (!Array.isArray(data)) return Object.keys(data);

    return data
        .map(x => Object.keys(x))
        .reduce((acc, x) => acc.concat(...x), [])
        .reduce((acc, x) => acc.includes(x) ? acc : [...acc, x], []);
}

export function transpose(data) {
    const columns = getColumns(data);
    const entries = columns.map(col => [col, data.map(row => row[col]) ])
    return Object.fromEntries(entries);
}

export const getUUID = () => ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g,
    c => (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16))

export function* ancestors(element) {
    parent = element;
    while (parent) {
        yield parent;
        parent = parent.parentElement;
    }
}

export function getParentOfType(element, type) {
    // e.g getParentOfType(child, 'svg')
    const node = element.node();
    for (const ancestor of ancestors(node))
        if (ancestor.nodeName === type)
            return d3.select(ancestor);

    return null;
}

