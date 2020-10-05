try:
    from config.application import app_context
    from db.mysql_dao import ReleaseDao, ReleaseMappingDao, ProductMappingDao, SearchViewDao, ProjectDao, ProductDao
    from service.release_service import ReleaseVo, ReleaseService
    from eyesmediapyutils.exceptions import CommonRuntimeException
except:
    import os
    import sys
    import peewee
    from peewee import MySQLDatabase

    sys.path.append(os.path.dirname(os.getcwd()))
    from config.application import app_context
    from db.mysql_dao import ReleaseDao, ReleaseMappingDao, SearchViewDao, ProjectDao, ProductDao
    from service.release_service import ReleaseVo, ReleaseService
    from eyesmediapyutils.exceptions import CommonRuntimeException
import unittest
import datetime
from unittest.mock import patch


def request_data_for_new_release(fail=None, full=None):
    data = {
        "version": "1.0",
        "objectId": "5f3e4d7ecadda185989810ee",
        "user": "product測試者"
    }
    if fail == "version":
        data.pop("version")
    if full:
        data.update({
            "releaseNote": "testing release",
            "dependencyId": ["5f27f46540b04a3ba81e5db6", "5f27f46540b04a3ba81e5db5", "5f27f46540b04a3ba81e5db4"]
        })
    return data


def request_data_for_history_info(fail=None):
    data = {
        "user": "Eyesmedia",
        "objectId": "5f27f46540b04a3ba81e5db4",
        "getRunning": True
    }
    if fail == "get_running":
        data.pop("getRunning")
    return data


def request_data_for_get_spec_release_detail(fail=None):
    data = {
        "user": "Eyesmedia",
        "releaseId": ["5f729b5ab7634f3335dcc895"]
    }
    if fail == "releaseId":
        data.pop("releaseId")
    return data


class VoTestCase(unittest.TestCase):
    def test_ReleaseVo(self):
        self.assertRaisesRegex(CommonRuntimeException, "999900001", self.releaseVo_new_release_version_fail)
        self.assertRaisesRegex(CommonRuntimeException, "999900001",
                               self.releaseVo_history_release_dep_info_get_running_fail)
        self.assertRaisesRegex(CommonRuntimeException, "999900001", self.get_spec_release_detail_fail)

    def test_releaseVo_new_release_version(self):
        """
        測試releasevo api_type = release_insert
        """
        request = request_data_for_new_release()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="release_insert")
        release_vo.validate(api_type="release_insert")
        assert release_vo.user == request.get("user")
        assert release_vo.object_id == request.get("objectId")
        assert release_vo.version == request.get("version")

    def releaseVo_new_release_version_fail(self):
        """
        1.測試releasevo api_type = release_insert
        2.預期因少了version欄位 判斷失敗 "999900001"
        """
        request = request_data_for_new_release(fail="version", full=True)
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="release_insert")
        release_vo.validate(api_type="release_insert")

    def test_releaseVo_history_release_dependency_information(self):
        """
        測試releasevo api_type = history_info
        """
        request = request_data_for_history_info()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="history_info")
        release_vo.validate(api_type="history_info")
        assert release_vo.user == request.get("user")
        assert release_vo.object_id == request.get("objectId")
        assert release_vo.get_running == request.get("getRunning")

    def releaseVo_history_release_dep_info_get_running_fail(self):
        """
        1.測試releasevo api_type = history_info
        2.預期因少了get_running欄位 判斷失敗 "999900001"
        """
        request = request_data_for_history_info(fail="get_running")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="history_info")
        release_vo.validate(api_type="history_info")

    def test_dependency_overview(self):
        """
        測試releasevo api_type = dependency_overview
        """
        # 只有user, 一個必填欄位 直接寫死
        request_data_user = {"user": "eyesmedia"}
        release_vo = ReleaseVo()
        release_vo.value_of_import(request_data_user, api_type="dependency_overview")
        release_vo.validate(api_type="dependency_overview")

    def test_get_spec_release_detail_success(self):
        """
        測試releasevo api_type = get_release_info
        """
        request = request_data_for_get_spec_release_detail()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="get_release_info")
        release_vo.validate(api_type="get_release_info")

        assert release_vo.user == request.get("user")
        assert release_vo.release_id_list == request.get("releaseId")

    def get_spec_release_detail_fail(self):
        """
        1.測試releasevo api_type = history_info
        2.預期因少了releaseId 判斷失敗 "999900001"
        """
        request = request_data_for_get_spec_release_detail(fail="releaseId")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="get_release_info")
        release_vo.validate(api_type="get_release_info")


class ReleaseTestCase(unittest.TestCase):

    def test_new_project_release_version_success(self):
        """
        1.測試 new_release_version for project
        2.正常回傳
        """
        objectType = "project"
        request = request_data_for_new_release()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="release_insert")
        release_vo.validate(api_type="release_insert")
        service = ReleaseService(app_context)

        check_insert_to_release_table_patch = patch.object(ReleaseDao, "insert_to_release_table",
                                                           side_effect=self.mock_insert_to_release_table)
        check_insert_to_release_table_patch.start()
        check_insert_to_mapping_table_patch1 = patch.object(ReleaseMappingDao, "insert_to_release_mapping_table",
                                                            side_effect=self.mock_insert_to_release_mapping_table)
        check_insert_to_mapping_table_patch1.start()
        get_active_and_version_patch = patch.object(ProjectDao, "get_active_and_version",
                                                            side_effect=self.mock_get_active_and_version)
        get_active_and_version_patch.start()

        service.new_release_version(objectType, release_vo)
        check_insert_to_release_table_patch.stop()
        check_insert_to_mapping_table_patch1.stop()
        get_active_and_version_patch.stop()

    def test_new_product_release_version_success(self):
        """
        1.測試 new_release_version for product
        2.正常回傳
        """
        objectType = "product"
        request = request_data_for_new_release()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="release_insert")
        release_vo.validate(api_type="release_insert")
        service = ReleaseService(app_context)

        check_insert_to_release_table_patch = patch.object(ReleaseDao, "insert_to_release_table",
                                                           side_effect=self.mock_insert_to_release_table)
        check_insert_to_release_table_patch.start()
        check_insert_to_mapping_table_patch = patch.object(ReleaseMappingDao, "insert_to_release_mapping_table",
                                                           side_effect=self.mock_insert_to_release_mapping_table)
        check_insert_to_mapping_table_patch.start()
        product_check_exist_patch = patch.object(ProductDao, "check_exist",
                                                side_effect=self.mock_product_check_exist)
        product_check_exist_patch.start()

        service.new_release_version(objectType, release_vo)
        check_insert_to_release_table_patch.stop()
        check_insert_to_mapping_table_patch.stop()
        product_check_exist_patch.stop()

    def test_project_history_release_dep_info_success(self):
        """
        1.測試 拿取專案所依賴的服務或套件歷史紀錄
        2.正常回傳
        """
        objectType = "project"
        request = request_data_for_history_info()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="history_info")
        release_vo.validate(api_type="history_info")
        service = ReleaseService(app_context)

        check_history_release_dep_info_patch = patch.object(ReleaseDao, "get_data_by_object_id",
                                                            side_effect=self.mock_history_release_info_success)
        check_history_release_dep_info_patch.start()
        result, cost_time = service.get_release_history_info(objectType, release_vo)
        check_history_release_dep_info_patch.stop()

    def test_product_history_release_dep_info_fail(self):
        """
        1.測試 訪問資料庫拿不到資料時之情境
        2.回傳錯誤代碼389900009
        """
        check_history_release_dep_info_patch = patch.object(ReleaseDao, "get_data_by_object_id",
                                                            side_effect=self.mock_history_release_info_fail)
        check_history_release_dep_info_patch.start()

        assert self.product_history_release_dep_info_fail() == None

        check_history_release_dep_info_patch.stop()

    def product_history_release_dep_info_fail(self):
        objectType = "product"
        request = request_data_for_history_info()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="history_info")
        release_vo.validate(api_type="history_info")
        service = ReleaseService(app_context)
        service.get_release_history_info(objectType, release_vo)

    def test_dependency_overview(self):
        """
        1.測試 拿取所有依賴套件的資料
        2.正常回傳
        """
        request_data_user = {"user": "eyesmedia"}
        release_vo = ReleaseVo()
        release_vo.value_of_import(request_data_user, api_type="dependency_overview")
        release_vo.validate(api_type="dependency_overview")
        service = ReleaseService(app_context)
        result, cost_time = service.get_release_overview()

    def test_get_specific_releases_info(self):
        """
        1.測試 拿取指定release_id的release詳細資料
        2.正常回傳
        """
        request = request_data_for_get_spec_release_detail()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="get_release_info")
        release_vo.validate(api_type="get_release_info")
        service = ReleaseService(app_context)

        check_search_by_id_list_patch = patch.object(ReleaseDao, "search_by_id_list",
                                                     side_effect=self.mock_search_by_id_list)
        check_search_by_id_list_patch.start()
        result, cost_time = service.get_specific_releases_info(release_vo)
        check_search_by_id_list_patch.stop()

    def mock_product_check_exist(self, *args, **kwargs):
        return True

    def mock_get_active_and_version(self, *args, **kwargs):
        class Fake_Dao:
            def dicts(self):
                return [{
                    "active_status": 1,
                    "version": "1.1"
                }]
        return Fake_Dao()

    def mock_insert_to_release_table(self, *args, **kwargs):
        return "release_id:123456"

    def mock_insert_to_release_mapping_table(self, *args, **kwargs):
        return None

    def mock_insert_to_product_mapping_table(self, *args, **kwargs):
        return None

    def mock_history_release_info_success(self, *args, **kwargs):
        """
        模擬history_release_info成功時的資料形式
        Parameters
        ----------
        Returns
        -------
        list
            模擬資料
        """
        class Mock_PeeweeModel:
            def dicts(self):
                return [{"project_name": "test11", "dependency_version": "0.9.0", "crt_date": datetime.datetime.now(),
                         "release_note": "123456", "release_version": "0.9.1", "release_id": "asd123456"}]
        return Mock_PeeweeModel()

    def mock_history_release_info_fail(self, *args, **kwargs):
        """
        模擬history_release_info失敗時的資料形式
        Parameters
        ----------
        Returns
        -------
        list
            模擬資料
        """
        class Mock_PeeweeModel:
            def dicts(self):
                return {}
        return Mock_PeeweeModel()

    def mock_search_by_id_list(self, *args, **kwargs):
        """
        模擬search_by_id_list的資料形式
        Parameters
        ----------
        Returns
        -------
        list
            模擬資料
        """
        value = [{
            "crt_date": datetime.datetime.now(),
            "crt_user": "eyesmedia",
            "mdy_date": datetime.datetime.now(),
            "mdy_user": None,
            "product_id": None,
            "product_name": None,
            "project_id": "5f61c7abcadda1db38c41d92",
            "project_name": "eyesmedia-hibernate-dao",
            "release_id": "5f3b2cddcadda143b726cc75",
            "release_note": None,
            "release_status": 0,
            "running_status": 0,
            "version": "0.9.0",
            "dependency_id": None,
            "language_type": ""
        }]
        return value


if __name__ == '__main__':
    unittest.main()
