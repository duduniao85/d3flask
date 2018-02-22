# encoding:utf8
'''
   根据RTTA数据库获取指定客户名称+销售机构代码的当前保有余额+交易账号,用于后续发起交易
'''
__author__ = 'xuyuming'
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import os
from flask.ext import restful
from flask import request
from flask.ext.restful import reqparse, fields, marshal_with
import cx_Oracle
import chardet

# parser.add_argument('transactionaccount', type=str)
# action='append' 可以支持多值列表传入 默认从flask.Request.values，以及 flask.Request.json 中取值
# fields 支持自定义（基于raw),url,重命名，
# fields.Url('todo_resource', absolute=True, scheme='https') 可以支持https
# 默认值和复杂结构，列表字段\

################################定义输出#################################
user = {
    'investorname': fields.String
}

# 此处列举一系统接口，提供GET方法，供前端调用，生成可视化效果
class users(restful.Resource):
    '''
    #定义一个请求参数 股票代码 stockcode
    根据股票代码查
    '''
    # 处理post请求的响应结果，包含多个参数
    @marshal_with(user)
    def get(self):
        #args = request.get_json(force=True)
        host = '106.15.183.29'
        port = '1521'
        sid = 'transdb'
        user = 'kdta_ta_zo'
        password = '1'

        cstr = 'oracle://{user}:{password}@{host}:{port}/{sid}'.format(user=user, password=password, host=host,
                                                                       port=port, sid=sid)
        db_engine = create_engine(cstr, echo=True)
        DB_Session = sessionmaker(bind=db_engine,autocommit=True)
        session = DB_Session()
        result = session.execute(u"""select investorname from ACCT_FUND t where t.TAACCOUNTID like 'RT1T99999%'""").fetchall() #
        session.close()
        return result
