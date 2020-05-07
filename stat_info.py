#!/usr/bin/env python
# encoding: utf-8


import time
import json
import gevent
import leveldb
import __init__
from loguru import logger
from utils import get_format_date, get_format_datetime
from model import TblStatInfoDetail30m


class ShareInfo(object):
    def __init__(self, user_name, worker, share_diff, valid):
        self.user_name = user_name
        self.worker = worker
        self.share_diff = share_diff
        self.valid = valid


class StatInfo(object):
    def __init__(self, total_diff, valid_count, invalid_count):
        self.total_diff = total_diff
        self.valid_count = valid_count
        self.invalid_count = invalid_count

    def to_json(self):
        o = {
            "total_diff": self.total_diff,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count
        }
        return json.dumps(o)

    def from_json(self, s):
        o = json.loads(s)
        self.total_diff = o["total_diff"]
        self.valid_count = o["valid_count"]
        self.invalid_count = o["invalid_count"]
        return self


# total stat info (less than 30 minutes)
class TotalStatInfo30Min(object):
    total_info_map = {}

    @staticmethod
    def add_share_info(share_info):
        t = int(time.time())
        stat_info = TotalStatInfo30Min.total_info_map.get(t)
        if stat_info is None:
            stat_info = StatInfo(share_info.valid and share_info.share_diff or 0.0,
                                 share_info.valid and 1 or 0,
                                 share_info.valid and 0 or 1)
        else:
            stat_info.total_diff += share_info.valid and share_info.share_diff or 0.0
            stat_info.valid_count += share_info.valid and 1 or 0
            stat_info.invalid_count += share_info.valid and 0 or 1
        TotalStatInfo30Min.total_info_map[t] = stat_info


# 30 minutes
class DetailStatInfo30Min(object):
    period_start_timestamp = 0
    period_end_timestamp = 0
    stat_info_map = {}

    @staticmethod
    def add_share_info(share_info):
        k = ".".join([share_info.user_name, share_info.worker])
        stat_info = DetailStatInfo30Min.stat_info_map.get(k)
        if stat_info is None:
            stat_info = StatInfo(share_info.valid and share_info.share_diff or 0.0,
                                 share_info.valid and 1 or 0,
                                 share_info.valid and 0 or 1)
        else:
            stat_info.total_diff += share_info.valid and share_info.share_diff or 0.0
            stat_info.valid_count += share_info.valid and 1 or 0
            stat_info.invalid_count += share_info.valid and 0 or 1
        DetailStatInfo30Min.stat_info_map[k] = stat_info


# per minute
class DetailStatInfo1Min(object):
    period_start_timestamp = 0
    period_end_timestamp = 0
    stat_info_map = {}

    @staticmethod
    def add_share_info(share_info):
        k = ".".join([share_info.user_name, share_info.worker])
        stat_info = DetailStatInfo1Min.stat_info_map.get(k)
        if stat_info is None:
            stat_info = StatInfo(share_info.valid and share_info.share_diff or 0.0,
                                 share_info.valid and 1 or 0,
                                 share_info.valid and 0 or 1)
        else:
            stat_info.total_diff += share_info.valid and share_info.share_diff or 0.0
            stat_info.valid_count += share_info.valid and 1 or 0
            stat_info.invalid_count += share_info.valid and 0 or 1
        DetailStatInfo1Min.stat_info_map[k] = stat_info


def stat_info_init():
    t = time.time()
    DetailStatInfo1Min.period_start_timestamp = int(t) / 60 * 60
    DetailStatInfo1Min.period_end_timestamp = (int(t) / 60 + 1) * 60

    DetailStatInfo30Min.period_start_timestamp = int(t) / 1800 * 1800
    DetailStatInfo30Min.period_end_timestamp = (int(t) / 1800 + 1) * 1800


def run_statistics_task():
    gevent.spawn(statistics_task)


def statistics_task():
    while True:
        need_to_remove = [t for t in TotalStatInfo30Min.total_info_map.keys() if t < time.time() - 1800]
        for i in need_to_remove:
            del TotalStatInfo30Min.total_info_map[i]

        if time.time() > DetailStatInfo1Min.period_end_timestamp:
            logger.debug("period 1 minute...")
            # insert to leveldb
            ldb_name_new = get_format_date()
            if ldb_name_new != __init__.ldb_name:
                __init__.ldb_name = ldb_name_new
                __init__.ldb = leveldb.LevelDB(__init__.ldb_name)

            logger.debug("batch insert %d records to leveldb..." % len(DetailStatInfo1Min.stat_info_map))
            batch = leveldb.WriteBatch()
            for k, v in DetailStatInfo1Min.stat_info_map.items():
                __init__.ldb.Put("-".join([k, str(DetailStatInfo1Min.period_start_timestamp)]), v.to_json())
            __init__.ldb.Write(batch, sync=True)

            t = time.time()
            DetailStatInfo1Min.period_start_timestamp = int(t) / 60 * 60
            DetailStatInfo1Min.period_end_timestamp = (int(t) / 60 + 1) * 60
            DetailStatInfo1Min.stat_info_map = {}

        if time.time() > DetailStatInfo30Min.period_end_timestamp:
            logger.debug("period 30 minute...")
            # insert to mysql
            logger.debug("batch insert %d records to mysql..." % len(DetailStatInfo30Min.stat_info_map))
            data_list = []
            for k, v in DetailStatInfo30Min.stat_info_map:
                l = k.split(".")
                d = {
                    "uname": l[0],
                    "worker": l[1],
                    "totaldiff": v.total_diff,
                    "validcount": v.valid_count,
                    "invalidcount": v.invalid_count,
                    "periodtime": get_format_datetime(DetailStatInfo30Min.period_start_timestamp)
                }
                data_list.append(d)
            TblStatInfoDetail30m.insert_many(data_list).execute()

            t = time.time()
            DetailStatInfo30Min.period_start_timestamp = int(t) / 1800 * 1800
            DetailStatInfo30Min.period_end_timestamp = (int(t) / 1800 + 1) * 1800
            DetailStatInfo30Min.stat_info_map = {}

        gevent.sleep(1)

