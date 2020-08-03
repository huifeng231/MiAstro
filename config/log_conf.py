#!/usr/bin/env python
# encoding: utf-8
'''
@author: Mark li
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: deamoncao100@gmail.com
@software: Pycharm
@file: log_conf.py
@time: 2019-09-28 16:41
@desc:
'''


_LEVEL = 'DEBUG'


def _file_handler(log_fname, formatter='simple'):
    return {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'formatter': formatter,
        'filename': 'log/%s.log' % log_fname,
        'maxBytes': 1024 * 1024 * 50,
        'backupCount': 5,
        'encoding': 'utf-8'
    }


def _log_dict(handler, level="DEBUG"):
    return {'handlers': [handler], 'level': level, 'propagate': False}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] %(message)s',
        },
        'print': {
            'format': '%(asctime)s %(message)s',
        }
    },
    'handlers': {
        'null': {'level': 'DEBUG', 'class': 'logging.NullHandler'},
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'simple'}
    },
    'loggers': {
        # 'root': _log_dict('null', level=_LEVEL),
    }
}


def _add(*names, formatter='simple'):
    for name in names:
        LOGGING.get("handlers")[name] = _file_handler(name, formatter=formatter)
        LOGGING.get("loggers")[name] = _log_dict(name, level=_LEVEL)

def get_logger(name="root"):
    import logging.config
    # from video.settings import log_conf
    logging.config.dictConfig(LOGGING)
    return logging.getLogger(name=name)
