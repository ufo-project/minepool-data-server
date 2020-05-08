#!/usr/bin/env python
# encoding: utf-8


from flask import Blueprint
import time
import json
from utils import get_format_datetime
from model import TblStatInfoTotal30m


bp = Blueprint('', __name__, url_prefix='/')


@bp.route('/poolinfo30m', methods=('GET', 'POST'))
def poolinfo30m():
    t = int(time.time()) - 1800
    s = get_format_datetime(t)
    infos = TblStatInfoTotal30m.select().where(TblStatInfoTotal30m.periodtime > s).execute()

    sharesdiff = 0.0
    hashrate = 0.0
    validcount = 0
    invalidcount = 0

    if len(infos) >= 1:
        sharesdiff = float(infos[0].totaldiff)
        hashrate = float(infos[0].hashrate) / 1000 / 1000
        validcount = infos[0].validcount
        invalidcount = infos[0].invalidcount

    return json.dumps({
        "sharesdiff": sharesdiff,
        "hashrate": "%.06f MHash/s" % hashrate,
        "validcount": validcount,
        "invalidcount": invalidcount
    })
