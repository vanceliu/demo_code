# -*- coding: utf-8 -*-
import argparse
import logging
from flask import Flask
from flask_cors import CORS
from config.application import app_context
from api.project_api import project_api
from api.release_api import release_api
from api.system_api import system_api, jwt_init

HOST = app_context.app_config["server"]["host"]
PORT = app_context.app_config["server"]["port"]
ENV = app_context.app_config["profiles"]

logger = logging.getLogger(__name__)

def main():
    app = Flask(__name__)
    CORS(app)
    jwt_init(app)

    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
    app.config["JSON_AS_ASCII"] = False
    app.config["app_context"] = app_context

    prefix = "{}/{}/{}".format(app_context.context_path, app_context.path_name, app_context.version)
    app.register_blueprint(project_api, url_prefix=prefix)
    app.register_blueprint(release_api, url_prefix=prefix)
    app.register_blueprint(system_api, url_prefix=prefix)

    return app


app = main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", dest="port", default=str(PORT), help="bind port")
    parser.add_argument("--ip", "-i", dest="host", default=str(HOST), help="bind host")
    parser.add_argument("--env", "-e", dest="env", default=str(ENV), help="active profiles")
    args = parser.parse_args()

    app.run(host=args.host, port=int(args.port), debug=False, threaded=True)
    # main(args.host, args.port, args.env)
