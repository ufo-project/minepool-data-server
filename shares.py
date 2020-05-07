#!/usr/bin/env python
# encoding: utf-8


import json
import time

from stat_info import ShareInfo
from stat_info import DetailStatInfo1Min
from stat_info import DetailStatInfo30Min
from stat_info import TotalStatInfo30Min


class ReceivedConnection(object):
    def __init__(self):
        self.connection = None
        self.data_cache = b""


def on_receive_data(c):
    while True:
        if b'\n' in c.data_cache:
            l = c.data_cache.split(b'\n', 1)
            c.data_cache = l[1]
            o = None
            try:
                o = json.loads(l[0].decode())
            except:
                return False
            on_new_share(o)
        else:
            return True


def on_new_share(share_obj):
    user_name = share_obj["uname"]
    worker = share_obj["worker"]
    share_diff = float(share_obj["sdiff"])
    valid = share_obj["valid"]

    TotalStatInfo30Min.add_share_info(ShareInfo(user_name, worker, share_diff, valid))
    DetailStatInfo1Min.add_share_info(ShareInfo(user_name, worker, share_diff, valid))
    DetailStatInfo30Min.add_share_info(ShareInfo(user_name, worker, share_diff, valid))
