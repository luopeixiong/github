# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 14:10:50 2017

@author: luopx
"""

import redis


class _redis(object):
    def __init__(self, host='127.0.0.1', port='6379', db='0',):
        self.host = host
        self.port = port
        self.db = db
        self._setredis()
    def _setredis(self):
        self._DB = redis.Redis(host=self.host, port=self.port, db=self.db)
        
    def _get_db(self):
        return self._DB
    