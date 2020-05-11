#!/usr/bin/env python
# encoding: utf-8


from flask import Blueprint
import time
import json
from utils import get_format_datetime
from model import TblStatInfoTotal30m, TblStatInfoDetail30m
from difficulty import UfoDiff
from stat_info import TotalStatInfo30Min, DetailStatInfo30Min
from peewee import fn


bp = Blueprint('', __name__, url_prefix='/v2/')


@bp.route('/poolinfo30m', methods=('GET', 'POST'))
def poolinfo30m():
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
        t2 = max(max(keys), int(time.time()))
        t = t2 - t1
        if t <= 0 or t > 1800:
            t = 1800
    else:
        t = 1800
    hashrate = UfoDiff.get_hash_rate_by_diff(totaldiff, t, None)

    return json.dumps({
        "sharesdiff": "%.06f" % totaldiff,
        "hashrate": "%.06f MHash/s" % (hashrate / 1000 / 1000),
        "validcount": validcount,
        "invalidcount": invalidcount
    })


@bp.route('/poolstat24h', methods=('GET', 'POST'))
def poolstat24h():
    t = int(time.time()) - 86400
    s = get_format_datetime(t)
    infos = TblStatInfoTotal30m.select().where(TblStatInfoTotal30m.periodtime > s)\
        .order_by(TblStatInfoTotal30m.periodtime).execute()

    stat_24h_list = []

    for info in infos:
        sharesdiff = float(info.totaldiff)
        hashrate = float(info.hashrate) / 1000 / 1000
        validcount = int(info.validcount)
        invalidcount = int(info.invalidcount)
        periodtime = str(info.periodtime)
        stat_24h_list.append(
            {
                "sharesdiff": "%.06f" % sharesdiff,
                "hashrate": "%.06f" % hashrate,
                "validcount": validcount,
                "invalidcount": invalidcount,
                "periodtime": periodtime
            }
        )
    return json.dumps(stat_24h_list)


@bp.route('/minerinfo30m/<query_name>', methods=('GET', 'POST'))
def minerinfo30m(query_name):
    totaldiff = 0.0
    hashrate = 0.0
    validcount = 0
    invalidcount = 0

    t = int(time.time()) - 1800
    s = get_format_datetime(t)

    for i in range(3):
        if i == 0:
            if '.' not in query_name:
                continue
            l = query_name.split('.', 1)

            for k, v in DetailStatInfo30Min.stat_info_map.items():
                l2 = k.split('.', 1)
                if l[0] == l2[0] or l[1] == l2[1]:
                    totaldiff += v.total_diff
                    validcount += v.valid_count
                    invalidcount += v.invalid_count

            # query time is less than period_start_timestamp + 10min
            time_inteval = int(time.time() - DetailStatInfo30Min.period_start_timestamp)
            if time_inteval < 600:
                infos = TblStatInfoDetail30m.select(fn.SUM(TblStatInfoDetail30m.totaldiff).alias('totaldiffsum'),
                                                fn.SUM(TblStatInfoDetail30m.validcount).alias('validcountsum'),
                                                fn.SUM(TblStatInfoDetail30m.invalidcount).alias('invalidcountsum'),
                                                TblStatInfoDetail30m.periodtime) \
                    .where(TblStatInfoDetail30m.periodtime > s, TblStatInfoDetail30m.uname == l[0],
                           TblStatInfoDetail30m.worker == l[1]) \
                    .group_by(TblStatInfoDetail30m.periodtime).order_by(TblStatInfoDetail30m.periodtime).execute()

                if len(infos) > 0:
                    totaldiff += float(infos[0].totaldiffsum)
                    validcount += int(infos[0].validcountsum)
                    invalidcount += int(infos[0].invalidcountsum)
                    time_inteval += 1800

            hashrate = float(UfoDiff.get_hash_rate_by_diff(totaldiff, time_inteval, None))
            break
        elif i == 1:
            for k, v in DetailStatInfo30Min.stat_info_map.items():
                l2 = k.split('.', 1)

                if l2[0] == query_name:
                    totaldiff += v.total_diff
                    validcount += v.valid_count
                    invalidcount += v.invalid_count

            # query time is less than period_start_timestamp + 10min
            time_inteval = int(time.time() - DetailStatInfo30Min.period_start_timestamp)
            if time_inteval < 600:
                infos = TblStatInfoDetail30m.select(fn.SUM(TblStatInfoDetail30m.totaldiff).alias('totaldiffsum'),
                                                    fn.SUM(TblStatInfoDetail30m.validcount).alias('validcountsum'),
                                                    fn.SUM(TblStatInfoDetail30m.invalidcount).alias('invalidcountsum'),
                                                    TblStatInfoDetail30m.periodtime) \
                    .where(TblStatInfoDetail30m.periodtime > s, TblStatInfoDetail30m.uname == query_name) \
                    .group_by(TblStatInfoDetail30m.periodtime).order_by(TblStatInfoDetail30m.periodtime).execute()

                if len(infos) > 0:
                    totaldiff += float(infos[0].totaldiffsum)
                    validcount += int(infos[0].validcountsum)
                    invalidcount += int(infos[0].invalidcountsum)
                    time_inteval += 1800

            hashrate = float(UfoDiff.get_hash_rate_by_diff(totaldiff, time_inteval, None))

            # maybe found!
            if totaldiff != 0.0:
                break

        elif i == 2:
            for k, v in DetailStatInfo30Min.stat_info_map.items():
                l2 = k.split('.', 1)

                if l2[1] == query_name:
                    totaldiff += v.total_diff
                    validcount += v.valid_count
                    invalidcount += v.invalid_count

            # query time is less than period_start_timestamp + 10min
            time_inteval = int(time.time() - DetailStatInfo30Min.period_start_timestamp)
            if time_inteval < 600:
                infos = TblStatInfoDetail30m.select(fn.SUM(TblStatInfoDetail30m.totaldiff).alias('totaldiffsum'),
                                                    fn.SUM(TblStatInfoDetail30m.validcount).alias('validcountsum'),
                                                    fn.SUM(TblStatInfoDetail30m.invalidcount).alias('invalidcountsum'),
                                                    TblStatInfoDetail30m.periodtime) \
                    .where(TblStatInfoDetail30m.periodtime > s, TblStatInfoDetail30m.worker == query_name) \
                    .group_by(TblStatInfoDetail30m.periodtime).order_by(TblStatInfoDetail30m.periodtime).execute()

                if len(infos) > 0:
                    totaldiff += float(infos[0].totaldiffsum)
                    validcount += int(infos[0].validcountsum)
                    invalidcount += int(infos[0].invalidcountsum)
                    time_inteval += 1800

            hashrate = float(UfoDiff.get_hash_rate_by_diff(totaldiff, time_inteval, None))
            break

    return json.dumps({
        "sharesdiff": "%.06f" % totaldiff,
        "hashrate": "%.06f MHash/s" % (hashrate / 1000 / 1000),
        "validcount": validcount,
        "invalidcount": invalidcount
    })


@bp.route('/minerstat24h/<query_name>', methods=('GET', 'POST'))
def minerstat24h(query_name):
    t = int(time.time()) - 86400
    s = get_format_datetime(t)

    infos = []
    for i in range(3):
        if i == 0:
            if '.' not in query_name:
                continue
            l = query_name.split('.', 1)
            infos = TblStatInfoDetail30m.select(fn.SUM(TblStatInfoDetail30m.totaldiff).alias('totaldiffsum'),
                                                fn.SUM(TblStatInfoDetail30m.validcount).alias('validcountsum'),
                                                fn.SUM(TblStatInfoDetail30m.invalidcount).alias('invalidcountsum'),
                                                TblStatInfoDetail30m.periodtime)\
                .where(TblStatInfoDetail30m.periodtime > s, TblStatInfoDetail30m.uname == l[0], TblStatInfoDetail30m.worker == l[1])\
                .group_by(TblStatInfoDetail30m.periodtime).order_by(TblStatInfoDetail30m.periodtime).execute()
            if len(infos) > 0:
                break
        elif i == 1:
            infos = TblStatInfoDetail30m.select(fn.SUM(TblStatInfoDetail30m.totaldiff).alias('totaldiffsum'),
                                                fn.SUM(TblStatInfoDetail30m.validcount).alias('validcountsum'),
                                                fn.SUM(TblStatInfoDetail30m.invalidcount).alias('invalidcountsum'),
                                                       TblStatInfoDetail30m.periodtime) \
                .where(TblStatInfoDetail30m.periodtime > s, TblStatInfoDetail30m.uname == query_name)\
                .group_by(TblStatInfoDetail30m.periodtime).order_by(TblStatInfoDetail30m.periodtime).execute()
            if len(infos) > 0:
                break
        else:
            infos = TblStatInfoDetail30m.select(fn.SUM(TblStatInfoDetail30m.totaldiff).alias('totaldiffsum'),
                                                fn.SUM(TblStatInfoDetail30m.validcount).alias('validcountsum'),
                                                fn.SUM(TblStatInfoDetail30m.invalidcount).alias('invalidcountsum'),
                                                       TblStatInfoDetail30m.periodtime) \
                .where(TblStatInfoDetail30m.periodtime > s, TblStatInfoDetail30m.worker == query_name) \
                .group_by(TblStatInfoDetail30m.periodtime).order_by(TblStatInfoDetail30m.periodtime).execute()
            if len(infos) > 0:
                break

    stat_24h_list = []
    for info in infos:
        sharesdiff = float(info.totaldiffsum)
        hashrate = float(UfoDiff.get_hash_rate_by_diff(sharesdiff, 1800, None)) / 1000 / 1000
        validcount = int(info.validcountsum)
        invalidcount = int(info.invalidcountsum)
        periodtime = str(info.periodtime)
        stat_24h_list.append(
            {
                "sharesdiff": "%.06f" % sharesdiff,
                "hashrate": "%.06f" % hashrate,
                "validcount": validcount,
                "invalidcount": invalidcount,
                "periodtime": periodtime
            }
        )
    return json.dumps(stat_24h_list)



