from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from uuid import UUID
from .. import models


register = template.Library()


def is_logged_event_type(value):
    return isinstance(value, str) and value in models.AuthEvent.Type.values


def is_uuid4(value):
    if not isinstance(value, (str, UUID)):
        return False

    if isinstance(value, UUID):
        return value.version == 4

    try:
        uuid4 = UUID(value, version=4)
    except ValueError:
        return False

    return str(uuid4) == value or uuid4.hex == value


event_styles = {
    # scls.__name__: scls for scls in models.events.BaseEvent.__subclasses__()
    'AuthEvent': { 'class': models.events.AuthEvent, 'color': 'info', 'icon': 'cil-user' },
    'AlarmEvent': { 'class': models.events.AlarmEvent, 'color': 'warning', 'icon': 'cil-warning' },
    'AcknowledgeAlarmsEvent': { 'class': models.events.AcknowledgeAlarmsEvent, 'color': 'primary', 'icon': 'cil-check-circle' }, # cil-thumb-up
    'ParameterChangeEvent': { 'class': models.events.ParameterChangeEvent, 'color': 'secondary', 'icon': 'cil-settings' },
    'ParameterChangeCommand': { 'class': models.events.ParameterChangeCommand, 'color': 'dark', 'icon': 'cil-equalizer' },
}


def icon_template(icon, classes=set()):
    classes = ' '.join({ 'c-icon' }.union(set(classes)))
    return f'<svg class="{classes}"><use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#{icon}"></use></svg>'


def remove_suffix(str_value, suffix):
    if (not suffix
        or not str_value
        or not str_value.endswith(suffix)):
        return str_value

    return str_value[:-len(suffix)]

@register.filter(name='event_type', is_safe=True)
def event_type_fmt(value):
    style = event_styles.get(value)
    if not style: return value
    value = style['class'].__name__
    # TODO use str.removesuffix python>=3.9
    value = _(remove_suffix(value, 'Event'))
    color = style.get('color', 'info')
    icon = style.get( 'icon', 'info')
    icon = icon_template(icon, {'mr-1'})
    return mark_safe(f"{icon}<span class='badge badge-{color}'>{value}</span>")


@register.filter(name='event_value')
def event_value_fmt(value):
    if isinstance(value, bool):
        if value:
            icon = icon_template('cil-asterisk-circle', {'mr-1', 'text-danger' })
            value = _("activado")
        else:
            icon = icon_template('cil-circle', {'mr-1'})
            value = _("desactivado")
        return mark_safe(f"{icon}<span>{value}</span>")

    if is_uuid4(value):
        icon = icon_template('cil-fingerprint', {'mr-1'})
        return mark_safe(f"<span title='UUID4({value})'>{icon} <span>uuid4</span></span>")

    if is_logged_event_type(value):
        return models.AuthEvent.Type(value).label

    return value