#encoding:utf8
'''
'''
__author__ = 'xuyuming'
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import os
from flask.ext import restful
from flask.ext.restful import reqparse,fields, marshal_with
get_parser = reqparse.RequestParser()
get_parser.add_argument('secucode', type=str,required=True,help="secucode cannot be blank!")
#action='append' 可以支持多值列表传入 默认从flask.Request.values，以及 flask.Request.json 中取值
# fields 支持自定义（基于raw),url,重命名，
# fields.Url('todo_resource', absolute=True, scheme='https')
# 默认值和复杂结构，列表字段\

################################定义输出#################################
dailyqoute_fields = {
    'open': fields.Float,
    'high': fields.Float,
    'close': fields.Float,
    'low': fields.Float,
    'volume': fields.Float,
    'amount':fields.Float,
    'secucode': fields.String,
    'tradeday': fields.String,
}

# 此处列举一系统接口，提供GET方法，供前端调用，生成可视化效果
class DailyQuote(restful.Resource):
    '''
    #定义一个请求参数 股票代码 stockcode
    根据股票代码查
    '''
    @marshal_with(dailyqoute_fields)
    def get(self, secucode):
        config=os.getenv('FLASK_CONFIG')
        if config == 'default':
            db_url='mysql+pymysql://root:root@localhost:3306/python?charset=utf8mb4'
        else:
            db_url='mysql+pymysql://root:Wuxi1107@localhost:3306/test?charset=utf8mb4'
        db_engine = create_engine(db_url, echo=True)
        DB_Session = sessionmaker(bind=db_engine)
        session = DB_Session()
        result=session.execute('select * from cron_dailyquote where secucode = :secucode order by tradeday ', {'secucode': secucode}).fetchall()
        session.close()
        return result

