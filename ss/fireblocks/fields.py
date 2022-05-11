from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import gettext_lazy as _


class NullTextField(models.TextField):
    """
    Subclass of the TextField that allows empty strings to be stored as NULL.
    Based upon https://gist.github.com/otov4its/4543540f3f893122ece654d81fee80bc
    """

    description = _("TextField that stores '' as None and returns None as ''")

    def __init__(self, *args, **kwargs):
        if not kwargs.get('null', True) or not kwargs.get('blank', True):
            raise ImproperlyConfigured('NullCharField implies null==blank==True')
        kwargs['null'] = kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        """
        Gets value right out of the db and changes it if its ``None``.
        """
        if value is None:
            return ''
        else:
            return value

    def to_python(self, value):
        """
        Gets value right out of the db or an instance, and changes it if its ``None``.
        """
        val = super().to_python(value)
        return '' if val is None else val

    def get_prep_value(self, value):
        """
        Catches value right before sending to db.
        """
        prep_value = super().get_prep_value(value)
        # If Django tries to save an empty string, send the db None (NULL).
        return None if prep_value == '' else prep_value

    def deconstruct(self):
        """
        For migration purposes
        """
        name, path, args, kwargs = super().deconstruct()
        del kwargs['null']
        del kwargs['blank']
        return name, path, args, kwargs
