# -*- coding: utf-8 -*-
from enum import Enum

DEFAULT_DATE_PATTERN = "%Y-%m-%d"
DEFAULT_DATETIME_PATTERN = "%Y-%m-%d %H:%M:%S"

# default global elasticsearch  constants
ES_SCROLL_SIZE = 20
ES_SCROLL_ALIVE = "1m"

# default global mongo constants
DEFAULT_KNOWHOW = "general"
DEFAULT_REPONSE_INTENT = "utter_general"
DEFAULT_REPONSE_TYPE = "system"


class Type(Enum):
    project = "project"
    product = "product"


class LanguageType(Enum):
    zh_CN = "zh_CN"
    zh_TW = "zh_TW"
    en_US = "en_US"
