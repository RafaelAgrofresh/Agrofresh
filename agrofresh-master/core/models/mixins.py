from django.db import models


class classproperty(property):
    def __get__(self, cls, owner):
      return self.fget.__get__(None, owner)()


class InheritanceParentMixin:
    @classproperty
    @classmethod
    def subclass_object_choices(cls):
        "All known subclasses, keyed by a unique name per class."
        return {
            rel.name: rel.related_model
            for rel in cls._meta.related_objects
            if rel.parent_link
        }

    @classproperty
    @classmethod
    def subclass_choices(cls):
        "Available subclass choices, with nice names."
        return [
            (name, model._meta.verbose_name)
            for name, model in cls.subclass_object_choices.items()
        ]

    @classmethod
    def get_subclass(cls, name):
        "Given a subclass name, return the subclass."
        return cls.subclass_object_choices.get(name, cls)


class LookUpTableMixin:
    @classmethod
    def update(cls):
        raise NotImplementedError()


class SaveOnValueChangeMixin:
    _cached = {}

    def get_cache_key(self):
        """hashable object used to identify the model instance"""
        # NOTE: _cached is shared between all derived classes,
        # so add a reference to the subtype # in the key
        # (e. g. (self.__class__, self.ref1.pk, self.ref2.pk))
        raise NotImplementedError()

    def get_latest_value(self):
        """returns the latest saved value"""
        raise NotImplementedError()

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not hasattr(self, 'value'):
            raise TypeError('value property required')

        key = self.get_cache_key()

        if not key in self._cached:
            self._cached[key] = self.get_latest_value()

        if self._cached[key] == self.value:
            return # Save changes only

        # Create a new instance instead of updating an existing one
        if self.pk is not None:
            raise Exception(
                f'{self.__class__.name} pk={self.pk} already saved'
                '\nCreate a new instance instead of updating an existing one'
            )

        super().save(force_insert, force_update, *args, **kwargs)
        self._cached[key] = self.value
