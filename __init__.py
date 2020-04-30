#!/usr/bin/env python
# encoding: utf-8
from abc import ABC

from flask import Flask
from peewee import MySQLDatabase
from playhouse.shortcuts import ReconnectMixin
from config import config
from loguru import logger
import logging


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase, ABC):
    pass


db = None


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

    global db
    db = ReconnectMySQLDatabase(config[config_name].DB_NAME, autocommit=True, autorollback=True,
                                **{'host': config[config_name].DB_HOST, 'port': config[config_name].DB_PORT,
                                   'user': config[config_name].DB_USER, 'password': config[config_name].DB_PASSWORD,
                                   'use_unicode': config[config_name].DB_USE_UNICODE,
                                   'charset': config[config_name].DB_CHARSET})

    return app
