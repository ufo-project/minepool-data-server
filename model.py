#!/usr/bin/env python
# encoding: utf-8

from peewee import *

database_proxy = DatabaseProxy()


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database_proxy
        pass


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


class TblStatInfoTotal30m(BaseModel):
    id = BigAutoField()
    totaldiff = DecimalField()
    hashrate = DecimalField()
    validcount = BigIntegerField()
    invalidcount = BigIntegerField()
    periodtime = DateTimeField()

    class Meta:
        table_name = 'tbl_stat_info_total_30m'



