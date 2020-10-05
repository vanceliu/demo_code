# -*- coding: utf-8 -*-
import logging
import traceback
import peewee
from config.constants import Type
from bson.objectid import ObjectId
from db.mysql.models import Product_Base_Table, Project_Base_Table, \
    Release_Table, Release_Mapping_Table, Product_Mapping_Table, Search_View
from db.mysql.mysql_base import MySqlRepository
from eyesmediapyutils import page

logger = logging.getLogger("mysql")


class ProductDao(MySqlRepository):
    def __init__(self, mysql_client):
        super().__init__(mysql_client)

    def _get_table(self):
        return Product_Base_Table

    def check_insert_validation(self, name):
        result = self.table.select().where(self.table.product_name == name).exists()
        return result

    def insert_to_product_table(self, product_name=None, note=None, jira_api=None):
        product_id = str(ObjectId())
        table_instance = self.table.create(product_id=product_id, product_name=product_name, note=note)
        return product_id

    def check_exist(self, product_id, active_status):
        boolean = self.table.select().where(self.table.product_id == product_id, self.table.active_status == active_status).exists()
        return boolean

    def update_to_product_table(self, product_id, note=None, jira_api=None, active_status=None):
        update_dict_data = {}
        if note:
            update_dict_data["note"] = note
        if jira_api:
            update_dict_data["jiraApi"] = jira_api
        if active_status == 0:
            update_dict_data["active_status"] = active_status
        query = self.table.update(update_dict_data).where(self.table.product_id == product_id)
        result = query.execute()  # 回傳更新了幾筆, 回傳為0有可能是沒有找到資料或是更新的資料與原本的資料一致
        return result

    def select_by_id(self, product_id):
        result = self.table.select().where(self.table.product_id == product_id).dicts().get()
        return result

    def search_by_parameters(self, result=True, product_name=None, active_status=None, note=None, keyword=None):
        """
        search table by given arguments(using 'and' operator).

        Parameters
        ----------
        result: boolen
            若為True => 回傳cursor
            若為False => 回傳是否存在
        product_name: str
        active_status: int
        note: str
        keyword: str
        """
        cursor = self.table.select()
        if keyword is not None:
            cursor = cursor.where(self.table.product_name.contains(keyword) | self.table.note.contains(keyword))
        if product_name is not None:
            cursor = cursor.where(self.table.product_name.contains(product_name))
        if active_status is not None:
            cursor = cursor.where(self.table.active_status == active_status)
        if note is not None:
            cursor = cursor.where(self.table.note.contains(note))

        if result:
            return cursor
        else:
            return cursor.exists()


class ProjectDao(MySqlRepository):
    def __init__(self, mysql_client):
        super().__init__(mysql_client)

    def _get_table(self):
        return Project_Base_Table

    def check_insert_validation(self, name, url=None, port=None):
        cursor = self.table.select().where(self.table.project_name == name)
        if url is not None:
            cursor = cursor.where(self.table.service_url == url)
        if port is not None:
            cursor = cursor.where(self.table.service_port == port)
        result = cursor.exists()
        return result

    def insert_to_project_table(self, project_name=None, service_port=None, git_url=None, service_url=None,
                                language_type=None, project_type=None, jira_api=None, note=None):
        project_id = str(ObjectId())
        table_instance = self.table.create(project_id=project_id, project_name=project_name,
                                           service_port=service_port, git_url=git_url, service_url=service_url,
                                           language_type=language_type, project_type=project_type,
                                           jira_api=jira_api, note=note)
        return project_id

    def update_to_project_table(self, project_id, active_status=None, service_port=None, git_url=None, service_url=None,
                                language_type=None, project_type=None, jira_api=None, note=None):
        """
        update table by given arguments(using 'and' operator).

        Parameters
        ----------
        project_id: str
        active_status: int
        service_port: int
        git_url: str
        service_url: str
        language_type: str
        project_type: str
        jira_api: str
        note: str

        Returns
        -------
        str object_id
        """
        update_dict_data = {}
        if service_port:
            update_dict_data["service_port"] = service_port
        if git_url:
            update_dict_data["git_url"] = git_url
        if service_url:
            update_dict_data["service_url"] = service_url
        if language_type:
            update_dict_data["language_type"] = language_type
        if project_type:
            update_dict_data["project_type"] = project_type
        if active_status is not None:
            update_dict_data["active_status"] = active_status
        if jira_api:
            update_dict_data["jira_api"] = jira_api
        if note:
            update_dict_data["note"] = note

        query = self.table.update(update_dict_data).where(self.table.project_id == project_id)
        result = query.execute()  # 回傳更新了幾筆, 回傳為0有可能是沒有找到資料或是更新的資料與原本的資料一致
        return result

    def select_by_id(self, project_id):
        result = self.table.select().where(self.table.project_id == project_id).dicts().get()
        return result

    def check_exist(self, object_id, service_port=None, service_url=None):
        cursor = self.table.select()
        if service_port:
            cursor = cursor.orwhere(self.table.service_port == service_port)
        if service_url:
            cursor = cursor.orwhere(self.table.service_url == service_url)
        cursor = cursor.where(self.table.project_id != object_id)
        data_exist = cursor.dicts().exists()
        return data_exist

    def search_by_parameters(self, result=True, project_name=None, service_port=None, git_url=None,
                             service_url=None, language_type=None, project_type=None, active_status=None,
                             jira_api=None, note=None, keyword=None):
        """
        search table by given arguments(using 'and' operator).

        Parameters
        ----------
        result: boolen
            若為True => 回傳cursor
            若為False => 回傳是否存在
        project_name: str
        service_port: str
        git_url: str
        service_url: str
        language_type: str
        project_type: str
        active_status: int
        jira_api: str
        note: str
        keyword: str
        """

        cursor = self.table.select()
        if keyword is not None:
            cursor = cursor.where(self.table.project_name.contains(keyword) | self.table.git_url.contains(keyword) |
                                  self.table.service_url.contains(keyword) | self.table.language_type.contains(keyword) |
                                  self.table.project_type.contains(keyword) | self.table.jira_api.contains(keyword) |
                                  self.table.note.contains(keyword))
        if project_name is not None:
            cursor = cursor.where(self.table.project_name.contains(project_name))
        if service_port is not None:
            cursor = cursor.where(self.table.service_port == service_port)
        if git_url is not None:
            cursor = cursor.where(self.table.git_url.contains(git_url))
        if service_url is not None:
            cursor = cursor.where(self.table.service_url.contains(service_url))
        if language_type is not None:
            cursor = cursor.where(self.table.language_type.contains(language_type))
        if project_type is not None:
            cursor = cursor.where(self.table.project_type.contains(project_type))
        if active_status is not None:
            cursor = cursor.where(self.table.active_status == active_status)
        if jira_api is not None:
            cursor = cursor.where(self.table.jira_api.contains(jira_api))
        if note is not None:
            cursor = cursor.where(self.table.note.contains(note))

        if result:
            return cursor
        else:
            return cursor.exists()

    def get_active_and_version(self, project_id, active_status, version):
        cursor = self.table.select(self.table.active_status, Release_Table.version)\
                .join(Release_Table, on=(self.table.project_id == Release_Table.project_id))\
                .orwhere( (self.table.project_id == project_id) & (self.table.active_status == active_status) )\
                .orwhere( (self.table.project_id == project_id) & (Release_Table.version == version) )
        return cursor


class ReleaseDao(MySqlRepository):
    def __init__(self, mysql_client):
        super().__init__(mysql_client)

    def _get_table(self):
        return Release_Table

    def insert_to_release_table(self, product_id=None, project_id=None, version=None, crt_user=None,
                                mdy_user=None, release_note=None):
        release_id = str(ObjectId())
        table_instance = self.table.create(release_id=release_id, product_id=product_id, project_id=project_id,
                                           version=version, crt_user=crt_user, mdy_user=mdy_user,
                                           release_note=release_note)
        return release_id

    def get_data_by_object_id(self, get_running_status, product_id=None, project_id=None):
        # 選取需要的 fields
        if project_id is not None:
            cursor = self.table.select(self.table.project_id, self.table.version, self.table.crt_date, self.table.release_note,
                                        self.table.release_id, Search_View.project_name.alias("dependency_project_name"),
                                        Search_View.dependency_id, Search_View.dependency_version)
        if product_id is not None:
            cursor = self.table.select(self.table.product_id, self.table.version, self.table.crt_date, self.table.release_note,
                                        self.table.release_id, Search_View.project_name.alias("dependency_project_name"),
                                        Search_View.dependency_id, Search_View.dependency_version)

        # join Search_View
        cursor = cursor.join(Search_View, peewee.JOIN.LEFT_OUTER, on=(self.table.release_id == Search_View.release_id))

        # filter
        if project_id is not None:
            cursor = cursor.where(self.table.project_id == project_id)
        if product_id is not None:
            cursor = cursor.where(self.table.product_id == product_id)

        if get_running_status is True:
            cursor = cursor.where(self.table.running_status == 1)

        # order by crt_date
        cursor = cursor.order_by(self.table.version.desc())
        return cursor

    def update_by_parameters(self, release_id, project_id=None, version=None, running_status=None, release_status=None,
                             mdy_date=None, mdy_user=None, release_note=None):
        """
        update table by given arguments.

        Parameters
        ----------
        release_id: str
        project_id: str
        version: str
        running_status: int
        release_status: int
        mdy_date: datetime
        mdy_user: str
        release_note: str
        """
        update_dict_data = {}
        update_dict_data["mdy_date"] = mdy_date
        update_dict_data["mdy_user"] = mdy_user
        if project_id is not None:
            update_dict_data["project_id"] = project_id
        if version is not None:
            update_dict_data["version"] = version
        if running_status is not None:
            update_dict_data["running_status"] = running_status
        if release_status is not None:
            update_dict_data["release_status"] = release_status
        if release_note is not None:
            update_dict_data["release_note"] = release_note

        # for release_id update
        if isinstance(release_id, str):
            query = self.table.update(update_dict_data).where(self.table.release_id == release_id)

        # for dependency_id update
        if isinstance(release_id, list):
            query = self.table.update(update_dict_data).where(self.table.release_id.in_(release_id))

        result = query.execute()  # 回傳更新了幾筆, 回傳為0有可能是沒有找到資料或是更新的資料與原本的資料一致
        return release_id if result >= 1 else None

    def project_release_overview(self):
        """
        拿取所有 object 的dependency_version

        Returns
        -------
        cursor: dict
            查詢之結果
        """
        project_cursor = self.table.select(self.table.release_id, self.table.version, self.table.project_id, Project_Base_Table.project_name) \
            .join(Project_Base_Table, on=(self.table.project_id == Project_Base_Table.project_id))\
            .where(Project_Base_Table.active_status != 0) \
            .order_by(Project_Base_Table.project_name)


        return project_cursor

    def product_release_overview(self):
        product_cursor = self.table.select(self.table.release_id, self.table.version, self.table.product_id, Product_Base_Table.product_name) \
            .join(Product_Base_Table, on=(self.table.product_id == Product_Base_Table.product_id))\
            .where(Product_Base_Table.active_status != 0) \
            .order_by(Product_Base_Table.product_name)
        return product_cursor

    def search_by_id_list(self, id_list):
        """
        用傳入的 id list 查找 table 中的詳細資料
        Parameters
        ----------
        id_list: list

        Returns
        -------
        result_in_db: peewee.object
            查詢之結果
        """
        result_in_db = self.table.select(self.table, Project_Base_Table.project_id, Project_Base_Table.project_name, Project_Base_Table.language_type,
                                         Product_Base_Table.product_id, Product_Base_Table.product_name,
                                         Search_View.dependency_id, Search_View.dependency_version, Search_View.project_name.alias("dependency_name")) \
            .join(Project_Base_Table, peewee.JOIN.LEFT_OUTER,
                  on=(Project_Base_Table.project_id == self.table.project_id)) \
            .join(Product_Base_Table, peewee.JOIN.LEFT_OUTER,
                  on=(Product_Base_Table.product_id == self.table.product_id)) \
            .join(Search_View, peewee.JOIN.LEFT_OUTER,
                  on=(Search_View.release_id == self.table.release_id)) \
            .where(self.table.release_id.in_(id_list)) \
            .order_by(self.table.release_id.desc()).dicts()
        return result_in_db

    def get_release_info(self, object_type, product_id=None, project_id=None):
        """
        透過指定project_id 找 table 的資料

        Parameters
        ----------
        object_type: str
            product or project
        product_id: str
        project_id: str

        Returns
        -------
        cursor: dict
            查詢之結果
        """
        if object_type == Type.product.value:
            cursor = self.table.select().where(self.table.product_id == product_id).order_by(self.table.version.desc())

        if object_type == Type.project.value:
            cursor = self.table.select().where(self.table.project_id == project_id).order_by(self.table.version.desc())

        return cursor
    
    def get_release_status_by_id(self, release_id):
        """
        用 release_id 拿取 release_status、running_status

        return
        ---------
        release_status: int
        """
        result = self.table.select(self.table.release_status, self.table.running_status).where(self.table.release_id == release_id).dicts().get()

        return result.get("release_status")

    def get_status_and_dependency_by_id(self, release_id):
        """
        用 release_id 拿取 release_status、running_status、dependency_list

        return
        ---------
        release_status: int
        running_status: int
        dependency_list: list
        """
        cursor = self.table.select(self.table.release_status, self.table.running_status, Release_Mapping_Table.dependency_id)\
                .join(Release_Mapping_Table, peewee.JOIN.LEFT_OUTER, on=(self.table.release_id == Release_Mapping_Table.release_id))\
                .where(self.table.release_id == release_id).dicts()
        
        dependency_list = list()        
        for values in cursor:
            release_status = values["release_status"]
            running_status = values["running_status"]
            if values["dependency_id"]: # 不 append None
                dependency_list.append(values["dependency_id"])
        
        return release_status, running_status, dependency_list


class ReleaseMappingDao(MySqlRepository):
    def __init__(self, mysql_client):
        super().__init__(mysql_client)

    def _get_table(self):
        return Release_Mapping_Table

    # 進版時使用的API
    def insert_to_release_mapping_table(self, release_id=None, dependency_id_list=None):
        """
        將資料insert到release_mapping_table中，
        若dependency_id_list為None則insert一筆dependency_id = null的資料

        Parameters
        ----------
        release_id : str
        dependency_id_list : list
        """
        mapping_list = []

        if dependency_id_list is None:
            return 0

        for dependency_id in dependency_id_list:
            mapping_list.append({"release_id": release_id, "dependency_id": dependency_id})
        insert_data_num = self.table.insert_many(mapping_list).execute()

        return insert_data_num

    def check_parent_dependency(self, release_id):
        """
        用來檢查是否有別的專案在使用此 version

        Parameters
        ----------
        release_id : str

        return
        ----------
        boolean
        """
        cursor = self.table.select(self.table.dependency_id, Release_Table.running_status) \
            .join(Release_Table, peewee.JOIN.LEFT_OUTER, on=(Release_Table.release_id == self.table.release_id)) \
            .where(self.table.dependency_id == release_id).dicts()

        if {"dependency_id": release_id, "running_status": 1} in list(cursor):
            return True
        else:
            return False

    def modify_dependency_by_release_id(self, release_id, dependency_id_list=None):
        """
        將資料 update 到release_mapping_table中

        Parameters
        ----------
        release_id : str
        dependency_id_list : list

        return
        ----------
        insert_data_num: int
            新增的筆數
        """
        mapping_list = []
        self.table.delete().where(self.table.release_id == release_id).execute()

        if dependency_id_list is None or len(dependency_id_list) == 0:
            return 0

        for dependency_id in dependency_id_list:
            mapping_list.append({"release_id": release_id, "dependency_id": dependency_id})
        insert_data_num = self.table.insert_many(mapping_list).execute()

        return insert_data_num


class SearchViewDao(MySqlRepository):
    def __init__(self, mysql_client):
        super().__init__(mysql_client)

    def _get_table(self):
        return Search_View

    def get_release_info(self, object_type, product_id=None, project_id=None):
        """
        透過指定project_id 找view的search_view指定欄位

        Parameters
        ----------
        object_type: str
            product or project
        product_id: str
        project_id: str

        Returns
        -------
        cursor: dict
            查詢之結果
        """
        if object_type == Type.product.value:
            cursor = self.table.select(self.table, Release_Table.version.alias("release_version"))\
                .join(Release_Table, on=(self.table.release_id == Release_Table.release_id))\
                .where(self.table.product_id == product_id).order_by(Release_Table.version.desc())

        if object_type == Type.project.value:
            cursor = self.table.select(self.table, Release_Table.version.alias("release_version"))\
                .join(Release_Table, on=(self.table.release_id == Release_Table.release_id))\
                .where(self.table.project_id == project_id).order_by(Release_Table.version.desc())

        return cursor
    

    def get_dependency_id(self, release_id):
        """
        拿取指定release_id 的dependency_id
        Returns
        -------
        cursor: dict
            查詢之結果
        """
        cursor = self.table.select(self.table.dependency_id).where(self.table.release_id == release_id)

        return cursor
