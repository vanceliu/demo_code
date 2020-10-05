# -*- coding: utf-8 -*-
import logging
import traceback
import yaml
from urllib import request, error

logger = logging.getLogger(__name__)


def load_config(server, yml_url):
    try:
        password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, server["uri"], server["username"], server["password"])

        handler = request.HTTPBasicAuthHandler(password_mgr)
        opener = request.build_opener(handler)
        request.install_opener(opener)

        config = request.urlopen(yml_url).read().decode("utf8")
        return yaml.safe_load(config)

    except error.URLError as e:
        if hasattr(e, "code"):
            logger.error("HTTP error: {}, url: {}".format(e.code, yml_url))
        elif hasattr(e, "reason"):
            logger.error("URL error: {}, url: {}".format(e.reason, yml_url))
        raise e
    except:
        logger.error(traceback.format_exc())
        raise
        # return None
