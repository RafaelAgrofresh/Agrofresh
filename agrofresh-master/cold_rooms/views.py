from cold_rooms import models
from django.contrib.auth.decorators import login_required, permission_required
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from historical.models import Alarm
import json


@login_required
def index(request):
    return render(request, "index.html")


@login_required
@permission_required('cold_rooms.can_view_cold_rooms_summary')
def cold_room_index(request):
    cold_rooms = models.ColdRoom.objects.all()
    context = { "cold_rooms": cold_rooms }
    return render(request, "cold_room/index.html", context)


@login_required
@permission_required('cold_rooms.can_view_cold_room_params', raise_exception=True)
def cold_room_params(request, pk):
    cold_room = get_object_or_404(models.ColdRoom, pk=pk)
    context = { "cold_room": cold_room }
    return render(request, "cold_room/params.html", context)


@login_required
@permission_required('cold_rooms.can_view_cold_room_detail', raise_exception=True)
def cold_room_detail(request, pk):
    cold_room = get_object_or_404(models.ColdRoom, id=pk)
    links = [
        {
            "name": c.name,
            "url": reverse('cold_room_detail', args=[c.id]),
        }
        for c in models.ColdRoom.objects.all()
    ]
    context = {
        "cold_room": cold_room,
        "links": links,
    }
    return render(request, "cold_room/detail.html", context)
