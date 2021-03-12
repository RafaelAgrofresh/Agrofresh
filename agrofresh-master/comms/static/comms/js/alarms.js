function getUnacknowledgedAlarms(data, {cold_room=null, unacknowledged=true}={}) {
    if (!data.fields) throw `'fields' not found in ${data}`;
    if (!data.alarms) throw `'alarms' not found in ${data}`;

    const coldRoomFilter = cold_room && +cold_room > 0
        ? alarm => alarm.meta.cold_room == cold_room
        : _ => true;

    const unacknowledgedFilter = unacknowledged && !!unacknowledged
        ? _ => true
        : alarm => !alarm.ts_end;

    const activeAlarms = data.alarms
        .filter(coldRoomFilter)
        .filter(unacknowledgedFilter)
        .map(a => ({
                ...a,
                desc: data.fields[a.name].desc,
                cold_room: a.meta.cold_room,
                active: !a.ts_end
        }));

    return [].concat(...activeAlarms);
}

function getUnacknowledgedAlarmsSorted(data, options) {
    const alarms = getUnacknowledgedAlarms(data, options);
    const keyFn = a => `${a.meta.alarm}/${a.meta.cold_room}`;
    const groups = d3.group(alarms, keyFn);
    const filtered = [...groups.values()].map(
        group => group.sort((a, b) => d3.ascending(a.active, b.ts))[0]
    );
    return [].concat(...filtered);
}

export { getUnacknowledgedAlarmsSorted as getActiveAlarms };

