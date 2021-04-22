# -*-coding:utf-8-*-

import logging


class Log(object):
    """日志"""
    def __init__(self):
        logger = logging.getLogger(__name__)

        fh = logging.FileHandler('log.log', mode='w', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s [line %(lineno)d]')
        logger.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        self.logger = logger

    def info(self, string):
        self.logger.info(string)

    def error(self, string):
        self.logger.error(string)
