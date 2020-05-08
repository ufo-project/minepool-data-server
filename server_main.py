#!/usr/bin/env python
# encoding: utf-8

import gevent
from gevent import monkey, pywsgi
monkey.patch_all()
from gevent import socket
from shares import on_receive_data
from __init__ import create_app, Application
from shares import ReceivedConnection
from stat_info import stat_info_init
from stat_info import run_statistics_task
from loguru import logger


def run_shares_receiver(ip, port):
    gevent.spawn(shares_receive_server, ip, port)


def shares_receive_server(ip, port):
    s = socket.socket()
    s.bind((ip, port))
    s.listen(5)
    while True:
        c, addr = s.accept()
        logger.info("address %s:%d connect..." % (addr[0], addr[1]))
        gevent.spawn(handle_connection, c)


def handle_connection(conn):
    c = ReceivedConnection()
    c.connection = conn
    while True:
        try:
            d = c.connection.recv(1024)
        except:
            logger.exception("")
            c.connection.close()
            break

        if not d:
            c.connection.close()
            break
        c.data_cache += d
        r = on_receive_data(c)
        if not r:
            c.connection.close()
            break


if __name__ == '__main__':
    create_app('default')
    stat_info_init()
    logger.info("Run SharesReceiverServer on 0.0.0.0:9999")
    run_shares_receiver('0.0.0.0', 9999)
    logger.info("Run statistics task")
    run_statistics_task()
    logger.info("Run WSGIServer on 0.0.0.0:8000")
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), Application.app)
    server.serve_forever()

