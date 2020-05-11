#!/usr/bin/env python
# encoding: utf-8


import time
import json
import gevent
import leveldb
from __init__ import Application
from loguru import logger
from utils import get_format_date, get_format_datetime
from model import TblStatInfoDetail30m, TblStatInfoTotal30m
from difficulty import UfoDiff


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


# total stat info (during the latest 30 minutes)
class TotalStatInfo30Min(object):
    period_start_timestamp = 0
    period_end_timestamp = 0
    total_info_map = {}

    @staticmethod
    def add_share_info(share_info):
        t = int(time.time())
        stat_info = TotalStatInfo30Min.total_info_map.get(t)
        if stat_info is None:
            stat_info = StatInfo(share_info.share_diff if share_info.valid == "1" else 0.0,
                                 1 if share_info.valid == "1" else 0,
                                 0 if share_info.valid == "1" else 1)
        else:
            stat_info.total_diff += share_info.share_diff if share_info.valid == "1" else 0.0
            stat_info.valid_count += 1 if share_info.valid == "1" else 0
            stat_info.invalid_count += 0 if share_info.valid == "1" else 1
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
            stat_info = StatInfo(share_info.share_diff if share_info.valid == "1" else 0.0,
                                 1 if share_info.valid == "1" else 0,
                                 0 if share_info.valid == "1" else 1)
        else:
            stat_info.total_diff += share_info.share_diff if share_info.valid == "1" else 0.0
            stat_info.valid_count += 1 if share_info.valid == "1" else 0
            stat_info.invalid_count += 0 if share_info.valid == "1" else 1
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
            stat_info = StatInfo(share_info.share_diff if share_info.valid == "1" else 0.0,
                                 1 if share_info.valid == "1" else 0,
                                 0 if share_info.valid == "1" else 1)
        else:
            stat_info.total_diff += share_info.share_diff if share_info.valid == "1" else 0.0
            stat_info.valid_count += 1 if share_info.valid == "1" else 0
            stat_info.invalid_count += 0 if share_info.valid == "1" else 1
        DetailStatInfo1Min.stat_info_map[k] = stat_info


def stat_info_init():
    t = time.time()

    # TotalStatInfo30Min
    TotalStatInfo30Min.period_start_timestamp = int(t)
    TotalStatInfo30Min.period_end_timestamp = (int(t) // 1800 + 1) * 1800
    TotalStatInfo30Min.total_info_map = {}

    # DetailStatInfo1Min
    DetailStatInfo1Min.period_start_timestamp = int(t)
    DetailStatInfo1Min.period_end_timestamp = (int(t) // 60 + 1) * 60
    DetailStatInfo1Min.stat_info_map = {}

    # DetailStatInfo30Min
    DetailStatInfo30Min.period_start_timestamp = int(t)
    DetailStatInfo30Min.period_end_timestamp = (int(t) // 1800 + 1) * 1800
    DetailStatInfo30Min.stat_info_map = {}


def run_statistics_task():
    gevent.spawn(statistics_task)


def statistics_task():
    while True:
        need_to_remove = [t for t in TotalStatInfo30Min.total_info_map.keys() if t < time.time() - 1800]
        for i in need_to_remove:
            del TotalStatInfo30Min.total_info_map[i]

        if time.time() > TotalStatInfo30Min.period_end_timestamp:
            logger.debug("period 30 minute [TotalStatInfo30Min]...")
            totaldiff = 0.0
            validcount = 0
            invalidcount = 0
            for v in TotalStatInfo30Min.total_info_map.values():
                totaldiff += v.total_diff
                validcount += v.valid_count
                invalidcount += v.invalid_count

            keys = list(TotalStatInfo30Min.total_info_map.keys())
            # time inteval
            if len(keys) > 0:
                t1 = min(keys)
                t2 = max(keys)
                t = t2 - t1
                if t <= 0:
                    t = 1800
            else:
                t = 1800
            hashrate = UfoDiff.get_hash_rate_by_diff(totaldiff, t, None)

            logger.debug("insert 30 minutes total info, totaldiff: [%.08f], hashrate: [%.08f]..."
                         % (totaldiff, hashrate))
            TblStatInfoTotal30m.create(totaldiff=totaldiff, hashrate="%.08f" % hashrate, validcount=validcount,
                                       invalidcount=invalidcount,
                                       periodtime=get_format_datetime(TotalStatInfo30Min.period_end_timestamp))

            t = time.time()
            TotalStatInfo30Min.period_start_timestamp = int(t) // 1800 * 1800
            TotalStatInfo30Min.period_end_timestamp = (int(t) // 1800 + 1) * 1800

        if time.time() > DetailStatInfo1Min.period_end_timestamp:
            logger.debug("period 1 minute [DetailStatInfo1Min]...")
            # insert to leveldb
            ldb_name_new = get_format_date()
            if ldb_name_new != Application.ldb_name:
                Application.ldb_name = ldb_name_new
                ldb_path_name = '/'.join([Application.ldb_path, Application.ldb_name])
                Application.ldb = leveldb.LevelDB(ldb_path_name)

            logger.debug("batch insert %d records to leveldb..." % len(DetailStatInfo1Min.stat_info_map))
            if len(DetailStatInfo1Min.stat_info_map) > 0:
                batch = leveldb.WriteBatch()
                for k, v in DetailStatInfo1Min.stat_info_map.items():
                    Application.ldb.Put("-".join([k, str(DetailStatInfo1Min.period_end_timestamp)]).encode(),
                                        v.to_json().encode())
                Application.ldb.Write(batch, sync=True)

            t = time.time()
            DetailStatInfo1Min.period_start_timestamp = int(t) // 60 * 60
            DetailStatInfo1Min.period_end_timestamp = (int(t) // 60 + 1) * 60
            DetailStatInfo1Min.stat_info_map = {}

        if time.time() > DetailStatInfo30Min.period_end_timestamp:
            logger.debug("period 30 minute [DetailStatInfo30Min]...")
            # insert to mysql
            logger.debug("batch insert %d records to mysql..." % len(DetailStatInfo30Min.stat_info_map))
            data_list = []
            for k, v in DetailStatInfo30Min.stat_info_map.items():
                l = k.split(".")
                d = {
                    "uname": l[0],
                    "worker": l[1],
                    "totaldiff": v.total_diff,
                    "validcount": v.valid_count,
                    "invalidcount": v.invalid_count,
                    "periodtime": get_format_datetime(DetailStatInfo30Min.period_end_timestamp)
                }
                data_list.append(d)
            if len(data_list) > 0:
                TblStatInfoDetail30m.insert_many(data_list).execute()

            t = time.time()
            DetailStatInfo30Min.period_start_timestamp = int(t) // 1800 * 1800
            DetailStatInfo30Min.period_end_timestamp = (int(t) // 1800 + 1) * 1800
            DetailStatInfo30Min.stat_info_map = {}

        gevent.sleep(1)

