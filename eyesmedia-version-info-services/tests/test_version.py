# -*- coding: utf-8 -*-
try:
    from config.application import app_context
    from db.mysql_dao import ProductDao, ProjectDao, ReleaseDao
    from service.version_info_service import VersionInfoVo, VersionInfoService
    from eyesmediapyutils.exceptions import CommonRuntimeException
except:
    import os
    import sys
    import peewee
    from peewee import MySQLDatabase
    sys.path.append(os.path.dirname(os.getcwd()))
    from config.application import app_context
    from db.mysql_dao import ProductDao, ProjectDao, ReleaseDao
    from service.version_info_service import VersionInfoVo, VersionInfoService
    from eyesmediapyutils.exceptions import CommonRuntimeException
import unittest
from unittest.mock import patch


def request_product_data(full=None, fail=None):
    data = {
        "version": "1.0",
        "name": "eyesmedia_test_prodcut_s",
        "user": "product測試者"
    }
    if full:
        data.update({
            "objectId": "test_product_id",
            "note": "測試用prodcut"
        })
    if fail == "name":
        data.pop("name")
    if fail == "active_status":
        data.update({
            "activeStatus": "0"
        })
    return data


def request_project_data(full=None, port=None, fail=None):
    data = {
        "version": "1.0",
        "name": "eyesmedia_test_project_s",
        "user": "project測試者",
        "projectType": "FrontEnd",
        "languageType": "Python",
    }
    if full:
        data.update({
            "objectId": "test_project_id",
            "gitUrl": "http://localhost",
            "servicePort": 65535,
            "serviceUrl": "/project/test",
            "note": "測試用project"
        })
    if port == "fail":
        data.update({"servicePort": 48001})
    if fail == "languageType":
        data.pop("languageType")
    if fail == "service_port":
        data.pop("servicePort")
    if fail == "service_url":
        data["serviceUrl"] = 123456
    return data


def search_data():
    data = {
        "keyword": "keyword",
        "projectType": "FrontEnd",
        "languageType": "Python",
        "activeStatus": 1,
        "name": "search_name",
        "note": "測試用note"
    }
    return data


class VoTestCase(unittest.TestCase):
    def test_VersionInfoVo(self):
        self.assertRaisesRegex(CommonRuntimeException, "389900006", self.VersionInfoVo_create_product_fail)
        self.assertRaisesRegex(CommonRuntimeException, "389900010", self.VersionInfoVo_create_project_fail)
        self.assertRaisesRegex(CommonRuntimeException, "389900007", self.VersionInfoVo_create_project_fail_2)
        self.assertRaisesRegex(CommonRuntimeException, "389900004", self.VersionInfoVo_modify_product_fail)
        self.assertRaisesRegex(AssertionError, "999900001", self.VersionInfoVo_modify_project_fail)

    def test_VersionInfoVo_create_product(self):
        """
        1.測試versioninfovo api_type = create
        2.判斷request_product與versioninfovo要一致

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "product"
        request = request_product_data()
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")
        assert version_vo.version == request.get("version")
        assert version_vo.name == request.get("name")
        assert version_vo.note == request.get("note")

    def test_VersionInfoVo_create_project(self):
        """
        1.測試versioninfovo api_type = create
        2.判斷request_project與versioninfovo要一致

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "project"
        request = request_project_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")
        assert version_vo.version == request.get("version")
        assert version_vo.name == request.get("name")
        assert version_vo.user == request.get("user")
        assert version_vo.object_id == request.get("objectId")
        assert version_vo.note == request.get("note")
        assert version_vo.git_url == request.get("gitUrl")
        assert version_vo.project_type == request.get("projectType")
        assert version_vo.language_type == request.get("languageType")
        assert version_vo.service_port == request.get("servicePort")
        assert version_vo.service_url == request.get("serviceUrl")

    def test_VersionInfoVo_modify_product(self):
        """
        1.測試versioninfovo api_type = modify
        2.判斷request_product與versioninfovo要一致

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "product"
        request = request_product_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")
        assert version_vo.object_id == request.get("objectId")
        assert version_vo.user == request.get("user")
        assert version_vo.note == request.get("note")

    def test_VersionInfoVo_modify_project(self):
        """
        1.測試versioninfovo api_type = modify
        2.判斷request_project與versioninfovo要一致

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "project"
        request = request_project_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")
        assert version_vo.object_id == request.get("objectId")
        assert version_vo.user == request.get("user")
        assert version_vo.note == request.get("note")
        assert version_vo.git_url == request.get("gitUrl")
        assert version_vo.project_type == request.get("projectType")
        assert version_vo.language_type == request.get("languageType")
        assert version_vo.service_port == request.get("servicePort")
        assert version_vo.service_url == request.get("serviceUrl")

    def test_VersionInfoVo_search(self):
        """
        1.測試versioninfovo api_type = search
        2.判斷request與versioninfovo要一致

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "product"
        request = search_data()
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="search")
        version_vo.validate(objectType, api_type="search")
        assert version_vo.keyword == request.get("keyword")
        assert version_vo.name == request.get("name")
        assert version_vo.active_status == request.get("activeStatus")
        assert version_vo.language_type == request.get("languageType")
        assert version_vo.project_type == request.get("projectType")

    def VersionInfoVo_create_product_fail(self):
        """
        1.測試versioninfovo api_type = create
        2.預期request_product 因少name欄位 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "product"
        request = request_product_data(fail="name")
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")

    def VersionInfoVo_create_project_fail(self):
        """
        1.測試 VersionInfoService 的 api_type = create
        2.port 在chatbot的連續port號 內會報錯 389900010

        """
        objectType = "project"
        request = request_project_data(full=True, port="fail")
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")

    def VersionInfoVo_create_project_fail_2(self):
        """
        1.測試versioninfovo api_type = create
        2.預期request_project 因少 languageType 欄位 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "project"
        request = request_project_data(full=True, fail="languageType")
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")

    def VersionInfoVo_modify_product_fail(self):
        """
        1.測試versioninfovo api_type = modify
        2.預期request_product 因為active_status = 0 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "product"
        request = request_product_data(full=True, fail="active_status")
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")

    def VersionInfoVo_modify_project_fail(self):
        """
        1.測試versioninfovo api_type = modify
        2.預期request_product 因為 git_url 不存在 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        objectType = "project"
        request = request_project_data(full=True, fail="service_url")
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")


class VersionTestCase(unittest.TestCase):
    def test_insert_new_fail(self):
        # check_exists 必定為True
        check_insert_validation_patch = patch.object(ProductDao, 'check_insert_validation',
                                                     side_effect=self.mock_check_insert_validation)
        check_insert_validation_patch.start()
        check_insert_validation_patch2 = patch.object(ProjectDao, 'check_insert_validation',
                                                      side_effect=self.mock_check_insert_validation)
        check_insert_validation_patch2.start()

        self.assertRaisesRegex(CommonRuntimeException, "389900001", self.insert_new_product_fail)
        self.assertRaisesRegex(CommonRuntimeException, "389900001", self.insert_new_project_fail)
        check_insert_validation_patch.stop()
        check_insert_validation_patch2.stop()
        # check_exists 關掉mock

    def insert_new_product_fail(self):
        """
        1.測試 VersionInfoService 的 insert_new function - product
        2.insert_new時, check_exists 為True, 需要報錯error 389900001

        """
        objectType = "product"
        request = request_product_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")
        service = VersionInfoService(app_context)
        result, cost_time = service.insert_new(objectType, version_vo)

    def test_insert_new_prodcut_success(self):
        """
        1.測試 VersionInfoService 的 insert_new function
        2.insert_new時, check_exists 為False 預期拿到的result 會與 release_id 一致

        """
        objectType = "product"
        request = request_product_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")
        service = VersionInfoService(app_context)

        # mock insert_to_product_table
        insert_to_product_table_patch = patch.object(ProductDao, 'insert_to_product_table',
                                                     side_effect=self.mock_insert_to_product_table)
        insert_to_product_table_patch.start()
        # mock insert_to_release_table
        insert_to_release_table_patch = patch.object(ReleaseDao, 'insert_to_release_table',
                                                     side_effect=self.mock_insert_to_release_table)
        insert_to_release_table_patch.start()

        result, cost_time = service.insert_new(objectType, version_vo)
        assert result == {"productId": "12345", "releaseId": "23456"}
        insert_to_product_table_patch.stop()
        insert_to_release_table_patch.stop()

    def test_insert_new_project_success(self):
        """
        1.測試 VersionInfoService 的 insert_new function
        2.insert_new時, check_exists 為False 預期拿到的result 會與 release_id 一致

        """
        objectType = "project"
        request = request_project_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")
        service = VersionInfoService(app_context)

        # mock insert_to_project_table
        insert_to_project_table_patch = patch.object(ProjectDao, 'insert_to_project_table',
                                                     side_effect=self.mock_insert_to_project_table)
        insert_to_project_table_patch.start()
        # mock insert_to_release_table
        insert_to_release_table_patch = patch.object(ReleaseDao, 'insert_to_release_table',
                                                     side_effect=self.mock_insert_to_release_table)
        insert_to_release_table_patch.start()

        result, cost_time = service.insert_new(objectType, version_vo)
        assert result == {"projectId": "12345", "releaseId": "23456"}
        insert_to_project_table_patch.stop()
        insert_to_release_table_patch.stop()

    def insert_new_project_fail(self):
        """
        1.測試 VersionInfoService 的 insert_new function - project
        2.check_exists 為True 需要報錯error 389900001

        """
        objectType = "project"
        request = request_project_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="create")
        version_vo.validate(objectType, api_type="create")
        service = VersionInfoService(app_context)
        result, cost_time = service.insert_new(objectType, version_vo)

    def test_modify_db_data_product_success(self):
        """
        1.測試 VersionInfoService 的 modify_db_data function - product
        2.測試modify成功案例

        """
        objectType = "product"
        request = request_product_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")
        service = VersionInfoService(app_context)

        # mock update_to_product_table
        update_to_product_table_patch = patch.object(ProductDao, 'update_to_product_table',
                                                     side_effect=self.mock_update_to_product_table)
        update_to_product_table_patch.start()

        result, cost_time = service.modify_db_data(objectType, version_vo)
        assert result == "update12345"

    def test_modify_db_data_project_success(self):
        """
        1.測試 VersionInfoService 的 modify_db_data function - project
        2.測試modify成功案例

        """
        objectType = "project"
        request = request_project_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")
        service = VersionInfoService(app_context)

        # mock update_to_product_table
        update_to_project_table_patch = patch.object(ProjectDao, 'update_to_project_table',
                                                     side_effect=self.mock_update_to_project_table)
        update_to_project_table_patch.start()
        # # mock check_exist
        check_exist_by_id_patch = patch.object(ProjectDao, 'check_exist', side_effect=self.mock_check_exist)
        check_exist_by_id_patch.start()

        result, cost_time = service.modify_db_data(objectType, version_vo)
        assert result == "update12345"

    def modify_db_data_product_fail1(self):
        """
        1.測試 VersionInfoService 的 modify_db_data function - product
        2.check_exist_by_id 為False 的情形下報錯 - 389900002

        """
        objectType = "product"
        request = request_product_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")
        service = VersionInfoService(app_context)
        result, cost_time = service.modify_db_data(objectType, version_vo)

    def modify_db_data_project_fail1(self):
        """
        1.測試 VersionInfoService 的 modify_db_data function - project
        2.check_exist_by_id 為False 的情形下報錯 - 389900002

        """
        objectType = "project"
        request = request_project_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="modify")
        version_vo.validate(objectType, api_type="modify")
        service = VersionInfoService(app_context)
        result, cost_time = service.modify_db_data(objectType, version_vo)

    def test_get_detail_info_fail(self):
        self.assertRaisesRegex(CommonRuntimeException, "389900009", self.get_detail_info_product_fail)
        self.assertRaisesRegex(CommonRuntimeException, "389900009", self.get_detail_info_project_fail)

    def test_get_detail_info_product_success(self):
        """
        1.測試 VersionInfoService 的 get_detail_info function - product
        2.get_detail_info 時, 會正常回傳

        """
        objectType = "product"
        object_id = "object_id123"
        # mock select_by_id
        select_by_id_patch = patch.object(ProductDao, 'select_by_id', side_effect=self.mock_select_by_id_product)
        select_by_id_patch.start()

        service = VersionInfoService(app_context)
        result, cost_time = service.get_detail_info(objectType, object_id)
        assert result["productName"] == "prodcut12345"
        select_by_id_patch.stop()

    def test_get_detail_info_project_success(self):
        """
        1.測試 VersionInfoService 的 get_detail_info function - project
        2.get_detail_info 時, 會正常回傳

        """
        objectType = "project"
        object_id = "object_id123"
        # mock select_by_id
        select_by_id_patch = patch.object(ProjectDao, 'select_by_id', side_effect=self.mock_select_by_id_project)
        select_by_id_patch.start()

        service = VersionInfoService(app_context)
        result, cost_time = service.get_detail_info(objectType, object_id)
        assert result["projectName"] == "project12345"
        select_by_id_patch.stop()

    def get_detail_info_product_fail(self):
        """
        1.測試 VersionInfoService 的 get_detail_info function - product
        2.select_by_id 為 fail 時, 會回報錯誤 389900009

        """
        objectType = "product"
        object_id = "fail"
        # mock select_by_id
        select_by_id_patch = patch.object(ProductDao, 'select_by_id', side_effect=self.mock_select_by_id_product)
        select_by_id_patch.start()

        service = VersionInfoService(app_context)
        result, cost_time = service.get_detail_info(objectType, object_id)
        assert result["productName"] == "prodcut12345"
        select_by_id_patch.stop()

    def get_detail_info_project_fail(self):
        """
        1.測試 VersionInfoService 的 get_detail_info function - project
        2.select_by_id 為 fail 時, 會回報錯誤 389900009

        """
        objectType = "project"
        object_id = "fail"
        # mock select_by_id
        select_by_id_patch = patch.object(ProjectDao, 'select_by_id', side_effect=self.mock_select_by_id_project)
        select_by_id_patch.start()

        service = VersionInfoService(app_context)
        result, cost_time = service.get_detail_info(objectType, object_id)
        assert result["projectName"] == "project12345"
        select_by_id_patch.stop()

    def test_archive_db_data_product_success(self):
        """
        1.測試 VersionInfoService 的 archive_db_data function - product
        2.archive_db_data 正常回傳

        """
        objectType = "product"
        user = "username"
        object_id = "object_product"
        service = VersionInfoService(app_context)
        # mock update_to_product_table
        update_to_product_table_patch = patch.object(ProductDao, 'update_to_product_table',
                                                     side_effect=self.mock_update_to_product_table)
        update_to_product_table_patch.start()

        result, cost_time = service.archive_db_data(user, object_id, objectType)
        assert result == "update12345"
        update_to_product_table_patch.stop()

    def test_archive_db_data_project_success(self):
        """
        1.測試 VersionInfoService 的 archive_db_data function - project
        2.archive_db_data 正常回傳

        """
        objectType = "project"
        user = "username"
        object_id = "object_project"
        service = VersionInfoService(app_context)
        # mock update_to_product_table
        update_to_project_table_patch = patch.object(ProjectDao, 'update_to_project_table',
                                                     side_effect=self.mock_update_to_project_table)
        update_to_project_table_patch.start()

        result, cost_time = service.archive_db_data(user, object_id, objectType)
        assert result == "update12345"
        update_to_project_table_patch.stop()

    def test_search_from_db_product_success(self):
        """
        1.測試 VersionInfoService 的 search_from_db function - product
        2.search_from_db, 正常回傳

        """
        objectType = "product"
        page = 1
        page_size = 10
        request = request_product_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="search")
        version_vo.validate(objectType, api_type="search")
        service = VersionInfoService(app_context)
        result, cost_time, page_object = service.search_from_db(objectType, version_vo, page, page_size)

    def test_search_from_db_project_success(self):
        """
        1.測試 VersionInfoService 的 search_from_db function - project
        2.search_from_db, 正常回傳

        """
        objectType = "project"
        page = 1
        page_size = 10
        request = request_project_data(full=True)
        version_vo = VersionInfoVo()
        version_vo.value_of_import(request, objectType, api_type="search")
        version_vo.validate(objectType, api_type="search")
        service = VersionInfoService(app_context)
        result, cost_time, page_object = service.search_from_db(objectType, version_vo, page, page_size)

    def mock_check_insert_validation(self, *args, **kwargs):
        return True

    def mock_insert_to_product_table(self, *args, **kwargs):
        return "12345"

    def mock_insert_to_project_table(self, *args, **kwargs):
        return "12345"

    def mock_insert_to_release_table(self, *args, **kwargs):
        return "23456"

    def mock_update_to_product_table(self, *args, **kwargs):
        return "update12345"

    def mock_update_to_project_table(self, *args, **kwargs):
        return "update12345"

    def mock_check_exist(self, *args, **kwargs):
        return False

    def mock_select_by_id_product(self, *args, **kwargs):
        if "fail" in args:
            raise
        return {"product_name": "prodcut12345"}

    def mock_select_by_id_project(self, *args, **kwargs):
        if "fail" in args:
            raise
        return {"project_name": "project12345"}


if __name__ == '__main__':
    unittest.main()