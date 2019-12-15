from peewee import BlobField, BooleanField, CharField, DateTimeField

from . import Model


class Notification(Model):
    created = DateTimeField()
    message = CharField()
    response_required = BooleanField()
    response = CharField(null=True)
    photo = BlobField(null=True)
    telegram_id = CharField(null=True)
    posed = BooleanField(default=False)
