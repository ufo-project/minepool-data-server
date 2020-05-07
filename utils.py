#!/usr/bin/env python
# encoding: utf-8


import time


def get_format_date(t=None):
    if t is None:
        t = int(time.time())
    lt = time.localtime(time.time())
    return time.strftime("%Y-%m-%d", lt)


if __name__ == "__main__":
    print(get_format_date())