from asgiref.sync import sync_to_async
# from django.contrib.auth.decorators import login_required, permission_required
from decorators.auth import login_required, permission_required
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic
from comms.structs import DataStruct
from comms.mbus_types import MemMapped, EEPROM, u16, u32, i16, i32, f32
from comms.tasks import mbus
from cold_rooms.models import ColdRoom
from historical.models import events
import csv
import io
import json
import asyncio


@login_required
@permission_required('comms.can_view_comms_data', raise_exception=True)
def index(request):
    cold_rooms = ColdRoom.objects.all()
    return render(request, "comms/index.html", { "cold_rooms": cold_rooms })


@login_required # TODO check permissions
async def write(request):
    """Write handler request { "cold_room": <pk>, "property": str, "value": any }"""
    data = {}
    if request.method=='POST':
        data = json.loads(request.body.decode("utf-8"))
        cold_room_pk = int(data['cold_room'])
        client = next(client
            for client in mbus.clients
            if client.cold_room.id == cold_room_pk)

        path  = data['property']
        value = data['value']
        resp  = await client.write(path, value, request.user)
        data  = { **data, "result": resp }
    return JsonResponse({ "data": data })


@sync_to_async
def get_last_settings(cold_room, working_mode):
    return {
        param.name: event.value
        for event in events.Event.params.get_latest_settings(cold_room, working_mode)
        if (pk := event.meta.get('parameter'))
        and (param := events.Parameter.objects.get(pk=pk))
    }


@login_required
@permission_required('comms.can_set_working_mode', raise_exception=True)
async def set_working_mode(request):
    """set_working_mode request { "cold_room": <pk>, "value": bool }"""
    data = {}
    if request.method =='POST':
        data = json.loads(request.body.decode("utf-8"))
        cold_room_pk = int(data['cold_room'])
        value = bool(data['value'])
        settings = await get_last_settings(cold_room_pk, value)

        if not settings:
            # Handle the first time
            settings = { "workingMode": value }

        client = next(client
            for client in mbus.clients
            if client.cold_room.id == cold_room_pk)

        results = []
        for path, value in settings.items():
            result = await client.write(path, value, request.user)
            results.append((path, value, result))
        print(results)

        resp = {
            path: value for path, value, result in results if result
        }
        data  = { **data, "result": resp }
    return JsonResponse({ "data": data })


@login_required
@permission_required('comms.can_acknowledge_alarms', raise_exception=True)
def acknowledge_alarms(request):
    """Acknowledge alarms request { "cold_room": <pk> }"""
    data = {}
    if request.method=='POST':
        data = json.loads(request.body.decode("utf-8"))

        if cold_room_pk := data.get('cold_room'):
            cold_room = get_object_or_404(ColdRoom, pk=int(cold_room_pk))
        else:
            cold_room = None

        event = events.AcknowledgeAlarmsEvent(
            ts=timezone.now(),
            cold_room=cold_room,
            user=request.user.username,
        )
        event.save()

    return JsonResponse({ "data": event.to_dict() })


@login_required
@permission_required('comms.can_accept_messages', raise_exception=True)
def accept_message(request):
    """Accept message request { "cold_room": <pk>, "msg_id": <pk> }"""
    if request.method =='POST':
        data = json.loads(request.body.decode("utf-8"))
        cold_room_pk = int(data['cold_room'])
        msg_id = str(data['msg_id'])
        client = next(client
            for client in mbus.clients
            if client.cold_room.id == cold_room_pk)

        result = client.accept_message(msg_id)

    return JsonResponse({ "data": { "cold_room": cold_room_pk, msg_id: result } })


@login_required
@permission_required('comms.can_export_memory_map', raise_exception=True)
def mmap(request):
    """Returns the memory map (CSV)."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mmap.csv"'

    writer = csv.writer(response)
    writer.writerow(['Offset', 'Size', 'Type', 'Name', 'Desc', 'EEPROM', 'Tags'])
    for field in DataStruct.get_fields():
        if not isinstance(field, MemMapped):
            continue

        typename = field.type.__name__
        desc   = _(field.metadata.get('description', ''))
        offset = field.metadata.get('offset')
        size   = field.metadata.get('size')
        path   = field.metadata.get('path')
        eeprom = isinstance(field, EEPROM)
        tags   = ', '.join(field.metadata.get('tags', []))
        writer.writerow([offset, size, typename, path, desc, eeprom, tags])

    return response


@login_required
@permission_required('comms.can_export_memory_map', raise_exception=True)
def mmap_header(request):
    """Returns the memory map as C header."""

    content = io.StringIO(newline='\r\n')
    content.write(f"// mmap.h (auto-generated on {timezone.now()})\n")
    content.write(
        "#pragma once\n"
        "\n"
    )

    for field in DataStruct.get_fields():
        if not isinstance(field, MemMapped):
            continue

        path = field.metadata.get('path')
        if path.startswith('_'):
            continue

        if field.type is bool:
            content.write(
                "#define _reg_%(name)s %(offset)s\n"
                "#define _bit_%(name)s %(bit)s // %(typename)s - %(desc)s\n"
                % {
                    'name': '{:40s}'.format(path.replace('.', '_')),
                    'offset': '{:<5d}'.format(field.metadata.get('offset')),
                    'bit': '{:<5d}'.format(field.metadata.get('bit')),
                    'typename': field.type.__name__,
                    'desc': _(field.metadata.get('description', '')),
                }
            )

        else:
            content.write(
                "#define %(name)s %(offset)s"
                " // %(typename)s - %(desc)s\n"
                % {
                    'name': '{:45s}'.format(path.replace('.', '_')),
                    'offset': '{:<5d}'.format(field.metadata.get('offset')),
                    'typename': field.type.__name__,
                    'desc': _(field.metadata.get('description', '')),
                }
            )

    response = HttpResponse(content.getvalue(), content_type='text/plain; charset=utf-8')
    # response = HttpResponse(content, content_type='text/h; charset=utf-8')
    # response['Content-Disposition'] = 'attachment; filename="mmap.h"'
    return response
