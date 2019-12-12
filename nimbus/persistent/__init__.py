import peewee

db = peewee.SqliteDatabase("database.db")


class Model(peewee.Model):
    class Meta:
        database = db
