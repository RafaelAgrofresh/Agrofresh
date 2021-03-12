const fmt = value => {
    if (typeof value === "boolean") return value ? "on" : "off";
    if (typeof value === "number") return d3.format("~s")(value.toFixed(10));
    return value;
};

export class Table {
    constructor(table, { header, columns, writeHandler }) {
        this.table = table;
        this.table.append("thead").append("tr");
        this.table.append("tbody");

        this.header = header;
        this.columns = columns;
        this.writeHandler = writeHandler;
        this.rowFilter = _ => true;
    }

    _getColumns(data) {
        return [
            ...this.columns,
            ...data.structs
                .map(struct => struct["cold_room"])
                .map(pk => ({
                    id: pk,
                    text: `${pk}`,
                    width: "20px",
                    editable: true,
                    visible: true,
                }))
        ];
    }

    _getRows(data) {
        return Object.keys(data.fields).map(prop => [
            data.fields[prop].tags,
            prop,
            data.fields[prop].type,
            data.fields[prop].addr,
            data.fields[prop].desc,
            ...data.structs.map(struct => struct[prop])
        ]);
    }

    update(data) {
        const colData = this._getColumns(data);
        const rowData = this._getRows(data);

        // header row
        this.table.select("thead tr")
            .style("display", this.header ? "table-row" : "none")
            .selectAll("th")
            .data(colData)
            .join("th")
                .attr("id", (_, idx) => `col-${idx}`)
                .style("width", column => column.width)
                .style("display", column => column.visible ? "table-col" : "none")
                .text(column => column.text);

        // create a row for each property in the data
        const rows = this.table.select("tbody")
            .selectAll("tr")
            .data(rowData, r => r[1])
            .join("tr")
                .attr("id", (_, idx) => `row-${idx}`);

        // create a cell in each row for each property
        const cells = rows.selectAll("td")
            .data(row => row)
            .join(enter => enter.append("td")
                .classed("editable", (_, i) => colData[i].editable)
                .attr("data-coldroom", (_, i) => colData[i].id)
                .style("display", (_, i) => colData[i].visible ? "table-col" : "none")
                .call(this._setViewMode.bind(this)));

        cells.select(".value").text(d => fmt(d));

        // set class based on tags (iodata|alarm|param|...)
        this.table.selectAll("tbody tr")
            .call(row => row.select("td:first-child")
                .attr("class", d => d[0].join(" "))
                .selectAll("span")
                .data(d => d[0].sort())
                .join("span")
                    .classed("value tag badge badge-secondary", true)
                    .style("margin", "1px")
                    .text(d => d));

        this.applyRowFilter();
    }

    _setViewMode(td) {
        td.call(td => td.select("input")
                .on("focus", null)
                .on("change", null)
                .on("click", null)
                .on("keydown", null)
                .remove())
            .append("span")
            .classed("value", true)
            .on("click", event => {
                const td = d3.select(event.target.parentNode);
                if (td.classed("editable"))
                    this._setEditMode(td);
            });
    }

    _setEditMode(td) {
        const writeData = this._writeData.bind(this);
        const setViewMode = this._setViewMode.bind(this);

        td.call(td => td.select("span")
                .on("click", null)
                .remove())
            .append("input")
            .classed("form-control", false)
            .attr("type", d => typeof d == "boolean" ? "button" : "text")
            .attr("value", d => fmt(d))
            .on("focus", event => event.target.select())
            .on("change", _ => td.call(writeData).call(setViewMode))
            .on("click", _ => td.call(writeData).call(setViewMode))
            .on("keydown", event => {
                const ESC = 27;
                const RET = 13;

                if (event.keyCode === ESC) {
                    td.call(setViewMode);
                    return;
                }

                if (event.keyCode === RET) {
                    td.call(writeData).call(setViewMode);
                    return;
                }
            })
            .node().focus();
    }

    _writeData(td) {
        const { cold_room, property, value } = this._buildPayload(td);
        const oldValue = td.datum();
        if (oldValue === value) return;
        const json = Object.fromEntries([[property, value]]);
        this.writeHandler(cold_room, json);
    }

    _buildPayload(td) {
        const tr = d3.select(td.node().parentNode);
        const inputDOM = td.select("input").node();
        const cold_room = td.attr("data-coldroom");
        const property = tr.datum()[1];
        const value = JSON.parse(inputDOM.type == "button"
            ? inputDOM.value.toLowerCase() !== "on"
            : inputDOM.value);

        return { cold_room, property, value };
    }

    applyRowFilter() {
        this.table.selectAll("tbody tr")
            .style("display", d => this.rowFilter(d) ? "table-row" : "none");
    }
}