# -*- coding: utf-8 -*-
import logging

from eyesmediapydb.mongo_base import MongoRepository
from config import constants
from config.constants import LanguageType

logger = logging.getLogger(__name__)

'''
新增的models class 需db/mongo目錄底下的__init__.py import 新的models class
'''

class NluCategory(MongoRepository):
    # id = None
    parent_id = None
    name = None
    code = None

