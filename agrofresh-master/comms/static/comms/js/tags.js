export const filterByTag = (fields, tag) => Object.fromEntries(
    Object.entries(fields).filter(field => field[1].tags.includes(tag))
);

export const extractTagSet = fields => Array.from(new Set([].concat(
    ...Object.values(fields).map(f => f.tags))
)).sort();

const isEmpty =  array => !array || array.length === 0;

export class TagFilter {
    constructor(target, tags, handler) {
        this.target = target;
        this.tags = tags;
        this.handler = handler || (() => {}); // TODO events?

        const setChecked = checked => tag => tag.classed('checked', checked)
            .transition().duration(250)
            .style("opacity", checked ? 1: 0.4);

        this.target
            .selectAll('.tag')
            .data(tags)
            .join(enter => enter.append('span')
                .text(d => d)
                .classed("tag btn btn-sm btn-dark", true))
                .style("margin", "2px")
                .style("padding", "2px")
                .call(setChecked(false))
                .on('click', event => {
                    const tag = d3.select(event.target);
                    const checked = !tag.classed('checked');
                    tag.call(setChecked(checked));
                    this.handler();
                });

        this.target.append('button')
            .attr("type", "button")
            .classed("btn btn-sm", true)
            .html("&times;")
            .on('click', event => {
                this.target.selectAll('.tag').call(setChecked(false));
                event.target.blur();
                this.handler();
            });
    }

    get predicate() {
        const checkedTags = this.target
            .selectAll('.tag.checked').nodes()
            .map(n => n.innerText);

        return tags => isEmpty(checkedTags)
            || checkedTags.every(tag => tags.includes(tag));
    }
}
