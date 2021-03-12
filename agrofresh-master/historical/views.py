from asgiref.sync import sync_to_async
from cold_rooms.models import ColdRoom
from collections import Counter
from comms.structs import DataStruct
from comms.tags import ALARM, PARAM
from core.models import Typed
from core.settings import TIME_ZONE
from datetime import timedelta
# from django.contrib.auth.decorators import login_required, permission_required
from decorators.auth import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import connection, connections
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from functools import reduce
from historical import models, forms
from plotly.offline import plot
from plotly.subplots import make_subplots
import asyncio
import csv
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def group_by(iterable, key_fn):
    groups = {}
    for item in iterable:
        key = key_fn(item)
        groups[key] = groups.get(key, [])
        groups[key].append(item)
    return groups


@sync_to_async
def get_cold_rooms_all():
    return list(ColdRoom.objects.all())


def tz_convert(df):
    assert isinstance(df, pd.DataFrame)

    datetime64_cols = [
        col
        for col in df.columns
        if isinstance(df[col].dtype, pd.core.dtypes.dtypes.DatetimeTZDtype)
    ]

    for col in datetime64_cols:
        df[col] = df[col].dt.tz_convert(TIME_ZONE)

    return df


def execute_query(query, **args):
    with connection.cursor() as cursor:
        cursor.execute(query, args)
        df = pd.DataFrame(
            cursor.fetchall(),
            columns=[col[0] for col in cursor.description],
        )
        return tz_convert(df)


get_downsampled_data_query = lambda func_name: f'''
    SELECT ts as time, value, cold_room_id, measurement_id
    FROM {func_name}(%(to_ts)s, %(from_ts)s, %(points)s, %(sample_time)s)
    -- LIMIT %(points)s
    '''

@sync_to_async
def get_numeric_data(cold_rooms, measurements, params):
    measurement_dtypes = [
        (models.FloatData, filter(lambda m: m.type == Typed.Type.FLOAT, measurements), "historical_floatdata_downsampled"),
        (models.IntegerData, filter(lambda m: m.type == Typed.Type.INT, measurements), "historical_integerdata_downsampled"),
    ]

    data = [
        execute_query(query, **args)
        for dtype, type_measurements, func_name in measurement_dtypes
        if (query := get_downsampled_data_query(func_name))
        if (cold_room_ids := tuple(c.id for c in cold_rooms))
        if (measurement_ids := tuple(m.id for m in type_measurements))
        if (args := {
            **params,
            'cold_rooms': cold_room_ids,
            'measurements': measurement_ids,
        })
    ]

    data = pd.concat(data, ignore_index=True) if data else pd.DataFrame(
        columns=['cold_room_id', 'measurement_id', 'time', 'value']
    )

    data = (data
        .astype({ 'value': np.float32 })
        .set_index(['cold_room_id', 'measurement_id', 'time'])
        .sort_values(['cold_room_id', 'measurement_id', 'time']))

    return data

@sync_to_async
def get_boolean_data(cold_rooms, measurements, params):
    if not cold_rooms or not measurements:
        return pd.DataFrame()

    query = f'''
    SELECT
        d.ts as time,
        d.value as value,
        cold_room_id, measurement_id
    FROM {models.BooleanData._meta.db_table} as d
    WHERE cold_room_id in %(cold_room_id)s
        AND measurement_id in %(measurement_id)s
        AND d.ts BETWEEN %(to_ts)s AND %(from_ts)s
    GROUP BY time, cold_room_id, measurement_id, value
    ORDER BY time DESC
    LIMIT %(points)s
    '''
    args = {
        **params,
        'cold_room_id': tuple(c.id for c in cold_rooms),
        'measurement_id': tuple(m.id for m in measurements),
        'points': 10000 # * len(cold_rooms) * len(measurements)
    }
    data = execute_query(query, **args)
    data = (data
        .astype({ 'value': bool })
        .set_index(['cold_room_id', 'measurement_id', 'time'])
        .sort_values(['cold_room_id', 'measurement_id', 'time']))

    def compute_events(df):
        events = df.join(df.shift(), rsuffix='_shifted')
        events = events[events.value_shifted == True]
        events = events[['time', 'time_shifted']]
        events = events.rename(columns={
            'time': 'finish',
            'time_shifted': 'start',
        })
        events = events.assign(duration=lambda row: row.finish - row.start)
        events = events.assign(active_time=events['duration'].sum())

        # pretty print timedelta64 (duration & active_time)
        events['duration'] = events['duration'].astype(str)
        events['active_time'] = events['active_time'].astype(str)
        return events

    def get_event_data(data, cold_room, measurement):
        try:
            return data.loc[cold_room.id, measurement.id].reset_index()
        except KeyError:
            return None

    data = [
        compute_events(df)
            .assign(id=f"{measurement.name} @ {cold_room.name}")
            .assign(cold_room_id=cold_room.id)
            .assign(measurement_id=measurement.id)
        for cold_room in cold_rooms
        for measurement in measurements
        if ((df := get_event_data(data, cold_room, measurement)) is not None)
    ]
    return pd.concat(data) if data else pd.DataFrame()


@sync_to_async
def get_selected_measurements(form):
    if form \
    and form.is_valid() \
    and (measurements := form.cleaned_data.get('measurements')):
        return [
            models.Measurement.objects.get(pk=int(pk))
            for pk in measurements
        ]

    return list(models.Measurement.objects.filter(enabled=True))


@sync_to_async
def get_historical_data_filter_params(form):
    now = timezone.now()
    params = {
        "from_ts": now,
        "to_ts": now - timedelta(days=7),
        "points": 1000, # or models.MeasurementDataDownsampled.DEFAULT_POINTS,
        "sample_time": timedelta(seconds=1),
    }

    if not form or not form.is_valid():
        return params

    if (ts_range := form.cleaned_data.get('ts_range')) and ts_range[0] and ts_range[1]:
        params = {
            **params,
            "from_ts": ts_range[1],
            "to_ts": ts_range[0],
        }

    return params


def get_traces_from_measurements(data, cold_rooms, measurements):
    traces = [
        *get_traces_from_numeric_measurements(data.get('numeric'), cold_rooms, measurements.get('numeric')),
        *get_traces_from_boolean_measurements(data.get('boolean'), cold_rooms, measurements.get('boolean')),
    ]

    # compute rows
    key_fn = lambda x: x.get('title')
    groups = group_by(traces, key_fn)
    traces = [
        { **trace,'row': 1 + n, 'col': 1 }
        for n, group in enumerate(groups.items())
        for trace in group[1]
    ]
    return traces


def get_traces_from_numeric_measurements(data, cold_rooms, measurements):
    indexes = set((c, m) for c, m, ts in  data.index.values.tolist())
    def get_title_safe(measurement):
        try:
            # return f"{measurement.name} - {measurement.description}"
            return str(measurement.description)
        except:
            return "--"

    yield from (
        {
            'title': title,
            'trace': go.Scattergl(
                x = df.index,
                y = df.value.round(decimals=6),
                name=cold_room.name,
                mode="lines+markers",
                line=dict(color=px.colors.qualitative.Plotly[m]),
                legendgroup=cold_room.name,
                showlegend=(n == 0),
                opacity=0.8,
            ),
        }
        for n, measurement in enumerate(measurements)
        for m, cold_room in enumerate(cold_rooms)
        if (cold_room.id, measurement.id) in indexes
            and ((df := data.loc[cold_room.id, measurement.id]) is not None)
            and ((title := get_title_safe(measurement)))
    )


def get_traces_from_boolean_measurements(data, cold_rooms, measurements):
    if data.empty:
        return

    traces = (
        px.timeline(
            data,
            x_start="start",
            x_end="finish",
            y="id",
            hover_name="id",
            hover_data=["start", "finish", "duration", "active_time"]
        )
        .data
    ) or (go.Bar(),)

    yield from [
        {
            'title': str(_("Boolean measurements")),
            'trace': trace,
        }
        for n, trace in enumerate(traces)
    ]


def group_measurements_by_type(measurements):
    is_typed_boolean = lambda m: m.type == Typed.Type.BOOL
    is_not_typed_boolean = lambda m: not is_typed_boolean(m)
    return {
        'boolean': list(filter(is_typed_boolean, measurements)),
        'numeric': list(filter(is_not_typed_boolean, measurements)),
    }

async def get_data(params, cold_rooms, measurements):
    return {
        'numeric': await get_numeric_data(cold_rooms, measurements.get('numeric'), params),
        'boolean': await get_boolean_data(cold_rooms, measurements.get('boolean'), params),
    }


async def get_plotly_view(request, cold_rooms):
    if len(cold_rooms) == 0: # _("no cold rooms defined")
        return HttpResponse(go.Figure().to_json(), content_type="application/json")

    form = forms.HistoricalDataFilterForm(request.GET)
    measurements = await get_selected_measurements(form)
    measurements = group_measurements_by_type(measurements)

    if len(measurements) == 0: # _("no measurement enabled")
        return HttpResponse(go.Figure().to_json(), content_type="application/json")

    params = await get_historical_data_filter_params(form)
    data = await get_data(params, cold_rooms, measurements)
    traces = get_traces_from_measurements(data, cold_rooms, measurements)

    if not traces:
        fig = go.Figure()
        return HttpResponse(fig.to_json(), content_type="application/json")

    n_rows=len(set(trace.get('row') for trace in traces))
    n_cols=len(set(trace.get('col') for trace in traces))
    titles=Counter(trace.get('title') for trace in traces).keys()

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=list(titles),
        vertical_spacing=0.04,
        shared_xaxes=True,
    ).add_traces(
        [trace.get('trace') for trace in traces],
        rows=[trace.get('row') for trace in traces],
        cols=[trace.get('col') for trace in traces],
    ).update_layout(
        title=dict(text=str(_("Historical data"))),
        title_font_size=24,
        height=n_rows * 260,
    ).update_traces(
        xaxis=f'x{n_rows}',
    ).update_xaxes(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        # Force the visualization of the selected time range
        autorange=False,
        range=[params.get('to_ts'), params.get('from_ts')],
    )
    return HttpResponse(fig.to_json(), content_type="application/json")


@login_required
@permission_required('historical.can_view_historical_data', raise_exception=True)
async def historical_data_json(request):
    cold_rooms = await get_cold_rooms_all()
    return await get_plotly_view(request, cold_rooms)


@login_required
@permission_required('historical.can_view_historical_data', raise_exception=True)
async def cold_room_data_json(request, pk):
    cold_rooms = [await sync_to_async(get_object_or_404)(ColdRoom, pk=pk)]
    return await get_plotly_view(request, cold_rooms)


def data_to_csv_response(data, filename="historical_data.zip"):
    from io import BytesIO
    from zipfile import ZipFile

    in_memory = BytesIO()
    with ZipFile(in_memory, "a") as zip:
        for name, df in data.items():
            zip.writestr(f"{name}.csv", df.to_csv())

    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    in_memory.seek(0)
    response.write(in_memory.read())
    return response


@login_required
@permission_required('historical.can_view_historical_data', raise_exception=True)
async def historical_data_csv(request):
    """Returns the historical data (CSV)."""
    cold_rooms = await get_cold_rooms_all()
    form = forms.HistoricalDataFilterForm(request.GET)
    measurements = await get_selected_measurements(form)
    measurements = group_measurements_by_type(measurements)
    params = await get_historical_data_filter_params(form)
    data = await get_data(params, cold_rooms, measurements)
    return data_to_csv_response(data)


@login_required
@permission_required('historical.can_view_historical_data', raise_exception=True)
async def cold_room_data_csv(request, pk):
    """Returns the historical data (CSV)."""
    cold_rooms = [await sync_to_async(get_object_or_404)(ColdRoom, pk=pk)]
    form = forms.HistoricalDataFilterForm(request.GET)
    measurements = await get_selected_measurements(form)
    measurements = group_measurements_by_type(measurements)
    params = await get_historical_data_filter_params(form)
    data = await get_data(params, cold_rooms, measurements)
    return data_to_csv_response(data)


# TODO move from func view to class views
@login_required
@permission_required('historical.can_view_historical_data', raise_exception=True)
def historical_data(request):
    form = forms.HistoricalDataFilterForm(request.GET)
    context = {
        "title": _("Cold Rooms - Historical Data"),
        "data_src": reverse('historical:data_json'),
        "form": form,
    }
    return render(request, "historical_data.html", context)


@login_required
@permission_required('historical.can_view_historical_data', raise_exception=True)
def cold_room_data(request, pk):
    form = forms.HistoricalDataFilterForm(request.GET)
    cold_room = get_object_or_404(ColdRoom, pk=pk)
    context = {
        "title": _("%(cold_room_name)s - Historical Data") % {
            "cold_room_name": cold_room.name,
        },
        "data_src": reverse('historical:cold_room_data_json', args=[pk]),
        "form": form,
    }
    return render(request, "historical_data.html", context)


class EventsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ('historical.can_view_events', )
    # TODO FormMixin
    # https://flowfx.de/blog/django-crispy-forms-and-the-cancel-button/
    model = models.Event
    context_object_name = 'events'
    template_name = 'events_list.html'
    paginate_by = 15
    ordering = ['-ts']
    form_class = forms.EventsViewFilterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url'] = reverse('historical:events')
        context['form'] = self.form or self.form_class()
        return context

    def get_queryset(self):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return super().get_queryset()

        queryset = self.model.objects
        args = self.form.cleaned_data
        OR = lambda a, b: a | b

        if ((ts_range := args.get('ts_range')) and ts_range[0] and ts_range[1]):
            queryset = queryset.filter(ts__range=ts_range)

        if (event_type := args.get('event_type')):
            q_filter = (Q(type=event_id) for event_id in event_type)
            queryset = queryset.filter(reduce(OR, q_filter))

        if (alarm := args.get('alarm')):
            q_filter = (Q(meta__alarm=alarm.id) for alarm in [alarm])
            queryset = queryset.filter(reduce(OR, q_filter))

        if (parameter := args.get('parameter')):
            q_filter = (Q(meta__parameter=param.id) for param in [parameter])
            queryset = queryset.filter(reduce(OR, q_filter))

        if (tags := args.get('tags')):
            fields = list(DataStruct.get_fields_tagged_as(*tags))
            alarms_lut = {a['name']: a['id'] for a in models.Alarm.objects.values('id', 'name')}
            params_lut = {p['name']: p['id'] for p in models.Parameter.objects.values('id', 'name')}

            alarms = [
                pk
                for f in fields
                if ALARM in f.metadata.get('tags')
                and (pk := alarms_lut.get(f.metadata.get('path')))
            ]

            params = [
                pk
                for f in fields
                if PARAM in f.metadata.get('tags')
                and (pk := params_lut.get(f.metadata.get('path')))
            ]

            q_filter = [Q(meta__alarm__in=alarms), Q(meta__param__in=params)]
            queryset = queryset.filter(reduce(OR, q_filter))

        if (cold_rooms := args.get('cold_room')):
            q_filter = (Q(meta__cold_room=croom.id) for croom in cold_rooms)
            queryset = queryset.filter(reduce(OR, q_filter))

        if (ordering := self.get_ordering()):
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


class EventsCsvView(EventsView):
    def render_to_response(self, context):
        queryset = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="events.csv"'

        writer = csv.writer(response)
        writer.writerow(['ts', 'type', 'description', 'value'])
        for event in queryset:
            writer.writerow([event.ts, event.type, event.description, event.value])

        return response