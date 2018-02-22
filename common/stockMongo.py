 # -*- coding:utf-8 -*-
#从ORACLE当中查询万得基本信息数据更新到mongodb当中

from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import os
import sys
import pandas as pd
import cx_Oracle
reload(sys)
sys.setdefaultencoding('utf8')
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.ZHS16GBK'
# wind 数据库信息
host = '172.16.61.36'
port = '1801'
sid = 'winddb'
user = 'wind_it'
password = 'wind_it'
cstr = 'oracle://{user}:{password}@{host}:{port}/{sid}'.format(user=user, password=password, host=host,                                                                       port=port, sid=sid)
db_engine = create_engine(cstr, echo=False,encoding='utf-8',convert_unicode=True)
DB_Session = sessionmaker(bind=db_engine)
session = DB_Session()
result = session.execute(" select t.F16_1090 ,                                 "
"        t.OB_OBJECT_NAME_1090 ,                                  "
"        t.F5_1090 ,                                   "
"        t.F6_1090 ,                                   "
"        T.F17_1090 ,                                 "
"        OB_OBJECT_NAME_1018,                                   "
"        F4_1018,                                   "
"        F5_1018 ,                                   "
"        F6_1018 ,                                   "
"        F7_1018,                                   "
"        F16_1018 ,                                 "
"        F18_1018 ,                                 "
"        F35_1018 ,                                 "
"        F44_1018 ,                                 "
"        (Select a.name                                           "
"           From wind.tb_object_1400, wind.tb_object_1022 a       "
"          Where substr(f3_1400, 1, 4) = substr(a.code, 1, 4)     "
"            And a.code Like '62%'                                "
"            And a.levelnum = '2'                                 "
"            And F6_1400 = '1'                                    "
"            And F4_1090 In ('A', 'B')                            "
"            And F1_1400 = OB_REVISIONS_1090)  ,                  "
"        (Select a.name                                           "
"           From wind.tb_object_1400, wind.tb_object_1022 a       "
"          Where substr(f3_1400, 1, 6) = substr(a.code, 1, 6)     "
"            And a.code Like '62%'                                "
"            And a.levelnum = '3'                                 "
"            And F6_1400 = '1'                                    "
"            And F4_1090 In ('A', 'B')                            "
"            And F1_1400 = OB_REVISIONS_1090) ,                   "
"        (Select a.name                                           "
"           From wind.tb_object_1400, wind.tb_object_1022 a       "
"          Where substr(f3_1400, 1, 8) = substr(a.code, 1, 8)     "
"            And a.code Like '62%'                                "
"            And a.levelnum = '4'                                 "
"            And F6_1400 = '1'                                    "
"            And F4_1090 In ('A', 'B')                            "
"            And F1_1400 = OB_REVISIONS_1090) ,                   "
"        (Select a.name                                           "
"           From wind.tb_object_1400, wind.tb_object_1022 a       "
"          Where f3_1400 = substr(a.code, 1, 10)                  "
"            And a.code Like '62%'                                "
"            And a.levelnum = '5'                                 "
"            And F6_1400 = '1'                                    "
"            And F4_1090 In ('A', 'B')                            "
"            And F1_1400 = OB_REVISIONS_1090) ,                   "
"        OB_OBJECT_NAME_1179 ,                                    "
"        OB_OBJECT_NAME_1180 ,                                    "
"        F42_1018 ,                                               "
"        F48_1018                                                 "
"   from wind.TB_OBJECT_1090 T,                                   "
"        WIND.TB_OBJECT_1018,                                     "
"        wind.TB_OBJECT_1179,                                     "
"        TB_OBJECT_1180                                           "
"  where f21_1090 = '1'                                           "
"    AND T.OB_REVISIONS_1090 = TB_OBJECT_1018.F34_1018            "
"    and TB_OBJECT_1018.F40_1018 = TB_OBJECT_1179.F1_1179         "
"    and f4_1090 = 'A'       and f16_1090<>'000001'                "
"    and TB_OBJECT_1018.F41_1018 = TB_OBJECT_1180.F1_1180         "
).fetchall()
session.close()
df=pd.DataFrame(result,columns=[u'证券代码',u'证券简称',u'交易所',u'上市板',\
                               u'上市日期',u'公司名称',u'省份',u'城市',u'注册地址',u'办公地址',\
                                u'主页',u'注册资本',u'成立日期',u'员工总数',u'所属万得一级行业',u'所属万得二级行业',u'所属万得三级行业',\
                                u'所属万得四级行业',u'公司类别',u'公司类型',u'公司简介',u'主要产品及业务'])
import chardet
print chardet.detect(df[u'公司简介'].values[0].decode('gbk').encode('utf-8'))
from pymongo import MongoClient
import decimal
import json
client  = MongoClient('127.0.0.1', port=27017)
db=client.stockdb
for i in df.to_dict(orient='records'):
    for key in i.keys():
        if isinstance(i[key],str):
            i[key]=(i[key].decode('gbk').encode('utf-8'))
        if isinstance(i[key],decimal.Decimal):
            i[key]=float(i[key])
    db.stock.insert_one(i)

######################################################TODO 2 ,同步行情信息



#####################################################TODO 3，同步大股东信息


######################################################TODO 4，同步股东户数信息（1151）


##################################################### TODO 5 ，上市公司的股票关系 （1671）



##################################################### TODO 6 同步增发历史1094，分红历史1093，配股历史 1092




#################################################### TODO 7,同步财务数据信息,




