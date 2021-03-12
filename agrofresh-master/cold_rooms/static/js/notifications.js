export class Notifications {
    constructor(target) {
        this.target = target;
    }

    update(data) {
        const errors = data.structs
            .filter(struct => struct.error)
            .map(struct => {
                const { error, cold_room } = struct;
                return { error, cold_room };
            });

        this.target.selectAll('.alert')
            .data(errors)
            .join(enter => enter.append("div")
                .classed("alert alert-danger", true))
                .style("padding-top", "2px")
                .style("padding-bottom", "2px")
                .style("margin-top", "2px")
                .style("margin-bottom", "4px")
                .text(d => d.error)
    }
}
