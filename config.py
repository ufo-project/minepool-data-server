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

    LDB_PATH = "../ldb_path"

    SHARES_SERVER_IP = "0.0.0.0"
    SHARES_SERVER_PORT = 9999

    WSGI_SERVER_IP = "0.0.0.0"
    WSGI_SERVER_PORT = 8085

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    LOG_BACKTRACE = False
    LOG_LEVEL = 'INFO'

    DB_HOST = '127.0.0.1'
    DB_PORT = 3306
    DB_NAME = 'ufodb'
    DB_USER = ''
    DB_PASSWORD = ''
    DB_USE_UNICODE = True
    DB_CHARSET = 'utf8'

    LDB_PATH = "../ldb_path"

    SHARES_SERVER_IP = "127.0.0.1"
    SHARES_SERVER_PORT = 9999

    WSGI_SERVER_IP = "127.0.0.1"
    WSGI_SERVER_PORT = 8085

    @staticmethod
    def init_app(app):
        pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
