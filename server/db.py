import datetime
from peewee import SqliteDatabase, Model, DateTimeField, CharField, TextField, BooleanField


db = SqliteDatabase('app.db', pragmas={'journal_mode': 'wal'})


class BaseModel(Model):
    class Meta:
        database = db


class CVRequest(BaseModel):
    class Meta:
        table_name = 'cv_request'

    email = CharField(index=True)
    name = TextField()
    note = TextField(null=True)
    token = TextField(unique=True)
    downloaded = BooleanField(default=False)
    created_date = DateTimeField(default=datetime.datetime.utcnow)
    downloaded_date = DateTimeField(null=True)


def check_tables(db_instance):
    models = [CVRequest]
    db_instance.bind(models)

    for model in models:
        exist = model.table_exists()
        if not exist:
            model.create_table()

def init_db():
    db.connect()
    check_tables(db)
    db.close()

def get_db():
    return db
