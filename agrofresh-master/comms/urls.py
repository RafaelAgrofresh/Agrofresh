from django.urls import path
from . import views

app_name = "comms"
urlpatterns = [
    path("", views.index, name="index"),
    path("write", views.write, name="write"),
    path("set_working_mode", views.set_working_mode, name="set_working_mode"),
    path("ack_alarms", views.acknowledge_alarms, name="ack_alarms"),
    path("accept_message", views.accept_message, name="accept_message"),
    path("mmap", views.mmap, name="mmap"),
    path("mmap_header", views.mmap_header, name="mmap_header"),
    # TODO can we reduce endpoints to single endpoint?
    # receives serialized commands/queries, deserialize, dispatches and return response,
    # the handlers generates events and returns results
    # the views are reduced to return cmd_bus.dispatch(command)
]
