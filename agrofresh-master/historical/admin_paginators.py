from django.core.paginator import Paginator
from sys import maxsize

# TODO cursor paginator?
# https://github.com/photocrowd/django-cursor-pagination

# TODO https://blog.ionelmc.ro/2020/02/02/speeding-up-django-pagination/
# use hypertable_approximate_row_count() ?

class DumbPaginator(Paginator):
    """
    Paginator that does not count the rows in the table.
    """
    @cached_property
    def count(self):
        return maxsize