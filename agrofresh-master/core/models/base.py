from core.fields import SortOrderField
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _


class TreeNode(models.Model):
    parent = models.ForeignKey('self',
        on_delete=models.CASCADE,
        verbose_name=_('parent'),
        help_text=_('parent help text'),
        related_name=_('children'))

    class Meta:
        abstract = True


class Named(models.Model):
    name = models.CharField(
        max_length=70,
        verbose_name=_('name'),
        help_text=_('name help text'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Described(models.Model):
    description = models.CharField(
        max_length=200,
        verbose_name=_('description'),
        help_text=_('description help text'))

    class Meta:
        abstract = True


class Enablable(models.Model):
    enabled = models.BooleanField(
        default=True,
        verbose_name=_('enabled'),
        help_text=_('enabled help text'))

    class Meta:
        abstract = True


class Timestamped(models.Model):
    ts = models.DateTimeField(
        verbose_name=_('timestamp'),
        help_text=_('timestamp help text'))

    class Meta:
        abstract = True


class Typed(models.Model):
    class Type(models.TextChoices):
        __empty__ = _('(Unknown)')
        BOOL  = 'bool',   _('boolean')
        INT   = 'int',    _('integer')
        FLOAT = 'float',  _('float')

        @classmethod
        def from_type(cls, type):
            members = {
                v.value: v
                for _, v in cls.__members__.items()
            }
            members = {
                **members,
                'u16': cls.INT,
                'u32': cls.INT,
                'u64': cls.INT,
                'i16': cls.INT,
                'i32': cls.INT,
                'i64': cls.INT,
                'f32': cls.FLOAT,
                'f64': cls.FLOAT,
            }
            return members.get(type.__name__, cls.__empty__)


        @classmethod
        def from_type(cls, type):
            members = {
                v.value: v
                for _, v in cls.__members__.items()
            }
            members = {
                **members,
                'u16': 'int',
                'u32': 'int',
                'u64': 'int',
                'i16': 'int',
                'i32': 'int',
                'i64': 'int',
                'f32': 'float',
                'f64': 'float',
            }
            return members.get(type.__name__, cls.__empty__)

    type = models.TextField(
        default=Type.__empty__,
        choices=Type.choices,
        verbose_name=_('type'),
        help_text=_('type help text'))

    class Meta:
        abstract = True


class Sortable(models.Model):
    sort_order = SortOrderField(_('Sort'), default=0) # blank=False, null=False

    class Meta:
        abstract = True
        ordering = ('sort_order',)

    # class QuerySet(models.QuerySet):

    #     def normalize_sort_order(self):
    #         models = self.all()
    #         for n, model in enumerate(models, start=1):
    #             model.sort_order = n
    #         self.bulk_update(models, ('sort_order',))

    # Manager = QuerySet.as_manager
    # # objects = Manager()


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def __str__(self):
        return str(self._meta.verbose_name)
