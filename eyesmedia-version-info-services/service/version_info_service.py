# -*- coding: utf-8 -*-
import logging
import traceback
import time
import yaml
from bson.objectid import ObjectId
from config.constants import Type
from db.mysql_dao import ProductDao, ProjectDao, ReleaseDao
from eyesmediapyutils.exceptions import CommonRuntimeException
from eyesmediapyutils.datetime import DateTimeUtils
from eyesmediapyutils.page import Paging

logger = logging.getLogger(__name__)


class VersionInfoVo(object):
    def __init__(self):
        # 若前端沒給之default值
        self.service_port = -1
        self.service_url = "-"

    def value_of_import(self, request_data, object_type, api_type=None):
        """
        接收前端給的資料

        Parameters
        ----------
        request_data : dict
            前端所給的資料
        object_type : str
            project or product
        api_type: str
            api類型
        """
        self.user = request_data.get("user")
        if api_type == "create":
            self.version = request_data.get("version")
            self.name = request_data.get("name")
            self.object_id = request_data.get("objectId")
            self.note = request_data.get("note")
            self.jira_api_id = request_data.get("jiraApiId")

            # 如果是project 接收project會有的資料
            if object_type == Type.project.value:
                self.project_type = request_data.get("projectType")
                self.language_type = request_data.get("languageType")
                self.git_url = request_data.get("gitUrl")
                self.service_port = request_data.get("servicePort")
                self.service_url = request_data.get("serviceUrl")

        if api_type == "modify":
            self.active_status = request_data.get("activeStatus")
            self.object_id = request_data.get("objectId")
            self.git_url = request_data.get("gitUrl")
            self.project_type = request_data.get("projectType")
            self.language_type = request_data.get("languageType")
            self.service_port = request_data.get("servicePort")
            self.service_url = request_data.get("serviceUrl")
            self.note = request_data.get("note")
            self.jira_api_id = request_data.get("jiraApiId")

        if api_type == "search":
            self.keyword = request_data.get("keyword")
            self.project_type = request_data.get("projectType")
            self.language_type = request_data.get("languageType")
            self.active_status = request_data.get("activeStatus")
            self.name = request_data.get("name")
            self.note = request_data.get("note")

        if api_type == "detail":
            self.object_id = request_data.get("objectId")
            self.object_type = request_data.get("objectType")

    def validate(self, objectType, api_type=None):
        """
        驗證前端資料
        Parameters
        ----------
        objectType: str
        """
        if api_type == "create":
            # 驗證必填欄位
            if self.user is None:
                raise CommonRuntimeException("999900001")
            if self.name is None:
                raise CommonRuntimeException("389900006")

            # 如果是project insert, 驗證其必填欄位
            if objectType == Type.project.value:
                if self.project_type is None:
                    raise CommonRuntimeException("389900008")
                if self.language_type is None:
                    raise CommonRuntimeException("389900007")

                # 另外確認chatbot的連續port號
                with open("port_block.yml", "r") as stream:
                    chatbot_port = yaml.safe_load(stream)["port_block"]["range"]
                for port in chatbot_port:
                    if self.service_port:
                        if port["start"] <= self.service_port <= port["end"]:
                            raise CommonRuntimeException("389900010")

                assert isinstance(self.git_url, (str, type(None))), "999900001"
                assert isinstance(self.service_port, (int, type(None))), "999900001"
                assert isinstance(self.service_url, (str, type(None))), "999900001"
                assert isinstance(self.jira_api_id, (str, type(None))), "999900001"

            #for release table
            if self.version is None:
                raise CommonRuntimeException("999900001")

            # 驗證選 必填欄位之格式
            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.name, str), "999900001"
            assert isinstance(self.version, str), "999900001"
            assert isinstance(self.note, (str, type(None))), "999900001"

        if api_type == "modify":
            if self.object_id is None:
                raise CommonRuntimeException("389900003")
            # 不得針對active_status做modify 只能用archive
            if self.active_status == "0":
                raise CommonRuntimeException("389900004")

            if objectType == Type.project.value:
                assert isinstance(self.service_port, (int, type(None))), "999900001"
                assert isinstance(self.service_url, (str, type(None))), "999900001"
            assert isinstance(self.git_url, (str, type(None))), "999900001"
            assert isinstance(self.project_type, (str, type(None))), "999900001"
            assert isinstance(self.language_type, (str, type(None))), "999900001"
            assert isinstance(self.note, (str, type(None))), "999900001"
            assert isinstance(self.jira_api_id, (str, type(None))), "999900001"

        if api_type == "search":
            assert isinstance(self.keyword, (str, type(None))), "999900001"
            assert isinstance(self.project_type, (str, type(None))), "999900001"
            assert isinstance(self.language_type, (str, type(None))), "999900001"
            assert isinstance(self.active_status, (int, type(None))), "999900001"
            assert isinstance(self.name, (str, type(None))), "999900001"


class VersionInfoService(object):
    def __init__(self, app_context):
        self.__product_base_dao = ProductDao(app_context.mysql_client)
        self.__project_base_dao = ProjectDao(app_context.mysql_client)
        self.__release_dao = ReleaseDao(app_context.mysql_client)
        self.__datetime = DateTimeUtils(app_context.timezone)

    def insert_new(self, object_type, versionVo):
        """
        新增資料至DB的project_base_table or product_base_table 以及 release_table

        Parameters
        ----------
        object_type : str
            project / product
        versionVo : object
            包含所有 input 資訊

        Returns
        -------
        release_id : str
            ObjectId流水號
        """
        ss_time = time.time()

        # for product
        if object_type == Type.product.value:

            data_exist = self.check_exist(object_type, name=versionVo.name)
            # 若存在 則不可新增 直接error
            if data_exist is True:
                logger.error(traceback.format_exc())
                raise CommonRuntimeException("389900001")

            # insert to product_table
            product_id = self.__product_base_dao.insert_to_product_table(product_name=versionVo.name,
                                                                         note=versionVo.note,
                                                                         jira_api=versionVo.jira_api_id)
            # insert to release_table
            release_id = self.__release_dao.insert_to_release_table(product_id=product_id,
                                                                    version=versionVo.version,
                                                                    crt_user=versionVo.user)
            result = dict()
            result["productId"] = product_id
            result["releaseId"] = release_id

        # for project
        elif object_type == Type.project.value:
            data_exist = self.check_exist(object_type, name=versionVo.name, service_port=versionVo.service_port,
                                          service_url=versionVo.service_url)
            # 若存在 則不可新增 直接error
            if data_exist is True:
                logger.error(traceback.format_exc())
                raise CommonRuntimeException("389900001")

            # insert to project_table
            if versionVo.service_port == -1:
                versionVo.service_port = None
            if versionVo.service_url == "-":
                versionVo.service_url = None
            project_id = self.__project_base_dao.insert_to_project_table(project_name=versionVo.name,
                                                                         service_port=versionVo.service_port,
                                                                         git_url=versionVo.git_url,
                                                                         service_url=versionVo.service_url,
                                                                         language_type=versionVo.language_type,
                                                                         project_type=versionVo.project_type,
                                                                         jira_api=versionVo.jira_api_id,
                                                                         note=versionVo.note)

            # insert to release_table
            release_id = self.__release_dao.insert_to_release_table(project_id=project_id,
                                                                    version=versionVo.version,
                                                                    crt_user=versionVo.user)
            result = dict()
            result["projectId"] = project_id
            result["releaseId"] = release_id


        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time

    def modify_db_data(self, object_type, versionVo):
        """
        更改base_table的資料
        Parameters
        ----------
        object_type: str
            project or product
        versionVo: object
            驗證過的前端資料

        Returns
        -------
        object_id: str
        """
        ss_time = time.time()
        # for product
        if object_type == Type.product.value:
            result = self.__product_base_dao.update_to_product_table(versionVo.object_id, note=versionVo.note,
                                                                     jira_api=versionVo.jira_api_id)
        # for project
        else:
            if versionVo.service_port or versionVo.service_url:
                data_exist = self.__project_base_dao.check_exist(versionVo.object_id,
                                                                 service_port=versionVo.service_port, service_url=versionVo.service_url)
                if data_exist is True:
                    logger.error(traceback.format_exc())
                    raise CommonRuntimeException("389900002")
            result = self.__project_base_dao.update_to_project_table(versionVo.object_id,
                                                                     service_port=versionVo.service_port,
                                                                     git_url=versionVo.git_url,
                                                                     service_url=versionVo.service_url,
                                                                     language_type=versionVo.language_type,
                                                                     project_type=versionVo.project_type,
                                                                     jira_api=versionVo.jira_api_id,
                                                                     active_status=versionVo.active_status,
                                                                     note=versionVo.note)

        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time

    # get detail product or project information by id
    def get_detail_info(self, object_type, object_id):
        """
        獲取base_table中的資料細節
        Parameters
        ----------
        object_type: str
            product or project
        object_id: str
            project_id or product_id 共稱object_id

        Returns
        -------
        查詢結果: dict
        """
        ss_time = time.time()
        if object_type == Type.product.value:
            try:
                result = self.__product_base_dao.select_by_id(object_id)
            except:
                logger.error(traceback.format_exc())
                raise CommonRuntimeException("389900009")
        # if object_type == Type.project.value
        else:
            try:
                result = self.__project_base_dao.select_by_id(object_id)
            except:
                logger.error(traceback.format_exc())
                raise CommonRuntimeException("389900009")
        result = _change_to_frontend_style(object_type, result)
        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time

    # check if project or product exist
    def check_exist(self, object_type, name=None, service_port=None, service_url=None):
        """
        確認db中該筆資料是否已經存在
        Parameters
        ----------
        object_type: str
            product_id, project_id
        name: str
            專案或產品名稱
        service_port: int
            服務之port號 若為product則無
        service_url: str
            服務所對應之url 若為product則無

        Returns
        -------
        boolean
        """
        try:
            if object_type == Type.product.value:
                name_exist = self.__product_base_dao.check_insert_validation(name)
                return name_exist
            elif object_type == Type.project.value:
                data_exist = self.__project_base_dao.check_insert_validation(name, service_url, service_port)
                return data_exist
        except:
            logger.error(traceback.format_exc())
            logger.error("Fail to check project/product name exist.")
            raise CommonRuntimeException("999999998")

    def archive_db_data(self, user, object_id, object_type):
        """
        封存專案或產品
        Parameters
        ----------
        user: str, 使用者名稱
        object_id: str, product_id or project_id
        object_type: str, product or project

        Returns
        -------
        product_id or project_id: str
        """
        ss_time = time.time()
        active_status = 0
        if object_type == Type.product.value:
            result = self.__product_base_dao.update_to_product_table(object_id, active_status=active_status)
        else:
            result = self.__project_base_dao.update_to_project_table(object_id, active_status=active_status)

        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time

    def search_from_db(self, object_type, versionVo, page, page_size):
        """
        查找base_table的資料by前端傳入的params
        Parameters
        ----------
        object_type: str
            project or product
        versionVo: object
            驗證過的資料
        page: int
            分頁頁數
        page_size: int
            分頁資料數量

        Returns
        -------
        資料庫查詢結果: list
        """
        ss_time = time.time()
        if object_type == Type.product.value:
            cursor = self.__product_base_dao.search_by_parameters(product_name=versionVo.name,
                                                                  active_status=versionVo.active_status,
                                                                  keyword=versionVo.keyword,
                                                                  note=versionVo.note)

            total_count = cursor.count()
            page_object = Paging(page_no=page, limit=page_size, data_count=total_count)
            # total_page = page_object.get_total_page(total_count)

            result = []
            for row_data in cursor.paginate(page, page_size).dicts():
                result_dict = _change_to_frontend_style(object_type, row_data)
                result.append(result_dict)
        # for project
        else:
            cursor = self.__project_base_dao.search_by_parameters(project_name=versionVo.name,
                                                                  language_type=versionVo.language_type,
                                                                  project_type=versionVo.project_type,
                                                                  active_status=versionVo.active_status,
                                                                  keyword=versionVo.keyword)

            total_count = cursor.count()
            page_object = Paging(page_no=page, limit=page_size, data_count=total_count)

            result = []
            for row_data in cursor.paginate(page, page_size).dicts():
                result_dict = _change_to_frontend_style(object_type, row_data)
                result.append(result_dict)
        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time, page_object


def _change_to_frontend_style(object_type, db_data):
    """
    將資料庫得到的dict格式 轉為前端駝峰式
    Parameters
    ----------
    object_type: str
    db_data: dict

    Returns
    -------
    資料庫結果: dict
        key為駝峰式
    """
    result_dict = dict()
    if object_type == Type.project.value:
        if db_data.get("active_status"):
            result_dict["activeStatus"] = db_data.get("active_status")
        if db_data.get("git_url"):
            result_dict["gitUrl"] = db_data.get("git_url")
        if db_data.get("jira_api_id"):
            result_dict["jiraApiId"] = db_data.get("jira_api_id")
        if db_data.get("language_type"):
            result_dict["languageType"] = db_data.get("language_type")
        if db_data.get("note"):
            result_dict["note"] = db_data.get("note")
        if db_data.get("project_id"):
            result_dict["projectId"] = db_data.get("project_id")
        if db_data.get("project_name"):
            result_dict["projectName"] = db_data.get("project_name")
        if db_data.get("project_type"):
            result_dict["projectType"] = db_data.get("project_type")
        if db_data.get("service_port"):
            result_dict["servicePort"] = db_data.get("service_port")
        if db_data.get("service_url"):
            result_dict["serviceUrl"] = db_data.get("service_url")
    if object_type == Type.product.value:
        if db_data.get("active_status"):
            result_dict["activeStatus"] = db_data.get("active_status")
        if db_data.get("note"):
            result_dict["note"] = db_data.get("note")
        if db_data.get("product_id"):
            result_dict["productId"] = db_data.get("product_id")
        if db_data.get("product_name"):
            result_dict["productName"] = db_data.get("product_name")

    return result_dict
