import django.dispatch

app_start = django.dispatch.Signal()
app_stop  = django.dispatch.Signal()

# @django.dispatch.receiver(app_start)
# def app_start_callback(sender, **kwargs):
#     print("app_start_callback!")

# @django.dispatch.receiver(app_stop)
# def app_stop_callback(sender, **kwargs):
#     print("app_stop_callback!")