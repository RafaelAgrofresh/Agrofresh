export class Writer {

    constructor(post_uri, csrf_token) {
        this.post_uri = post_uri;
        this.csrf_token = csrf_token;
    }

    async write(cold_room, json) {

        // TODO write only changes
        // TODO refactor post_uri endpoint to take multiple properties at once
        const writeProperty = this.writePropertyPromise.bind(this);
        const tasks = Object.entries(json)
            .map(([property, value]) => writeProperty(cold_room, property, value));

        const results = await Promise.all(tasks);     // Gather up the results.
        results.forEach(x => console.log(x));         // Print them out on the console
    }

    writePropertyPromise(cold_room, property, value) {
        return d3.json(this.post_uri, {
            method: "POST",
            headers: { "X-CSRFToken": this.csrf_token },
            body: JSON.stringify({ cold_room, property, value })
        }).then(d => `cold_room[pk=${d.data.cold_room}].${d.data.property}=${d.data.value}`);
    }
}
