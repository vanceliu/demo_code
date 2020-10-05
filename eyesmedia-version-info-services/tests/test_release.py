try:
    from config.application import app_context
    from db.mysql_dao import ReleaseDao, ReleaseMappingDao, SearchViewDao
    from service.release_service import ReleaseVo, ReleaseService
    from eyesmediapyutils.exceptions import CommonRuntimeException
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



# code start here---
"""
前端資料 匯入形式
"""
# -------------



class VoTestCase(unittest.TestCase):
    pass



class ReleaseTestCase(unittest.TestCase):
    pass



if __name__ == '__main__':
    unittest.main()