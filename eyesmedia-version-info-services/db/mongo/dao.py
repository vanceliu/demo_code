# -*- coding: utf-8 -*-
import logging
import pymongo
from eyesmediapydb.mongo_base import MongoRepository
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

'''
新增的Dao class 需在db/mongo目錄底下的__init__.py import 新的Dao class
'''


class NluCategoryDao(MongoRepository):
    def __init__(self, mongo_client):
        super().__init__(mongo_client)

    def _get_collection_name(self):
        return "nlu_category"

    def count_by_code(self, code):
        return self.count({"code": code})

    def find_by_code(self, code):
        return self.find({"code": code})

    def find_by_name(self, name):
        return self.find({"name": name})

    def count_by_ids(self, id_list):
        ids = [ObjectId(id) for id in id_list]
        return self.count({"_id": {"$in": ids}})


if __name__ == "__main__":
    import traceback
    import utils
    from config.application import app_context
    from db.mongo.models import NluCategory

    try:
        app_context.init_mongo_client()

        dao = NluCategoryDao(app_context.mongo_client)
        data_list = utils.read_csv_file("/Users/admin/Documents/workspace/eyesmedia-corpus-server/data/nlu", "category.csv")
        for data in data_list:
            model = NluCategory()
            model.code = data[0]
            model.name = data[1]
            dao.save_one(model.to_dict())

        # dao = SentenceDao(app_context.mongo_client)
        # logger.info(dao.find_by_ids(["5b767a38efaa657a7929fa95"]))
    except:
        logger.error(traceback.format_exc())
