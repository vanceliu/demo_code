# -*- coding: utf-8 -*-
import logging
import traceback
from flask import Blueprint, json, current_app, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from eyesmediapyutils.payload import ReponsePayloadBulider

logger = logging.getLogger(__name__)
system_api = Blueprint("system_api", __name__)
jwt = JWTManager()


def jwt_init(app):
    jwt.init_app(app)

@system_api.before_app_request
# @jwt_required
def load_first():
    print(request.endpoint)
    print(request)

# jwt loader callback:
# callback可以自己定義status code, errorcode與response data
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    app_context = current_app.config["app_context"]
    reponse_payload = ReponsePayloadBulider(app_context.messages)
    try:
        service = UserService(app_context)
        # req_data = request.get_json()
        # data = service.login(None, None, refresh=expired_token.get("identity"))
        resp = json.jsonify(reponse_payload.bulid("156600002", error_desc="Account Login Expire"))
        return resp
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(reponse_payload.bulid("999999999", error_desc="Account Login Expire")), 401


@jwt.unauthorized_loader
def my_unauthorized_token_callback(description):
    app_context = current_app.config["app_context"]
    reponse_payload = ReponsePayloadBulider(app_context.messages)
    return json.jsonify(reponse_payload.bulid("999999999", error_desc=description)), 401


@jwt.invalid_token_loader
def my_invalid_token_callback(description):
    app_context = current_app.config["app_context"]
    reponse_payload = ReponsePayloadBulider(app_context.messages)
    return json.jsonify(reponse_payload.bulid("999999999", error_desc=description)), 401