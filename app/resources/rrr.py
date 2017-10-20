#encoding:utf8
'''
返回准备金率历史数据
'''
__author__ = 'xuyuming'
from flask.ext import restful
from flask.ext.restful import reqparse,fields, marshal_with
import tushare as ts
#get_parser = reqparse.RequestParser()
#get_parser.add_argument('secucode', type=str,required=True,help="secucode cannot be blank!")
#action='append' 可以支持多值列表传入 默认从flask.Request.values，以及 flask.Request.json 中取值
# fields 支持自定义（基于raw),url,重命名，
# fields.Url('todo_resource', absolute=True, scheme='https')
# 默认值和复杂结构，列表字段\

################################定义输出#################################
rrr_fields = {
    'date': fields.String,
    'before': fields.String,
    'now': fields.String,
    'changed': fields.String
}

# 此处列举一系统接口，提供GET方法，供前端调用，生成可视化效果
class rrr(restful.Resource):
    '''
    #定义一个请求参数 股票代码 stockcode
    根据股票代码查
    '''
    @marshal_with(rrr_fields)
    def get(self):
        result=ts.get_rrr()
        print result.T
        return result.T

