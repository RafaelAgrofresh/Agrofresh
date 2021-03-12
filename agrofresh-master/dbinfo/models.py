from django import forms
from django.db import connection, models
from django.db.models import Count, F, Func, Sum
from django.db.models.functions import Cast
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _


class ViewMixin:
    @classmethod
    def create_or_replace(cls):
        raise NotImplementedError()

    @classmethod
    def drop(cls):
        SQL = "drop view if exists %(view_name)s" % {
            'view_name': cls._meta.db_table
        }
        with connection.cursor() as cursor:
            cursor.execute(SQL)

class TableInfo(ViewMixin, models.Model):
    """
    Information about tables.
    """
    table_name = models.TextField(
        primary_key=True,
        verbose_name=_('table name'),
        help_text=_('Table name of the table'),
    )

    is_hypertable = models.BooleanField(
        verbose_name=_('is hypertable'),
        help_text=_('Indicates if the table is a timescaleDB hypertable'),
    )

    table_size = models.PositiveBigIntegerField(
        verbose_name=_('table size'),
        help_text=_('Disk space used by table data'),
    )

    index_size = models.PositiveBigIntegerField(
        verbose_name=_('index size'),
        help_text=_('Disk space used by indexes'),
    )

    total_size = models.PositiveBigIntegerField(
        verbose_name=_('total size'),
        help_text=_('Total disk space used by the table (data + indexes)'),
    )

    class QuerySet(models.QuerySet):
        def summary(self):
            metrics = {
                'tables':      Count('table_name'),
                'hypertables': Sum(Cast('is_hypertable', models.IntegerField())),
                'table_size':  Sum('table_size'),
                'index_size':  Sum('index_size'),
                'total_size':  Sum('total_size'),
            }
            return self.aggregate(**metrics)

    objects = QuerySet.as_manager()

    class Meta:
        managed = False
        db_table = "tables_info"
        verbose_name = _("Table Information")
        verbose_name_plural = _("Tables Information")

    @classmethod
    def create_or_replace(cls):
        SQL = """create or replace view %(view_name)s as
        select r.table_name, r.is_hypertable,
            r.table_size, r.index_size, r.total_size,
            (r.total_size::float / pg_database_size(current_catalog)  * 100) as tpc
        from (
            select t.table_name,
                not h.table_name is null as is_hypertable,
                GREATEST(
                    pg_table_size(quote_ident(t.table_name)), -- includes TOAST
                    (select coalesce(table_bytes, 0) + coalesce(toast_bytes, 0)
                        from hypertable_relation_size(quote_ident(h.table_name)))
                ) as table_size,
                GREATEST(
                    pg_indexes_size(quote_ident(t.table_name)),
                    (select coalesce(index_bytes, 0)
                        from hypertable_relation_size(quote_ident(h.table_name)))
                ) as index_size,
                GREATEST(
                    pg_total_relation_size(quote_ident(t.table_name)),
                    (select coalesce(total_bytes, 0)
                        from hypertable_relation_size(quote_ident(h.table_name)))
                )  as total_size
            from information_schema.tables as t
            left join timescaledb_information.hypertable as h
            on h.table_name = t.table_name
            where t.table_schema = 'public'
            and t.table_type like '%%TABLE%%') as r""" % {
            'view_name': cls._meta.db_table
        }
        with connection.cursor() as cursor:
            cursor.execute(SQL)
