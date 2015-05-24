#!/usr/bin/python
# -*- coding: UTF-8 -*-

from peewee import Model
from peewee import CharField
from peewee import ForeignKeyField
from app.services.database import get_db
from app.models.site import Site


class Reader(Model):
    url = CharField()
    email = CharField(default='')
    site = ForeignKeyField(Site, related_name='reader_site')

    class Meta:
        database = get_db()