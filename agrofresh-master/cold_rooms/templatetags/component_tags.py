from django import template
from cold_rooms import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from comms.structs import DataStruct


register = template.Library()


@register.inclusion_tag('../templates/cold_room/card.html', takes_context=True)
def cold_room_card(context, cold_room):
    # Can be replaced with an include tag
    # {% include "cold_room/card.html" with cold_room=cold_room %}
    # takes_context=True is needed to access current context vars like 'perms'
    return { 'cold_room': cold_room, 'perms': context.get('perms') }


@register.inclusion_tag('../templates/messages_tag.html')
def show_messages(messages):
    return { 'messages': messages }


@register.simple_tag
def bg_class(number):
    return {
        1: "bg-gradient-dark",
        2: "bg-gradient-info",
        3: "bg-gradient-success",
        4: "bg-gradient-danger",
    }.get(number, "bg-gradient-primary")


@register.inclusion_tag('../templates/smallcard_tag.html')
def show_card(measurement):
    return {
        'title': '',
        'source': '',
        'unit': '',
        'classcolor': '',
        'imagesrc': '',
        'imagetip': '',
        'format': '',
        **measurement
    }


@register.inclusion_tag('../templates/alarms_table.html', takes_context=True)
def alarms_table(context, cold_room=None):
    data = {
        'fields': DataStruct.get_fields_lut(),
        'perms': context.get('perms')
    }
    if cold_room:
        return { **data, 'cold_room': cold_room }

    return data


@register.simple_tag(takes_context=True)
def navigation_items(context):
    user = context.get('user')
    return [
        {
            "url": reverse("cold_rooms"),
            "icon": "fa fa-snowflake-o",
            "label": _("Cold Rooms"),
            "enabled": (bool(user) and user.has_perm("cold_rooms.can_view_cold_rooms_summary")),
        },
        {
            "url": reverse("historical:data"),
            "icon": "fa fa-line-chart",
            "label": _("Historical"),
            "enabled": (bool(user) and user.has_perm("historical.can_view_historical_data")),
        },
        {
            "url": reverse("historical:events"),
            "icon": "fa fa-bell-o",
            "label": _("Event Log"),
            "enabled": (bool(user) and user.has_perm("historical.can_view_events")),
        },
    ]


@register.simple_tag
def measurement_items(cold_room=None):
    # TODO find a better place (view, model property)
    maesurements = [
        {
            'title': _('Indoor Temperature'),
            'source': 'temperatureInside',
            'unit': 'ºC',
            'classcolor': 'bg-gradient-dark',
            'imagesrc': '/static/assets/icons/cold_rooms/temperature.png',
            'imagetip': _('Temperatura en cámara'),
            'format': '.1f',
            'enabled': cold_room.enable_temperature_measurement if cold_room else True
        },
        {
            'title': _('Humidity'),
            'source': 'humidityInside',
            'unit': _('% RH'),
            'classcolor': 'bg-gradient-dark',
            'imagesrc': '/static/assets/icons/cold_rooms/humidity.png',
            'imagetip': _('Humedad en cámara'),
            'format': '.1f',
            'enabled': cold_room.enable_humidity_measurement if cold_room else True
        },
        {
            'title': _('Carbon dioxide'),
            'source': 'CO2Measure',
            'unit': 'CO2 ppm',
            'classcolor': 'bg-gradient-dark',
            'imagesrc': '/static/assets/icons/cold_rooms/co2.png',
            'imagetip': _('CO2 en cámara'),
            'format': '.0f',
            'enabled': cold_room.enable_CO2_measurement if cold_room else True
        },
        {
            'title': _('Ethylene'),
            'source': 'C2H4Measure',
            'unit': 'C2H4 ppm',
            'classcolor': 'bg-gradient-dark',
            'imagesrc': '/static/assets/icons/cold_rooms/etileno.png',
            'imagetip': _('Etileno en cámara'),
            'format': '.1f',
            'enabled': cold_room.enable_C2H4_measurement if cold_room else True
        },
    ]

    return filter(lambda m: m['enabled'], maesurements)

@register.simple_tag
def status_icon_items():
    return [
        {
            "src": "systemOn",
            "imgsrc": "/static/assets/icons/cold_rooms/play.png",
            "title": _("Cámara en marcha"),
        },
        {
            "src": "systemOff",
            "imgsrc": "/static/assets/icons/cold_rooms/stop.png",
            "title": _("Cámara en paro"),
        },
        {
            "src": "anyAlarm",
            "imgsrc": "/static/assets/icons/cold_rooms/bell.png",
            "title": _("Existen alarmas en cámara"),
        },
        {
            "src": "openDoor",
            "imgsrc": "/static/assets/icons/cold_rooms/opendoor.png",
            "title": _("Puerta abierta"),
        },
        {
            "src": "heaterOn",
            "imgsrc": "/static/assets/icons/cold_rooms/flame.png",
            "title": _("Calor activado"),
        },
        {
            "src": "fridgeOn",
            "imgsrc": "/static/assets/icons/cold_rooms/cold.png",
            "title": _("Frío activado"),
        },
    ]


@register.filter
def ntimes(value, arg):
    """Product of two values"""
    return f"{float(value) * float(arg)}"