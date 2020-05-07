#!/usr/bin/env python
# encoding: utf-8

from peewee import *
from __init__ import db


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = db


class TblStatInfoDetail30m(BaseModel):
    id = BigAutoField()
    uname = CharField()
    worker = CharField()
    totaldiff = DecimalField()
    validcount = BigIntegerField()
    invalidcount = BigIntegerField()
    periodtime = DateTimeField()

    class Meta:
        table_name = 'tbl_stat_info_detail_30m'


