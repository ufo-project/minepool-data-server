#!/usr/bin/env python
# encoding: utf-8


import time


def get_format_date(t=None):
    if t is None:
        t = int(time.time())
    lt = time.localtime(t)
    return time.strftime("%Y-%m-%d", lt)


def get_format_datetime(t=None):
    if t is None:
        t = int(time.time())
    lt = time.localtime(t)
    return time.strftime("%Y-%m-%d %H:%M:%S", lt)


if __name__ == "__main__":
    print(get_format_date())
    print(get_format_datetime())

