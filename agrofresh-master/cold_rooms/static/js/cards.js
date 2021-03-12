function clickHandler(sender, cardID) {
    // const query = `#cold_room${cold_room_id}-card .measurements`;
    const query = `#${cardID} .measurements`;
    const container = document.querySelector(query);
    const charts = container.getElementsByClassName("chart-active");
    if (!charts) return;
    for (const chart of charts) {
        chart.classList.remove("chart-active");
    }
    sender.classList.add("chart-active");
}
