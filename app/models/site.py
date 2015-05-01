#!/usr/bin/python
# -*- coding: UTF-8 -*-

from peewee import Model
from peewee import CharField
from app.services.database import get_db


class Site(Model):
    name = CharField(unique=True)
    url = CharField()
    token = CharField()

    class Meta:
        database = get_db()
