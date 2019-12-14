"""This module descibes all things last.

This is a helper system so that submodules can see when the last did
something, from the last email they checked to the last time they were
ran.  It is intentionally vague.

"""
from peewee import CharField

from . import Model


class Last(Model):
    """The simple last model."""

    key = CharField(primary_key=True)
    value = CharField()
