from django import template


register = template.Library()

@register.filter
def belongs_to(user, group_name):
    return user.groups.filter(name=group_name).exists()