#!/usr/bin/env python
# encoding: utf-8

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SUPER-SECRET'
    LOGFILE = "server.log"


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_BACKTRACE = True
    LOG_LEVEL = 'DEBUG'

    DB_HOST = '192.168.1.122'
    DB_PORT = 3306
    DB_NAME = 'test'
    DB_USER = 'root'
    DB_PASSWORD = '123456'
    DB_USE_UNICODE = True
    DB_CHARSET = 'utf8'

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    LOG_BACKTRACE = False
    LOG_LEVEL = 'INFO'

    DB_HOST = ''
    DB_PORT = 3306
    DB_NAME = ''
    DB_USER = ''
    DB_PASSWORD = ''
    DB_USE_UNICODE = ''
    DB_CHARSET = ''

    @staticmethod
    def init_app(app):
        pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
