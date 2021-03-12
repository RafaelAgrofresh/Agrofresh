from django.db import models


class SortOrderField(models.PositiveIntegerField):
    description = "A value for sorting model instances"

    # TODO improve
    # https://github.com/dylanmccall/django-sort-order-field
    # https://github.com/andersinno/django-sorting-field
