# -*- coding: utf-8 -*-
import yaml
import os
import logging
import logging.config
import traceback
import configparser
import time
from elasticsearch import Elasticsearch
from config.constants import LanguageType
from config.cloud_config import load_config
from eyesmediapydb.mongo_base import MongoConfig, MongoClientProvider
from db.mysql.mysql_base import MySqlConnectionProvider, MySqlConfig

# ROOT_PATH = os.path.dirname(sys.modules["__main__"].__file__)  # project root path
ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
LOG_PATH = os.path.join(ROOT_PATH, "logs/")
BOOTSTRAP_CONFIG_FILE = os.path.join(ROOT_PATH, "bootstrap.yml")
LOGGING_CONFIG_FILE = os.path.join(ROOT_PATH, "logging.yml")
DEFAULT_ACTIVE = "local"

logger = logging.getLogger(__name__)


def _init_logging():
    global LOG_PATH, LOGGING_CONFIG_FILE
    default_level = logging.NOTSET
    default_format = "%(asctime)s [%(threadName)s-%(process)d] %(levelname)-5s %(module)s - %(message)s"
    use_default = False

    if os.path.exists(LOGGING_CONFIG_FILE):
        if not os.path.isdir(LOG_PATH):
            os.mkdir(LOG_PATH)

        try:
            with open(LOGGING_CONFIG_FILE) as file:
                log_setting = yaml.safe_load(file)

            logging.config.dictConfig(log_setting)
            logger.info("init logging end, from {}".format(LOGGING_CONFIG_FILE))
        except:
            logger.warning("read {} failure, init default logging...".format(LOGGING_CONFIG_FILE))
            # default_level = log_setting["root"]["level"]
            # default_format = log_setting["formatters"]["simple"]["format"]
            use_default = True

    if use_default:
        logging.basicConfig(
            level=default_level,
            format=default_format
        )


_init_logging()


class ApplicationContext(object):
    app_config = None  # running active config
    messages = {}
    mongo_client = None
    mongo_client_rpt = None
    es_client = None
    mysql_config = None
    version = None  # url_prefix version (/corpus/api/{version})
    active = None  # running active
    # profiles = dict()  # store all of active profiles
    # active_list = None  # list, store multiple actives' tag
    # cloud_config = None  # clould config server information
    ner_model = None
    timezone = "Asia/Taipei"
    nlu_config = None
    language = LanguageType.zh_TW.value
    tokenizer = None

    def __init__(self):
        sstime = time.time()
        self.__load_active_profiles()
        # self.app_config = self.profiles.get(self.active)
        if not self.app_config:
            raise EnvironmentError("Can not load profile: {}".format(self.active))

        self.__load_msg_property()

        self.context_path = self.app_config["server"]["contextPath"]

        root_config = self.app_config["eyesmedia"]
        self.version = root_config["api"]["version"]
        self.path_name = root_config["api"]["path-name"]

        # setting system default language
        locale = root_config.get("locale")
        if locale and LanguageType(locale):
            self.language = locale
        self.app_config.setdefault("language", locale)

        local_timezone = root_config.get("localTimeZone")
        if local_timezone:
            self.timezone = local_timezone

        db_config = root_config.get("database")
        if db_config:
            self.mongo_client_rpt = self.init_mongo_client(db_config.get("mongodb-rpt"))
            self.mongo_client_syslogger = self.init_mongo_client(db_config.get("mongodb-syslogger"))
            self.mysql_client = self.init_mysql_client(db_config.get("mysql"))


        cost_time = time.time() - sstime
        logger.info("application({}) is initialized, cost time is {}/s, {}".format(self.active, cost_time, self.app_config))

    def __load_active_profiles(self):
        with open(BOOTSTRAP_CONFIG_FILE) as stream:
            data = yaml.safe_load(stream)
        self.active = data["default"]["active"]
        application_name = data["application"]["name"]
        active_list = data["profile"]["actives"]  # load multiple actives
        active_list = str(active_list).replace(' ', '').split(',')  # split multiple actives into list
        cloud_config = data["cloud"]["config"]

        # load cloud config
        if self.active in active_list:
            yml_url = cloud_config["uri"] + "/" + self.active + "/" + application_name + "-" + self.active + ".yml"
            try:
                self.app_config = load_config(cloud_config, yml_url)
                logger.info("cloud config file({}) loading success!".format(yml_url))
            except:
                logger.warning("cloud config file({}) loading failed...".format(yml_url))

        if not self.app_config:
            # load from local config file
            config_file = "application-" + self.active + ".yml"
            config_file = os.path.join(ROOT_PATH, config_file)
            with open(config_file) as stream:
                self.app_config = yaml.safe_load(stream)
            logger.info("config file({}) loading success!".format(config_file))

    def __load_msg_property(self):
        msg_prop_file = os.path.join(ROOT_PATH, "messages.properties")
        if os.path.exists(msg_prop_file):
            try:
                msg_prop = configparser.ConfigParser()
                msg_prop.read(msg_prop_file)
                for section in msg_prop.sections():
                    for key in msg_prop[section]:
                        self.messages.setdefault(key, msg_prop[section][key])
                logger.info("messages.properties({}) loading success!".format(len(self.messages)))
            except:
                logger.error(traceback.format_exc())
                logger.error("messages properties loading failed...")

    def init_mongo_client(self, config):
        if not config:
            return None
        try:
            # mongo_config = self.app_config["eyesmedia"]["data"]["mongodb"]
            mongo_config = MongoConfig(host=config["host"],
                                       port=config.get("port"),
                                       dbname=config["dbname"],
                                       username=config["username"],
                                       password=str(config["pwd"]),
                                       replicaset=config.get("replica-set")
                                       )
            mongo_config.timezone = self.timezone
            mongo_config.auth_source = config.get("authentication-database")
            mongo_config.auth_mode = config.get("authentication-mode")

            provider = MongoClientProvider(mongo_config)
            logger.info("init MongoClient success, {}".format(config))
            return provider.create_client(socketTimeoutMS=5000,
                                          maxIdleTimeMS=2000,
                                          connectTimeoutMS=5000,
                                          maxPoolSize=2)
        except:
            logger.error("init MongoDB Client has error, config is {}".format(config))
            raise

    def init_mysql_client(self, config):
        if not config:
            return None
        try:
            mysql_config =  MySqlConfig(dbname=config["db"],
                                        host=config["host"],
                                        username=config["username"],
                                        port=config["port"],
                                        password=str(config["password"])
                                        )
            provider = MySqlConnectionProvider(mysql_config)
            logger.info("init mysql client success, {}".format(config))
            return provider.create_client()
        except:
            logger.error("init mysql client has error, config is {}".format(config))
            raise



app_context = ApplicationContext()