# -*- coding: utf-8 -*-
import logging
import traceback
from flask import Blueprint, json, current_app, request
from service.version_info_service import VersionInfoService, VersionInfoVo
from eyesmediapyutils.payload import ReponsePayloadBulider
from eyesmediapyutils.exceptions import CommonRuntimeException

logger = logging.getLogger(__name__)
project_api = Blueprint("project_api", __name__)


@project_api.route("/<string:objectType>/create", methods=["POST"])
def new_release_func(objectType):
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        versionVo = VersionInfoVo()
        versionVo.value_of_import(req_data, objectType, api_type="create")
        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        versionVo.validate(objectType, api_type="create")
        service = VersionInfoService(app_context)
        result, cost_time = service.insert_new(objectType, versionVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))


@project_api.route("/<string:objectType>/modify", methods=["POST"])
def modify_func(objectType):
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        versionVo = VersionInfoVo()
        versionVo.value_of_import(req_data, objectType, api_type="modify")
        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        versionVo.validate(objectType, api_type="modify")
        service = VersionInfoService(app_context)
        result, cost_time = service.modify_db_data(objectType, versionVo)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))

@project_api.route("/detail", methods=["POST"])
def get_detail():
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        if not req_data.get("user") or not req_data.get("objectId") or not req_data.get("objectType"):
            return json.jsonify(response_payload.bulid("999900001"))
        service = VersionInfoService(app_context)
        result, cost_time = service.get_detail_info(req_data["objectType"], req_data["objectId"])

        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))

    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))


@project_api.route("/archive", methods=["POST"])
def archive_func():
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))
    if not req_data.get("user") or not req_data.get("objectId") or not req_data.get("objectType"):
        return json.jsonify(response_payload.bulid("999900001"))

    try:
        service = VersionInfoService(app_context)
        result, cost_time = service.archive_db_data(req_data.get("user"), req_data.get("objectId"),
                                                    req_data.get("objectType"))
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))


@project_api.route("/<string:objectType>/search", methods=["POST"])
def search_func(objectType):
    app_context = current_app.config["app_context"]
    response_payload = ReponsePayloadBulider(app_context.messages)

    if request.method == "POST":
        req_data = request.get_json()
        versionVo = VersionInfoVo()
        versionVo.value_of_import(req_data, objectType, api_type="search")
        if not req_data:
            logger.error("json body is empty")
            return json.jsonify(response_payload.bulid("999900001"))

    try:
        if req_data.get("page") is not None:
            page = req_data["page"]
        else:
            page = 1
        if req_data.get("pageSize") is not None:
            page_size = req_data["pageSize"]
        else:
            page_size = 20
        versionVo.validate(objectType, api_type="search")
        service = VersionInfoService(app_context)
        result, cost_time, page_object = service.search_from_db(objectType, versionVo, page, page_size)
        return json.jsonify(response_payload.bulid("996600001", cost_time=cost_time, data=result, paging=page_object))
    except CommonRuntimeException as crex:
        logger.error(traceback.format_exc())
        return json.jsonify((response_payload.bulid_from_exception(crex)))
    except AssertionError as ae:
        return json.jsonify((response_payload.bulid(ae.args[0])))
    except:
        logger.error(traceback.format_exc())
        return json.jsonify(response_payload.bulid("999999999"))
