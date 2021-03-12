export const N_SAMPLES = 500;

const data = {
    labels: [],
    datasets: [{
        backgroundColor: 'rgba(255,255,255,.2)',
        borderColor: 'rgba(255,255,255,.55)',
        data: [],
    }]
};

const options = {
    maintainAspectRatio: false,
    tooltips: { enabled: false },
    legend: { display: false },
    layout: {
        padding: { left: 0, right: 0, top: 0, bottom: 2 },
    },
    scales: {
        xAxes: [{ display: false }],
        yAxes: [{ display: false, ticks: { max: 0, min: 0 } }],
    },
    elements: {
        line: { borderWidth: 2 },
        point: {
            radius: 0,
            hitRadius: 10,
            hoverRadius: 4,
        }
    },
    animation: { duration: 0 },
    hover: { animationDuration: 0 },
    responsiveAnimationDuration: 0,
};

function isIterable (value) {
    return Symbol.iterator in Object(value);
}

export class Sparkline {
    constructor(canvas) {
        if (!canvas)
            throw new Error('expected not null canvas');

        this.canvas = canvas;
        this.chart = new Chart(canvas, { type: 'line', data, options });
    }

    update(buffer) {
        if (!buffer || !isIterable(buffer))
            throw new Error('expected not null buffer');

        const data = [...buffer];
        this.chart.data.datasets[0].data = data;
        if (this.chart.data.labels.length !== data.length) {
            this.chart.data.labels = Array.from({ length: data.length }, (_, i) => i);
        }

        // set yAxes[0] range to absolute min, max values
        const yValue = data[data.length - 1] || 0;
        const yTicks = this.chart.options.scales.yAxes[0].ticks;
        this.chart.options.scales.yAxes[0].ticks = {
            ...yTicks,
            min: Math.min(yTicks.min || 0, yValue),
            max: Math.max(yTicks.max || 0, yValue),
        };

        this.chart.update();
    }
}
