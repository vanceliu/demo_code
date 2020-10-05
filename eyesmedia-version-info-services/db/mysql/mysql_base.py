# connect with peewee style
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import logging
import abc
from peewee import MySQLDatabase
from eyesmediapydb import DefaultDBConfig

logger = logging.getLogger("eyesmediapydb")


class MySqlConfig(DefaultDBConfig):
    __charset = "utf8mb4"

    @property
    def charset(self):
        return self.__charset

    @charset.setter
    def charset(self, value):
        self.__charset = value

class MySqlConnectionProvider(object):
    def __init__(self, config):
        if not isinstance(config, MySqlConfig):
            raise Exception("input attribute(config) type must be mysql_base.MySqlConfig")
        self.mysql_config = config

    def create_client(self,  **kwargs):
        client =  MySQLDatabase(self.mysql_config.dbname,
                                host=self.mysql_config.host,
                                user=self.mysql_config.username,
                                port=self.mysql_config.port,
                                passwd=self.mysql_config.password,
                                **kwargs
                            )
        logger.debug("create mysql client:{}".format(client))
        return client

class MySqlRepository(abc.ABC):
    def __init__(self, db):
        self.table = self._get_table()
        self.table._meta.database = db

    @abc.abstractmethod
    def _get_table(self):
        pass



