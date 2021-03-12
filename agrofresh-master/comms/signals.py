import django.dispatch


comms_start = django.dispatch.Signal()
comms_error = django.dispatch.Signal(providing_args=['error'])
comms_alarm = django.dispatch.Signal(providing_args=['alarm'])

# Signal handlers are usually defined in a signals submodule of the application they relate to.
# Signal receivers are connected in the ready() method of the app config class, if you're using
# the receiver() decorator, import the signals submodule inside ready().


### SENDING SIGNALS
# comms_start.send(sender=self.__class__)
# comms_error.send(sender=self.__class__, error=error, cold_room=cold_room)
# comms_alarm.send(sender=self.__class__, alarm=alarm)


### CONNECTING RECEIVER FUNCTIONS
# import logging
# from django.utils import timezone
# logger = logging.getLogger(__name__)


# @django.dispatch.receiver(comms_error)
# def log_comms_error(sender, **kwargs):
#     logger.warn(f"comms error @ {timezone.now()} {kwargs}")


# @django.dispatch.receiver(comms_alarm)
# def log_comms_alarm(sender, **kwargs):
#     logger.warn(f"comms alarm @ {timezone.now()} {kwargs}")
