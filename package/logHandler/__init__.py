#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Logger Handler
"""

from .logHandler import LogHandler

"""
usage:
* 文件夹拷贝到工程根目录文件下

from package.logHandler import LogHandler
import logging

log = LogHandler(log_name, level = logging.DEBUG)

默认Log level 为 DEBUG

log.info('this is a test msg')
log.debug("this is a debug log")

log文件输出为工程根目录下的log文件

# 日志级别
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
"""
