import django.dispatch
import rx
from django.utils import timezone
from comms.signals import comms_alarm, comms_error
from core.signals import app_stop
from rx import operators as ops


channel = rx.subject.ReplaySubject()
ALARM = '⚠'
ERROR = '🚨'
TIME  = '⏱'

def dt_format(ts):
    return timezone.localtime(ts).strftime("%d/%m/%Y %H:%M:%S %z")

# Signal handlers are usually defined in a signals submodule of the application they relate to.
# Signal receivers are connected in the ready() method of the app config class, if you're using
# the receiver() decorator, import the signals submodule inside ready().


@django.dispatch.receiver(comms_error)
def notify_comms_error(sender, error, **kwargs):
    ts = dt_format(timezone.now())
    channel.on_next(f"{ERROR} CommsError::\"{error}\" [{TIME} {ts}]")


@django.dispatch.receiver(comms_alarm)
def notify_comms_alarm(sender, alarm, **kwargs):
    ts = dt_format(alarm.ts)
    channel.on_next(f"{ALARM} {alarm.type}::\"{alarm.description}\" [{TIME} {ts}]")


notifications = channel.pipe(
    ops.buffer_with_time(0.5),
    ops.filter(lambda x: x),
)

# @django.dispatch.receiver(app_stop)
# def stop_telegram_bot(sender, **kwargs):
#     # telegram.bot.stop()
#     # TODO stop bot?
#     pass