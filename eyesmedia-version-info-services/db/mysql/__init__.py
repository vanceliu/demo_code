# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


class DefaultDBConfig(object):

    def __init__(self, host, username, password, port=None, dbname=None):
        self.__host = host
        self.__port = port
        self.__dbname = dbname
        self.__username = username
        self.__password = password

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def dbname(self):
        return self.__dbname

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password