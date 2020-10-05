try:
    from config.application import app_context
    from db.mysql_dao import ReleaseDao, ReleaseMappingDao, SearchViewDao
    from service.release_service import ReleaseVo, ReleaseService
    from eyesmediapyutils.exceptions import CommonRuntimeException
    import peewee
except:
    import os
    import sys
    import peewee
    from peewee import MySQLDatabase

    sys.path.append(os.path.dirname(os.getcwd()))
    from config.application import app_context
    from db.mysql_dao import ReleaseDao, ReleaseMappingDao, SearchViewDao
    from service.release_service import ReleaseVo, ReleaseService
    from eyesmediapyutils.exceptions import CommonRuntimeException
import unittest
from unittest.mock import patch


def request_activate_data(running_status, fail=None):
    data = {
        "user": "activate測試者",
        "releaseId": "test_release_id",
        "runningStatus": running_status
    }
    if fail == "release_id":
        data.pop("releaseId")
    return data


def request_latest_info_data(fail=None):
    data = {
        "user": "latest_info測試者",
        "objectId": "test_object_id"
    }
    if fail == "wrong type":
        data["objectId"] = int(10)
    if fail == "missing data":
        data.pop("user")
    return data


def request_verify_data(fail=None):
    data = {
        "user": "latest_info測試者",
        "releaseId": "test_release_id",
        "releaseStatus": 1
    }
    if fail == "wrong type":
        data["releaseStatus"] = str(1)
    if fail == "missing data":
        data.pop("user")
    return data


def request_modify_data(fail=None):
    data = {
        "user": "eyesmedia",
        "releaseId": "test_release_id",
        "dependencyId": ["5f27f46540b04a3ba81e5db6", "5f27f46540b04a3ba81e5db5", "5f27f46540b04a3ba81e5db4"],
        "releaseNote": ""
    }
    if fail == "wrong type":
        data["releaseId"] = int(123)
    if fail == "missing data":
        data.pop("user")
    return data


class VoTestCase(unittest.TestCase):
    def test_ReleaseVo(self):
        self.assertRaisesRegex(CommonRuntimeException, "999900001", self.ReleaseVo_activate_fail)
        self.assertRaisesRegex(AssertionError, "999900001", self.ReleaseVo_latest_info_wrong_type_fail)
        self.assertRaisesRegex(CommonRuntimeException, "999900001", self.ReleaseVo_latest_info_missing_data_fail)
        self.assertRaisesRegex(AssertionError, "999900001", self.ReleaseVo_verify_wrong_type_fail)
        self.assertRaisesRegex(CommonRuntimeException, "999900001", self.ReleaseVo_verify_missing_data_fail)
        self.assertRaisesRegex(AssertionError, "999900001", self.ReleaseVo_modify_wrong_type_fail)
        self.assertRaisesRegex(CommonRuntimeException, "999900001", self.ReleaseVo_modify_missing_data_fail)

    def ReleaseVo_modify_wrong_type_fail(self):
        """
        1.測試releaseVo api_type = modify_dependency
        2.預期request_modify_data 因 releaseId 的資料型態錯誤 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_modify_data(fail="wrong type")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="modify_release_info")
        release_vo.validate(api_type="modify_release_info")

    def ReleaseVo_modify_missing_data_fail(self):
        """
        1.測試releaseVo api_type = modify_dependency
        2.預期request_modify_data 因丟失 user 的資料 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_modify_data(fail="missing data")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="modify_release_info")
        release_vo.validate(api_type="modify_release_info")

    def ReleaseVo_verify_wrong_type_fail(self):
        """
        1.測試releaseVo api_type = verify
        2.預期request_activate_data 因 object_id 的資料型態錯誤 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_verify_data(fail="wrong type")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="verify")
        release_vo.validate(api_type="verify")

    def ReleaseVo_verify_missing_data_fail(self):
        """
        1.測試releaseVo api_type = verify
        2.預期request_activate_data 因 object_id 的資料型態錯誤 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_verify_data(fail="missing data")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="verify")
        release_vo.validate(api_type="verify")

    def test_ReleaseVo_latest_info_success(self):
        """
        1.測試ReleaseVo api_type = latest_info
        2.判斷request_latest_info_data與releasevo要一致

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_latest_info_data()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="latest_info")
        release_vo.validate(api_type="latest_info")
        assert release_vo.user == request.get("user")
        assert release_vo.object_id == request.get("objectId")

    def ReleaseVo_latest_info_wrong_type_fail(self):
        """
        1.測試releaseVo api_type = latest_info
        2.預期request_activate_data 因 object_id 的資料型態錯誤 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_latest_info_data(fail="wrong type")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="latest_info")
        release_vo.validate(api_type="latest_info")

    def ReleaseVo_latest_info_missing_data_fail(self):
        """
        1.測試releaseVo api_type = latest_info
        2.預期request_activate_data 因缺少 user 欄位 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_latest_info_data(fail="missing data")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="latest_info")
        release_vo.validate(api_type="latest_info")

    def ReleaseVo_activate_fail(self):
        """
        1.測試releaseVo api_type = activate
        2.預期request_activate_data 因少releaseId欄位 判斷失敗

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_activate_data(running_status=1, fail="release_id")
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="activate")
        release_vo.validate(api_type="activate")

    def test_ReleaseVo_activate_success(self):
        """
        1.測試ReleaseVo api_type = activate
        2.判斷request_activate_data與releasevo要一致

        Parameters
        ----------
        version_vo : object
            包含所有 input 資訊
        """
        request = request_activate_data(running_status=1)
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="activate")
        release_vo.validate(api_type="activate")
        assert release_vo.user == request.get("user")
        assert release_vo.release_id == request.get("releaseId")
        assert release_vo.running_status == request.get("runningStatus")


class ReleaseTestCase(unittest.TestCase):
    def test_deactivate_fail(self):
        """
        1.測試對有 parent 正在使用的 release_id 進行 deactivate
        2.回傳錯誤 389900011
        3.測試對不存在的 release_id 進行 deactivate
        4.回傳錯誤 389900002
        """
        check_parent_dependency_patch = patch.object(ReleaseMappingDao, 'check_parent_dependency',
                                                     side_effect=self.mock_check_parent_dependency_exist)
        check_parent_dependency_patch.start()
        self.assertRaisesRegex(CommonRuntimeException, "389900011", self.deactive_inuse_object)
        check_parent_dependency_patch.stop()

        check_parent_dependency_patch = patch.object(ReleaseMappingDao, 'check_parent_dependency',
                                                     side_effect=self.mock_check_parent_dependency_not_exist)
        check_parent_dependency_patch.start()
        update_by_parameters_patch = patch.object(ReleaseDao, 'update_by_parameters',
                                                  side_effect=self.mock_update_by_parameters_None)
        update_by_parameters_patch.start()
        self.assertRaisesRegex(CommonRuntimeException, "389900002", self.deactive_not_exist_object)
        update_by_parameters_patch.stop()
        check_parent_dependency_patch.stop()

    def deactive_inuse_object(self):
        """
        1.測試對有 parent 正在使用的 release_id 進行 deactivate
        2.回傳錯誤 389900011
        """
        request = request_activate_data(running_status=0)
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="activate")
        release_vo.validate(api_type="activate")

        service = ReleaseService(app_context)
        result, cost_time = service.activate(release_vo)

    def deactive_not_exist_object(self):
        """
        1.測試對不存在的 release_id 進行 deactivate
        2.回傳錯誤 389900002
        """
        request = request_activate_data(running_status=0)
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="activate")
        release_vo.validate(api_type="activate")

        service = ReleaseService(app_context)
        result, cost_time = service.activate(release_vo)

    def test_deactivate_success(self):
        """
        1.測試 deactivate
        2.update_by_parameters 正常回傳

        """
        request = request_activate_data(running_status=0)
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="activate")
        release_vo.validate(api_type="activate")

        check_parent_dependency_patch = patch.object(ReleaseMappingDao, 'check_parent_dependency',
                                                     side_effect=self.mock_check_parent_dependency_not_exist)
        check_parent_dependency_patch.start()
        update_by_parameters_patch = patch.object(ReleaseDao, 'update_by_parameters',
                                                  side_effect=self.mock_update_by_parameters_success)
        update_by_parameters_patch.start()

        service = ReleaseService(app_context)
        result, cost_time = service.activate(release_vo)
        assert result == "test_release_id"
        check_parent_dependency_patch.stop()
        update_by_parameters_patch.stop()

    def test_activate_fail(self):
        """
        1.測試對不存在的 release_id 進行 activate
        2.回傳錯誤 389900009
        """
        get_dependency_id_patch = patch.object(SearchViewDao, 'get_dependency_id',
                                               side_effect=self.mock_get_dependency_id_not_exist)
        get_dependency_id_patch.start()
        check_parent_dependency_patch = patch.object(ReleaseMappingDao, 'check_parent_dependency',
                                               side_effect=self.mock_check_parent_dependency_exist)
        check_parent_dependency_patch.start()
        get_release_status_by_id_patch = patch.object(ReleaseDao, 'get_release_status_by_id',
                                               side_effect=self.mock_get_release_status_by_id)
        get_release_status_by_id_patch.start()

        self.assertRaisesRegex(CommonRuntimeException, "389900009", self.activate_fail)

        get_dependency_id_patch.stop()
        check_parent_dependency_patch.stop()
        get_release_status_by_id_patch.stop()

    def activate_fail(self):
        """
        1.測試對不存在的 release_id 進行 activate
        2.回傳錯誤 389900009
        """
        request = request_activate_data(running_status=1)
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="activate")
        release_vo.validate(api_type="activate")

        service = ReleaseService(app_context)
        result, cost_time = service.activate(release_vo)

    def test_activate_success(self):
        """
        1.測試 activate
        2.update_by_parameters 正常回傳
        """
        request = request_activate_data(running_status=1)
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="activate")
        release_vo.validate(api_type="activate")

        get_dependency_id_patch = patch.object(SearchViewDao, 'get_dependency_id',
                                               side_effect=self.mock_get_dependency_id_dicts)
        get_dependency_id_patch.start()
        check_parent_dependency_patch = patch.object(ReleaseMappingDao, 'check_parent_dependency',
                                               side_effect=self.mock_check_parent_dependency_not_exist)
        check_parent_dependency_patch.start()
        get_release_status_by_id_patch = patch.object(ReleaseDao, 'get_release_status_by_id',
                                               side_effect=self.mock_get_release_status_by_id)
        get_release_status_by_id_patch.start()
        update_by_parameters_patch = patch.object(ReleaseDao, 'update_by_parameters',
                                                  side_effect=self.mock_update_by_parameters_success)
        update_by_parameters_patch.start()

        service = ReleaseService(app_context)
        result, cost_time = service.activate(release_vo)

        assert result == "test_release_id"
        get_dependency_id_patch.stop()
        update_by_parameters_patch.stop()

    def test_latest_info_fail(self):
        """
        1.測試拿取不存在的 release_id 的上一版的 dependency 紀錄
        2.回傳錯誤 389900009
        """
        request = request_latest_info_data()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="latest_info")
        release_vo.validate(api_type="latest_info")

        get_release_info_patch = patch.object(SearchViewDao, 'get_release_info',
                                              side_effect=self.mock_get_release_info_not_exist)
        get_release_info_patch.start()
        service = ReleaseService(app_context)
        result, cost_time = service.latest_release_info("project", release_vo)
        assert result == None
        get_release_info_patch.stop()

    def test_latest_info_project_success(self):
        """
        1.測試拿取上一版的 dependency
        2.正常回傳
        """
        request = request_latest_info_data()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="latest_info")
        release_vo.validate(api_type="latest_info")

        get_release_info_view_patch = patch.object(SearchViewDao, 'get_release_info',
                                                   side_effect=self.mock_get_release_info_success)
        get_release_info_view_patch.start()
        get_release_info_table_patch = patch.object(ReleaseDao, 'get_release_info',
                                                    side_effect=self.mock_get_release_info_success)
        get_release_info_table_patch.start()

        service = ReleaseService(app_context)
        result, cost_time = service.latest_release_info("project", release_vo)
        assert result == None
        get_release_info_view_patch.stop()
        get_release_info_table_patch.stop()

    def test_latest_info_product_success(self):
        """
        1.測試拿取上一版的 dependency
        2.正常回傳
        """
        request = request_latest_info_data()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="latest_info")
        release_vo.validate(api_type="latest_info")

        get_release_info_view_patch = patch.object(SearchViewDao, 'get_release_info',
                                                   side_effect=self.mock_get_release_info_success)
        get_release_info_view_patch.start()
        get_release_info_table_patch = patch.object(ReleaseDao, 'get_release_info',
                                                    side_effect=self.mock_get_release_info_success)
        get_release_info_table_patch.start()

        service = ReleaseService(app_context)
        result, cost_time = service.latest_release_info("product", release_vo)
        assert result == None
        get_release_info_view_patch.stop()
        get_release_info_table_patch.stop()

    def test_verify_fail(self):
        """
        1.測試對不存在的 release_id verify
        2.回傳錯誤 389900002
        """
        update_by_parameters_patch = patch.object(ReleaseDao, 'update_by_parameters',
                                                  side_effect=self.mock_update_by_parameters_None)
        update_by_parameters_patch.start()

        self.assertRaisesRegex(CommonRuntimeException, "389900002", self.verify_fail)

        update_by_parameters_patch.stop()

    def verify_fail(self):
        """
        1.測試對不存在的 release_id verify
        2.回傳錯誤 389900002
        """
        request = request_verify_data()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="verify")
        release_vo.validate(api_type="verify")

        service = ReleaseService(app_context)
        result, cost_time = service.verify(release_vo)

    def test_verify_success(self):
        """
        1.測試 verify
        2.正常回傳
        """

        request = request_verify_data()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="verify")
        release_vo.validate(api_type="verify")

        update_by_parameters_patch = patch.object(ReleaseDao, 'update_by_parameters',
                                                  side_effect=self.mock_update_by_parameters_success)
        update_by_parameters_patch.start()

        service = ReleaseService(app_context)
        result, cost_time = service.verify(release_vo)
        assert result == "test_release_id"
        update_by_parameters_patch.stop()

    def test_modify_success(self):
        """
        1.測試 modify
        2.正常回傳
        """
        request = request_modify_data()
        release_vo = ReleaseVo()
        release_vo.value_of_import(request, api_type="modify_release_info")
        release_vo.validate(api_type="modify_release_info")

        modify_dependency_by_release_id_patch = patch.object(ReleaseMappingDao, 'modify_dependency_by_release_id',
                                                             side_effect=self.mock_modify_dependency_by_release_id_success)
        modify_dependency_by_release_id_patch.start()
        get_status_and_dependency_by_id_patch = patch.object(ReleaseDao, 'get_status_and_dependency_by_id',
                                                             side_effect=self.mock_get_status_and_dependency_by_id)
        get_status_and_dependency_by_id_patch.start()
        update_by_parameters_patch = patch.object(ReleaseDao, 'update_by_parameters',
                                                             side_effect=self.mock_update_by_parameters_None)
        update_by_parameters_patch.start()

        service = ReleaseService(app_context)
        result, cost_time = service.modify_release(release_vo)
        assert result == "test_release_id"
        modify_dependency_by_release_id_patch.stop()
        get_status_and_dependency_by_id_patch.stop()
        update_by_parameters_patch.stop()

    def mock_get_status_and_dependency_by_id(self, *args, **kwargs):
        return 0, 0, ["5f27f46540b04a3ba81e5db6", "5f27f46540b04a3ba81e5db5", "5f27f46540b04a3ba81e5db4"]

    def mock_get_release_info_success(self, *args, **kwargs):
        class Fake_Table_Data:
            def __init__(self):
                self.release_version = "not same"

        class Fake_Data:
            def __init__(self):
                self.crt_date = "now"
                self.version = "not the same"
                self.release_table = Fake_Table_Data()

        class Mock_Method:
            def limit(self, limit):
                return Mock_Method()

            def get(self):
                return Fake_Data()

            def dicts(self):
                return [{"crt_date": "not now"}]

        return Mock_Method()

    def mock_get_release_info_not_exist(self, *args, **kwargs):
        class Mock_Method:
            def limit(self, limit):
                return Mock_Method()

            def get(self):
                raise

        return Mock_Method()

    def mock_get_dependency_id_dicts(self, *args, **kwargs):
        class Mock_Check_Method:
            def dicts(self):
                return [{"dependency_id": "123"}]

            def count(self):
                return 1

        return Mock_Check_Method()

    def mock_get_release_status_by_id(self, *args, **kwargs):
        return 1

    def mock_get_dependency_id_not_exist(self, *args, **kwargs):
        raise

    def mock_check_parent_dependency_exist(self, *args, **kwargs):
        return True

    def mock_check_parent_dependency_not_exist(self, *args, **kwargs):
        return False

    def mock_check_parent_dependency_not_exist(self, *args, **kwargs):
        return False

    def mock_update_by_parameters_None(self, *args, **kwargs):
        return None

    def mock_update_by_parameters_success(self, *args, **kwargs):
        return "test_release_id"

    def mock_modify_dependency_by_release_id_success(self, *args, **kwargs):
        return 0


if __name__ == '__main__':
    unittest.main()
