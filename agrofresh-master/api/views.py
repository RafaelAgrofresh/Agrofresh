from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from cold_rooms.models import ColdRoom
from historical.models import (
    Event,
    BooleanData,
    IntegerDataDownsampled,
    FloatDataDownsampled,
    MeasurementDataDownsampled,
)
import csv
import json
import asyncio

field_type_LUT = {
    "BooleanField"  : "bool",
    "DecimalField"  : "float",
    "FloatField"    : "float",
    "IntegerField"  : "int",
    "ForeignKey"    : "fk",
    "DateTimeField" : "datetime",
}

def cold_rooms(request):
    data = {
        "data": [
            {
                **model_to_dict(cold_room),
                'parameters' : reverse('api:cold_room_params', args=[cold_room.id]),
                'historical_data' : reverse('api:cold_room_data', args=[cold_room.id]),
                'historical_events' : reverse('api:cold_room_events', args=[cold_room.id]),
            }
            for cold_room in ColdRoom.objects.all()
        ]
    }
    return JsonResponse(data)


def get_columns(model_class):
    return [
        {
            "name": field.name,
            "desc": field.help_text or field.verbose_name or field.name,
            "type": field_type_LUT.get(field.get_internal_type(), "str"),
        }
        for field in model_class._meta.get_fields()
        if field.name != "id"
    ]


def historical_data(request):
    form = MeasurementDataDownsampled.Form(request.GET)
    if not form.is_valid():
        return JsonResponse(
            {'errors': form.errors.get_json_data(escape_html=False)},
            status=400,
        )

    params = form.cleaned_data
    queryset = FloatDataDownsampled.objects.table_function(
        from_ts=params.get('from_ts'),
        to_ts=params.get('to_ts'),
        cold_room_id=params.get('cold_room_id'),
        measurement_id=params.get('measurement_id'),
        points=params.get('points') or MeasurementDataDownsampled.DEFAULT_POINTS,
    )
    rows = [model_to_dict(d) for d in queryset]
    cols = []
    # cols = ('ts', 'cold_room_id', 'measurement_id', 'avg', 'max', 'min')
    # rows = list(queryset.values_list(*cols))
    data = {"cols": cols, "rows": rows, "data": []} # TODO
    return JsonResponse(data)


def historical_events(request):
    raise NotImplementedError()
    """Return the latest N events."""
    data = Event.objects.order_by('-ts')[:N]
    data = [model_to_dict(d) for d in data]
    data = { "data": data }
    return JsonResponse(data)


def cold_room_data(request, pk):
    """Return the latest N measurements of the seleceted cold room."""
    cold_room = get_object_or_404(ColdRoom, pk=pk)
    # data = cold_room.measurements_data.order_by('-ts')[:N]
    data = cold_room.FloatData_set.order_by('-ts')[:N]
    # TODO view or QuerySet.union({float|integer|boolean}measurementdata_set)
    # QuerySet.union().order_by() throws 'RelatedManager' object has no attribute '_combinator_query'
    data = [model_to_dict(d) for d in data]
    data = { "cols": [], "rows": [], "data": data } # TODO: Unify API
    return JsonResponse(data)


def cold_room_events(request, pk):
    """Return the latest N events related to the seleceted cold room."""
    cold_room = get_object_or_404(ColdRoom, pk=pk)
    data = cold_room.events.order_by('-ts')[:N]
    data = [model_to_dict(d) for d in data]
    data = { "data": data }
    return JsonResponse(data)


def cold_room_params(request, pk):
    """Return the parameters of the seleceted cold room."""
    cold_room = get_object_or_404(ColdRoom, pk=pk)
    data = cold_room.parameters.order_by('parameter__name')
    data = [model_to_dict(d) for d in data]
    data = { "data": data }
    return JsonResponse(data)