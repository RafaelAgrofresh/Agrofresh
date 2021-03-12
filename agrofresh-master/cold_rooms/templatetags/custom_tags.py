from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.contrib.staticfiles import finders
from base64 import b64encode
import hashlib
import os

register = template.Library()

# https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity

def hash(algorithm, filename):
    hasher = hashlib.new(algorithm)
    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for block in iter(lambda: f.read(4096),b""):
            hasher.update(block)

    digest = hasher.digest()
    digest = b64encode(digest)
    digest = digest.decode("utf-8")
    return f'{algorithm}-{digest}'

@register.simple_tag
def static_script(url):
    url = str(url)
    fname = finders.find(url)
    url = static(url)
    digest = hash('sha384', fname)
    tag = f'<script integrity="{digest}" crossorigin="anonymous" src="{url}"></script>'
    return mark_safe(tag)

@register.simple_tag
def static_link(url):
    url = str(url)
    fname = finders.find(url)
    url = static(url)
    digest = hash('sha384', fname)
    tag = f'<link rel="stylesheet" integrity="{digest}" crossorigin="anonymous" href="{url}">'
    return mark_safe(tag)


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a param by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
