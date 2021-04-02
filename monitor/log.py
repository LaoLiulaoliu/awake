#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import RotatingFileHandler
from const import LOG_DIR

def logging_file(path, name, maxBytes=1024 * 1024 * 5, backupCount=10, level='INFO'):
    if not os.path.exists(path):
        os.makedirs(path)

    basic_format = '[%(asctime)s %(threadName)s %(levelname)-5s] [%(filename)s:%(funcName)s:%(lineno)-1d] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(basic_format, date_format)

    logger = logging.getLogger()
    logger.setLevel(level)

    fhlr = RotatingFileHandler(filename=os.path.join(path, name), maxBytes=maxBytes, backupCount=backupCount)
    fhlr.suffix = "%Y-%m-%d.log"
    # fhlr.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    fhlr.setFormatter(formatter)

    # shlr = logging.StreamHandler()
    # shlr.setFormatter(formatter)
    # logger.addHandler(shlr)
    logger.addHandler(fhlr)

logging_file(os.path.join(os.environ['HOME'], LOG_DIR), 'awake.log')
