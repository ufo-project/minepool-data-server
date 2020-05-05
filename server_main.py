#!/usr/bin/env python
# encoding: utf-8


from gevent import monkey
from gevent import pywsgi
from __init__ import create_app
from config import config
monkey.patch_all()


if __name__ == '__main__':
    app = create_app('default')
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    server.serve_forever()

