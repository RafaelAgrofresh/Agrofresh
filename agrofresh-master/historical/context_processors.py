from django.forms.models import model_to_dict
from .models import Settings


def settings(request):
    settings = Settings.load()
    # TODO measurements are not JSON serializable
    context = {
        "settings": {
            "show_unack_alarms": settings.show_unack_alarms,
        },
    }
    return context