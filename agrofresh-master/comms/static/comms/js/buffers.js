export class CircularBuffer {
    constructor(n) {
        this.n = n;
        this.idx = 0;
        this.arr = Array.from({length: n}, _ => 0);
    }

    *[Symbol.iterator]() {
        for (let i = 0; i < this.n; i++) {
            const idx = (this.idx + i) % this.n;
            yield this.arr[idx];
        }
    }

    push(value) {
        this.arr[this.idx] = value;
        this.idx = (this.idx + 1) % this.n;
    }

    *map(mapper, thisArg) {
        for (const val of this)
            yield mapper.call(thisArg, val);
    }
}

