# -*- coding: utf-8 -*-
import logging
import traceback
from flask import Blueprint, json, current_app, request
from eyesmediapyutils.payload import ReponsePayloadBulider
from eyesmediapyutils.exceptions import CommonRuntimeException
from service.release_service import ReleaseVo, ReleaseService

logger = logging.getLogger(__name__)
release_api = Blueprint("release_api", __name__)


@release_api.route("/release/<string:objectType>/insert", methods=["POST"])
def new_release_version_func(objectType):
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="release_insert")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="release_insert")
        service = ReleaseService(app_context)
        result, cost_time = service.new_release_version(objectType, releaseVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))


@release_api.route("/release/<string:objectType>/get-latest-dependencies", methods=["POST"])
def latest_info_func(objectType):
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="latest_info")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="latest_info")
        service = ReleaseService(app_context)
        result, cost_time = service.latest_release_info(objectType, releaseVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))


@release_api.route("/release/activate", methods=["POST"])
def activate_func():
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="activate")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="activate")
        service = ReleaseService(app_context)
        result, cost_time = service.activate(releaseVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))


@release_api.route("/release/verify", methods=["POST"])
def verify_func():
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="verify")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="verify")
        service = ReleaseService(app_context)
        result, cost_time = service.verify(releaseVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))

@release_api.route("/release/<string:objectType>/history-info", methods=["POST"])
def history_info_func(objectType):
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="history_info")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="history_info")
        service = ReleaseService(app_context)
        result, cost_time = service.get_release_history_info(objectType, releaseVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))

@release_api.route("/release/get-overview", methods=["POST"])
def release_overview_func():
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="release_overview")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="release_overview")
        service = ReleaseService(app_context)
        result, cost_time = service.get_release_overview()
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))

@release_api.route("/release/get-detail", methods=["POST"])
def get_detail_func():
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="get_release_info")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="get_release_info")
        service = ReleaseService(app_context)
        result, cost_time = service.get_specific_releases_info(releaseVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))

@release_api.route("/release/modify", methods=["POST"])
def modify_dependency_func():
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        releaseVo = ReleaseVo()
        releaseVo.value_of_import(req_data, api_type="modify_release_info")

        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        releaseVo.validate(api_type="modify_release_info")
        service = ReleaseService(app_context)
        result, cost_time = service.modify_release(releaseVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))


