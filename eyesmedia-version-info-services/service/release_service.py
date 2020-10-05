# -*- coding: utf-8 -*-
import logging
import traceback
import time
from itertools import groupby
from operator import itemgetter
from collections import defaultdict
from datetime import datetime
from config.constants import Type
from db.mysql_dao import ReleaseDao, ReleaseMappingDao, SearchViewDao, ProductDao, ProjectDao
from eyesmediapyutils.exceptions import CommonRuntimeException
from eyesmediapyutils.datetime import DateTimeUtils


logger = logging.getLogger(__name__)


class ReleaseVo(object):
    def __init__(self):
        pass

    def value_of_import(self, request_data, api_type=None):
        """
        import並轉換前端給的資料

        Parameters
        ----------
        request_data : dict
            前端所給的資料
        api_type : str
            自己定義的constants，用來決定如何檢查及import
        """
        if api_type == "release_insert":
            self.user = request_data.get("user")
            self.object_id = request_data.get("objectId")
            self.version = request_data.get("version")
            self.release_note = request_data.get("releaseNote")
            self.dependency_id_list = request_data.get("dependencyId")

        if api_type == "latest_info":
            self.user = request_data.get("user")
            self.object_id = request_data.get("objectId")

        if api_type == "activate":
            self.user = request_data.get("user")
            self.release_id = request_data.get("releaseId")
            self.running_status = request_data.get("runningStatus")

        if api_type == "verify":
            self.user = request_data.get("user")
            self.release_id = request_data.get("releaseId")
            self.release_status = request_data.get("releaseStatus")

        if api_type == "history_info":
            self.user = request_data.get("user")
            self.object_id = request_data.get("objectId")
            self.get_running = request_data.get("getRunning")

        if api_type == "release_overview":
            self.user = request_data.get("user")

        if api_type == "get_release_info":
            self.user = request_data.get("user")
            self.release_id_list = request_data.get("releaseId")

        if api_type == "modify_release_info":
            self.user = request_data.get("user")
            self.release_id = request_data.get("releaseId")
            self.dependency_id_list = request_data.get("dependencyId")
            self.release_note = request_data.get("releaseNote")

    def validate(self, api_type=None):
        if api_type == "release_insert":
            # check if data exists
            if self.user is None or self.object_id is None or self.version is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.object_id, str), "999900001"
            assert isinstance(self.version, str), "999900001"
            assert isinstance(self.release_note, (str, type(None))), "999900001"  # check data is None or str
            assert isinstance(self.dependency_id_list, (list, type(None))), "999900001"

        if api_type == "latest_info":
            if self.user is None or self.object_id is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.object_id, str), "999900001"

        if api_type == "activate":
            if self.user is None or self.release_id is None or self.running_status is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.release_id, str), "999900001"
            assert isinstance(self.running_status, int), "999900001"

        if api_type == "verify":
            if self.user is None or self.release_id is None or self.release_status is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.release_id, str), "999900001"
            assert isinstance(self.release_status, int), "999900001"

        if api_type == "history_info":
            if self.user is None or self.object_id is None or self.get_running is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.object_id, str), "999900001"
            assert isinstance(self.get_running, bool), "999900001"

        if api_type == "release_overview":
            if self.user is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"

        if api_type == "get_release_info":
            if self.user is None or self.release_id_list is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.release_id_list, list), "999900001"

        if api_type == "modify_release_info":
            if self.user is None or self.release_id is None:
                raise CommonRuntimeException("999900001")

            assert isinstance(self.user, str), "999900001"
            assert isinstance(self.release_id, str), "999900001"
            assert isinstance(self.dependency_id_list, list), "999900001"
            assert isinstance(self.release_note, (str, type(None))), "999900001"


class ReleaseService(object):
    def __init__(self, app_context):
        self.__release_dao = ReleaseDao(app_context.mysql_client)
        self.__release_mapping_dao = ReleaseMappingDao(app_context.mysql_client)
        self.__product_dao = ProductDao(app_context.mysql_client)
        self.__project_dao = ProjectDao(app_context.mysql_client)
        self.__search_view_dao = SearchViewDao(app_context.mysql_client)
        self.__datetime = DateTimeUtils(app_context.timezone)

    def new_release_version(self, object_type, releaseVo):
        """
        新增release version to release table and release_mapping_table
        如果沒有dependency 則只會新增到release table
        Parameters
        ----------
        object_type: str
            product or project
        releaseVo: object
            前端獲得之資料
        Returns
        -------
        str
            new_release_id
        """
        ss_time = time.time()

        if object_type == Type.project.value:
            # check active status and version
            _is_active = False
            _version_duplicate = False
            cursor = self.__project_dao.get_active_and_version(releaseVo.object_id, active_status=1, version=releaseVo.version).dicts()
            for value in cursor:
                if value["active_status"] == 1:
                    _is_active = True
                if value["version"] == releaseVo.version:
                    _version_duplicate = True
            # 根據 boolean raise 不同的 error
            if _is_active is False and _version_duplicate is True:
                raise CommonRuntimeException("389900014")
            if _is_active is False:
                raise CommonRuntimeException("389900012")
            if _version_duplicate is True:
                raise CommonRuntimeException("389900015")

            new_release_id = self.__release_dao.insert_to_release_table(project_id=releaseVo.object_id,
                                                                        version=releaseVo.version,
                                                                        crt_user=releaseVo.user,
                                                                        release_note=releaseVo.release_note)
            self.__release_mapping_dao.insert_to_release_mapping_table(release_id=new_release_id,
                                                                        dependency_id_list=releaseVo.dependency_id_list)

        else:
            # check active status
            _is_active = self.__product_dao.check_exist(releaseVo.object_id, active_status=1)
            if _is_active is True:
                new_release_id = self.__release_dao.insert_to_release_table(product_id=releaseVo.object_id,
                                                                            version=releaseVo.version,
                                                                            crt_user=releaseVo.user,
                                                                            release_note=releaseVo.release_note)
                self.__release_mapping_dao.insert_to_release_mapping_table(release_id=new_release_id,
                                                                           dependency_id_list=releaseVo.dependency_id_list)
            else:
                raise CommonRuntimeException("389900012")

        cost_time = round(time.time() - ss_time, 2)
        return new_release_id, cost_time

    def latest_release_info(self, object_type, releaseVo):
        """
        獲取從資料庫search_view得到的最新所有相關的套件或服務之名字及版本號
        Parameters
        ----------
        object_type: str
            project or product
        releaseVo: object
            驗證過的前端資料

        Returns
        -------
        list
            查詢結果
        """
        ss_time = time.time()

        # 從 search view 中拿取 release info
        if object_type == Type.project.value:
            result_of_search_view = self.__search_view_dao.get_release_info(object_type, project_id=releaseVo.object_id)
        else:
            result_of_search_view = self.__search_view_dao.get_release_info(object_type, product_id=releaseVo.object_id)
        # 取得最新版本的單筆資料(view)(release_version)
        try:
            latest_view_data = result_of_search_view.limit(1).get()
        except:
            cost_time = round(time.time() - ss_time, 2)
            return None, cost_time

        # 從 release table 中拿取 release info
        if object_type == Type.project.value:
            result_of_release_table = self.__release_dao.get_release_info(object_type, project_id=releaseVo.object_id)
        else:
            result_of_release_table = self.__release_dao.get_release_info(object_type, product_id=releaseVo.object_id)
        # 取得最新版本的單筆資料(table)
        try:
            latest_data_of_release_table = result_of_release_table.limit(1).get()
        except:
            raise CommonRuntimeException("389900009")
        
        # 檢查 dependency data 是否真的是上一個 release 的資料
        if latest_data_of_release_table.version != latest_view_data.release_table.release_version:
            cost_time = round(time.time() - ss_time, 2)
            return None, cost_time
        else:
            result = list()
            result_dict = dict()
            for db_data in result_of_search_view.dicts():
                # 如果crt_date相符(代表為the latest)
                if db_data["release_version"] == latest_data_of_release_table.version:
                    if db_data["product_name"] is not None:
                        result_dict["name"] = db_data["product_name"]
                    else:
                        result_dict["name"] = db_data["project_name"]
                    result_dict["version"] = db_data["dependency_version"]
                    result.append(result_dict)
                    result_dict = {}

            cost_time = round(time.time() - ss_time, 2)
            return result, cost_time

    def verify(self, releaseVo):
        """
        修改release_table的release_status
        Parameters
        ----------
        releaseVo :object of ReleaseVo

        Returns
        -------
        str
            verify 的 release_id
        """
        ss_time = time.time()

        result = self.__release_dao.update_by_parameters(release_id=releaseVo.release_id,
                                                         release_status=releaseVo.release_status,
                                                         mdy_user=releaseVo.user, mdy_date=datetime.utcnow())

        # 查無資料
        if result is None:
            raise CommonRuntimeException("389900002")

        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time

    def activate(self, releaseVo):
        """
        修改release_table的running_status
        Parameters
        ----------
        releaseVo: object

        Returns
        -------
        str release_id
        """
        ss_time = time.time()

        # 檢查是否能關閉
        if releaseVo.running_status == 0:
            if self.__release_mapping_dao.check_parent_dependency(releaseVo.release_id) is True:
                raise CommonRuntimeException("389900011")

        # 若running_status為1 則所有套件 服務都必須啟動
        if releaseVo.running_status == 1:
            release_status = self.__release_dao.get_release_status_by_id(releaseVo.release_id)
            if release_status != 1:
                raise CommonRuntimeException("389900016")

            # get dependency_id
            try:
                # 只建立出語法
                dep_ids_from_view = self.__search_view_dao.get_dependency_id(releaseVo.release_id)
                list_of_dep_ids = list()
                # 連線到db並且拿出資料，並且判斷有無dependency
                if dep_ids_from_view.count() == 0:
                    pass
                else:
                    for data in dep_ids_from_view.dicts():
                        list_of_dep_ids.append(data["dependency_id"])
            except:
                raise CommonRuntimeException("389900009")

            # update dependency_id running_status to 1
            if len(list_of_dep_ids) > 0:
                self.__release_dao.update_by_parameters(list_of_dep_ids, 
                                                        running_status=releaseVo.running_status,
                                                        mdy_date=datetime.utcnow(),
                                                        mdy_user=releaseVo.user)

        # update release_id running_status
        release_id = self.__release_dao.update_by_parameters(str(releaseVo.release_id),
                                                             running_status=releaseVo.running_status,
                                                             mdy_date=datetime.utcnow(),
                                                             mdy_user=releaseVo.user)

        if release_id is None:
            raise CommonRuntimeException("389900002")
        cost_time = round(time.time() - ss_time, 2)
        return release_id, cost_time

    def get_release_history_info(self, object_type, releaseVo):
        """
        獲取從資料庫search_view得到的最新所有相關的套件或服務之名字及版本號
        Parameters
        ----------
        object_type: str, project or product
        releaseVo: object 驗證過的前端資料

        Returns
        -------
        result: list 查詢結果
        """
        ss_time = time.time()

        if object_type == Type.project.value:
            search_result = self.__release_dao.get_data_by_object_id(get_running_status=releaseVo.get_running, project_id=releaseVo.object_id)
        if object_type == Type.product.value:
            search_result = self.__release_dao.get_data_by_object_id(get_running_status=releaseVo.get_running, product_id=releaseVo.object_id)


        # 更換 data form
        result = []
        check_duplicate = "" # 用來檢查是否更換到下一個版號
        temp_dict = defaultdict(list)
        search_result = list(search_result.dicts())
        for dict_data in search_result:
            if check_duplicate != dict_data["release_id"]:
                # 跳過第一個空資料
                if check_duplicate != "":
                    result.append(temp_dict)

                check_duplicate = dict_data["release_id"]

                temp_dict = defaultdict(list) # 清空上一個版本的資料
                if dict_data.get("product_id") is None:
                    temp_dict.update({
                        "releaseDate": self.__datetime.utc_to_localize(dict_data.get("crt_date")).strftime("%Y/%m/%d %H:%M"),
                        "projectId": dict_data.get("project_id"),
                        "releaseId": dict_data.get("release_id"),
                        "releaseNote": dict_data.get("release_note"),
                        "releaseVersion": dict_data.get("version")
                    })
                else:
                    temp_dict.update({
                        "releaseDate": self.__datetime.utc_to_localize(dict_data.get("crt_date")).strftime(
                            "%Y/%m/%d %H:%M"),
                        "productId": dict_data.get("product_id"),
                        "releaseId": dict_data.get("release_id"),
                        "releaseNote": dict_data.get("release_note"),
                        "releaseVersion": dict_data.get("version")
                    })
                # 將 dependency 資料放在一起
                temp_dict["dependency"].append({
                    "dependencyId": dict_data.get("dependency_id"),
                    "dependencyProjectName": dict_data.get("dependency_project_name"),
                    "dependencyVersion": dict_data.get("dependency_version")
                })

            else:
                # 將 dependency 資料放在一起
                temp_dict["dependency"].append({
                    "dependencyId": dict_data.get("dependency_id"),
                    "dependencyProjectName": dict_data.get("dependency_project_name"),
                    "dependencyVersion": dict_data.get("dependency_version")
                })
        # 放入最後一筆資料
        if temp_dict != {}:
            result.append(temp_dict)

        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time

    def get_release_overview(self):
        """
        獲取從資料庫release_table得到的所有dependency版本

        Returns
        -------
        result: list 查詢結果
        """
        ss_time = time.time()

        project_cursor = self.__release_dao.project_release_overview()
        product_cursor = self.__release_dao.product_release_overview()
        _version_dict = defaultdict(list)
        _name_list = list()

        # 先組合project的資料
        project_items = list(project_cursor.dicts())
        groups = groupby(project_items, itemgetter("project_id", "project_name"))
        project_result = list()
        for key, data in groups:
            version = list()
            for item in data:
                version.append({
                    "releaseId": item.get("release_id"),
                    "version": item.get("version")
                })
            version.sort(key=itemgetter("version"), reverse=True)
            project_result.append({
                "id": key[0], # project_id
                "name": key[1], # project_name
                "version": version
            })

        # 組合product資料
        product_items = list(product_cursor.dicts())
        groups = groupby(product_items, itemgetter("product_id", "product_name"))
        product_result = list()
        for key, data in groups:
            version = list()
            for item in data:
                version.append({
                    "releaseId": item.get("release_id"),
                    "version": item.get("version")
                })
            version.sort(key=itemgetter("version"), reverse=True)
            product_result.append({
                "id": key[0], # product_id
                "name": key[1], # product_name
                "version": version
            })

        result = dict()
        result["Project"] = project_result
        result["Product"] = product_result

        # 方法二
        # project_result = list()
        # for project_item in project_cursor.dicts():
        #     _version_dict[project_item["project_name"]].append({"releaseId": project_item["release_id"],
        #                                                         "version": project_item["version"]
        #                                                         })
        #     _version_dict["projectId"] = project_item.get("project_id")
        #     if project_item["project_name"] not in _name_list:
        #         project_result.append({"projectName": project_item["project_name"],
        #                                "version": _version_dict[project_item["project_name"]],
        #                                "projectId": _version_dict["projectId"]})
        #         _name_list.append(project_item["project_name"])
        #
        # # 清空
        # _version_dict = defaultdict(list)
        # _name_list = list()
        #
        # product_result = list()
        # for product_item in product_cursor.dicts():
        #     _version_dict[product_item["product_name"]].append({"releaseId": product_item["release_id"],
        #                                                         "version": product_item["version"]
        #                                                         })
        #     _version_dict["productId"] = product_item.get("productId")
        #     if product_item["product_name"] not in _name_list:
        #         product_result.append({"productName": product_item["product_name"],
        #                                "version": _version_dict[product_item["product_name"]],
        #                                "productId": _version_dict["productId"]})
        #         _name_list.append(product_item["product_name"])
        #
        # result = dict()
        # result["project"] = project_result
        # result["product"] = product_result

        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time

    def get_specific_releases_info(self, releaseVo):
        """
        依據 release_id_list 拿出對應的 release 資料

        Returns
        -------
        result: list 查詢結果
        """
        ss_time = time.time()

        cursor = self.__release_dao.search_by_id_list(releaseVo.release_id_list)

        # 過濾要給前端的column並且轉換格式
        search_result = list(cursor)
        if not search_result:
            raise CommonRuntimeException("389900009")
        arranged_result = []
        check_duplicate = search_result[0]["release_id"]
        dict_data = defaultdict(list)
        for value in search_result:
            if value["release_id"] != check_duplicate:
                # 若無 dependency 依然回傳一個空 list
                if not "dependency" in dict_data:
                    dict_data["dependency"] = list()

                arranged_result.append(dict_data)
                dict_data = defaultdict(list) # 清空
                check_duplicate = value["release_id"]
            else:
                if value["dependency_id"]: # 避免在第一筆資料插入空的dependency
                    dict_data["dependency"].append({
                        "dependencyId": value["dependency_id"],
                        "dependencyName": value["dependency_name"],
                        "dependencyVersion": value["dependency_version"]
                    })
            dict_data["crtDate"] = self.__datetime.utc_to_localize(value["crt_date"]).strftime("%Y/%m/%d %H:%M")
            dict_data["crtUser"] = value["crt_user"]
            dict_data["mdyUser"] = value["mdy_user"]
            dict_data["releaseId"] = value["release_id"]
            dict_data["releaseNote"] = value["release_note"]
            dict_data["releaseStatus"] = value["release_status"]
            dict_data["runningStatus"] = value["running_status"]
            dict_data["version"] = value["version"]
            dict_data["languageType"] = value["language_type"]

            if value["product_name"] is not None:
                dict_data["name"] = value["product_name"]
            else:
                dict_data["name"] = value["project_name"]
            if value["mdy_date"] is not None:
                dict_data["mdyDate"] = self.__datetime.utc_to_localize(value["mdy_date"]).strftime("%Y/%m/%d %H:%M")
            else:
                dict_data["mdyDate"] = None

            if value["project_id"] is not None:
                dict_data["isProduct"] = False
            else:
                dict_data["isProduct"] = True



        # append 最後一筆 data
        if not "dependency" in dict_data:
            dict_data["dependency"] = list()
        arranged_result.append(dict_data)

        cost_time = round(time.time() - ss_time, 2)
        return arranged_result, cost_time

    def modify_release(self, releaseVo):
        """
        更改 release info
        Parameters
        ----------
        releaseVo: object
            驗證過的前端資料

        Returns
        -------
        release_id: str
        """
        ss_time = time.time()

        # 更新 release note
        if releaseVo.release_note is not None:
            self.__release_dao.update_by_parameters(release_id=releaseVo.release_id, release_note=releaseVo.release_note)

        # 更新 dependency
        release_status, running_status, dependency_list= self.__release_dao.get_status_and_dependency_by_id(releaseVo.release_id)

        if (release_status != 0 or running_status != 0) and dependency_list != releaseVo.dependency_id_list:
            raise CommonRuntimeException("389900013")
        # dependency 有做更動再寫入db
        if dependency_list != releaseVo.dependency_id_list:
            self.__release_mapping_dao.modify_dependency_by_release_id(release_id=releaseVo.release_id,
                                                                        dependency_id_list=releaseVo.dependency_id_list)
        result = releaseVo.release_id

        cost_time = round(time.time() - ss_time, 2)
        return result, cost_time