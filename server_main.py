#!/usr/bin/env python
# encoding: utf-8

import gevent
from gevent import monkey, pywsgi
monkey.patch_all()
from gevent import socket
from shares import on_receive_data
from __init__ import Application
from shares import ReceivedConnection
from stat_info import stat_info_init
from stat_info import run_statistics_task

from abc import ABC

from flask import Flask
from peewee import MySQLDatabase
from playhouse.shortcuts import ReconnectMixin
from config import config
from loguru import logger
from utils import get_format_date
from model import database_proxy
from bp import bp
import logging
import leveldb


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase, ABC):
    pass


# create a custom handler
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


# application factory pattern
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # logging properties are defined in config.py
    logger.start(app.config['LOGFILE'], level=app.config['LOG_LEVEL'], format="{time} {level} {message}",
                 backtrace=app.config['LOG_BACKTRACE'], rotation='25 MB')

    # register loguru as handler
    app.logger.addHandler(InterceptHandler())

    Application.db = ReconnectMySQLDatabase(config[config_name].DB_NAME, autocommit=True, autorollback=True,
                                            **{'host': config[config_name].DB_HOST, 'port': config[config_name].DB_PORT,
                                               'user': config[config_name].DB_USER,
                                               'password': config[config_name].DB_PASSWORD,
                                               'use_unicode': config[config_name].DB_USE_UNICODE,
                                               'charset': config[config_name].DB_CHARSET})
    database_proxy.initialize(Application.db)

    Application.ldb_path = app.config['LDB_PATH']
    Application.ldb_name = get_format_date()
    ldb_path_name = '/'.join([Application.ldb_path, Application.ldb_name])
    Application.ldb = leveldb.LevelDB(ldb_path_name)

    Application.app = app
    Application.app.register_blueprint(bp)


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

        ReceivedConnection.received_count_per_min += 1
        r = on_receive_data(c)
        if not r:
            c.connection.close()
            break


if __name__ == '__main__':
    create_app('default')
    stat_info_init()
    logger.info("Run SharesReceiverServer on [%s:%d]"
                % (Application.app.config['SHARES_SERVER_IP'],
                   Application.app.config['SHARES_SERVER_PORT']))
    run_shares_receiver(Application.app.config['SHARES_SERVER_IP'], Application.app.config['SHARES_SERVER_PORT'])
    logger.info("Run statistics task")
    run_statistics_task()
    logger.info("Run WSGIServer on [%s:%d]"
                % (Application.app.config['WSGI_SERVER_IP'],
                   Application.app.config['WSGI_SERVER_PORT']))
    server = pywsgi.WSGIServer((Application.app.config['WSGI_SERVER_IP'], Application.app.config['WSGI_SERVER_PORT']),
                               Application.app)
    server.serve_forever()

