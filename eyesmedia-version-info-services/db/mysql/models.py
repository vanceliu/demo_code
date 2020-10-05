# -*- coding: utf-8 -*-
import peewee


class Product_Base_Table(peewee.Model):
    product_id = peewee.PrimaryKeyField()
    product_name = peewee.CharField(50)
    active_status = peewee.IntegerField()
    note = peewee.CharField(250)


class Project_Base_Table(peewee.Model):
    project_id = peewee.PrimaryKeyField()
    project_name = peewee.CharField(50)
    service_port = peewee.IntegerField()
    git_url = peewee.CharField(250)
    service_url = peewee.CharField(100)
    language_type = peewee.CharField(20)
    project_type = peewee.CharField(20)
    active_status = peewee.IntegerField()
    jira_api = peewee.CharField(50)
    note = peewee.CharField(250)


class Release_Table(peewee.Model):
    release_id = peewee.PrimaryKeyField()
    product_id = peewee.CharField(50)
    project_id = peewee.CharField(50)
    version = peewee.CharField(20)
    running_status = peewee.IntegerField()
    release_status = peewee.IntegerField()
    crt_date = peewee.DateTimeField()
    mdy_date = peewee.DateTimeField()
    crt_user = peewee.CharField(50)
    mdy_user = peewee.CharField(50)
    release_note = peewee.CharField(250)


class Release_Mapping_Table(peewee.Model):
    release_id = peewee.PrimaryKeyField()
    dependency_id = peewee.CharField(36)


class Product_Mapping_Table(peewee.Model):
    product_id = peewee.PrimaryKeyField()
    dependency_id = peewee.CharField(36)


class Search_View(peewee.Model):
    release_id = peewee.PrimaryKeyField()
    dependency_id = peewee.CharField(50)
    project_id = peewee.CharField(50)
    product_id = peewee.CharField(50)
    project_name = peewee.CharField(50)
    product_name = peewee.CharField(50)
    dependency_version = peewee.CharField(20)
    running_status = peewee.IntegerField()
    crt_date = peewee.DateTimeField()
    release_note = peewee.CharField(250)
