# encoding:utf8
'''
   根据前端表单动态增加一笔交易申请对象
   同时提供返回完整新增的交易申请列表 get
'''
__author__ = 'xuyuming'
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import os
from flask import Flask, jsonify
from flask.ext import restful
from flask import request
from flask.ext.restful import reqparse, fields, marshal_with
import uuid
from flask.ext.api import status
parser = reqparse.RequestParser()
parser.add_argument('investorname',location='args',type=str,required=True,help=u"投资者姓名不能为空")
################################定义输出#################################
traderequest = {
    'ecapserialno': fields.String,
    'distributorcode': fields.String,
    'businesscode': fields.String,
    'takeincomeflag': fields.String,
    'targetinvestorname': fields.String,
    'targetdistributorcode': fields.String,
    'transactiondate': fields.String,
    'orgibusitime': fields.String,
    'applicationvol': fields.Float,
    'applicationamount': fields.Float,
    'investorname': fields.String
}

# 此处列举一系统接口，提供GET方法，供前端调用
#
class traderequest(restful.Resource):
    '''
    提供get接口获取所有申请, 根据交易发起方查询交易
    '''

    @marshal_with(traderequest)
    def get(self):
        # = request.get_json(force=True)
        args = parser.parse_args()
        investorname = args['investorname']
        host = '106.15.183.29'
        port = '1521'
        sid = 'transdb'
        user = 'kdta_ta_zo'
        password = '1'

        cstr = 'oracle://{user}:{password}@{host}:{port}/{sid}'.format(user=user, password=password, host=host,
                                                                       port=port, sid=sid)
        db_engine = create_engine(cstr, echo=True)
        DB_Session = sessionmaker(bind=db_engine)
        session = DB_Session()
        result = session.execute("""select ecapserialno ecapserialno,
                    t.distributorcode,
                    t.businesscode,
                    takeincomeflag,
                    t3.investorname as targetinvestorname,
                    targetdistributorcode,
                    transactiondate,
                    orgibusitime,
                    applicationvol,
                    applicationamount,
                    t2.investorname investorname

               FROM TEMP_ECPAY_TRADE T,
                    ACCT_FUND        T2,
                    ACCT_FUND        T3,
                    ACCT_TRANS       T4,
                    ACCT_TRANS       T5
              WHERE T2.INVESTORNAME  like '%{investorname}%'
                AND T.TRANSACTIONACCOUNTID = T4.TRANSACTIONACCOUNTID
                AND T4.TAACCOUNTID = T2.TAACCOUNTID
                AND T.TARGETTRANSACTIONACCOUNT = T5.TRANSACTIONACCOUNTID(+)
                AND T5.TAACCOUNTID = T3.TAACCOUNTID(+)
                ORDER BY ORGIBUSITIME""".format(investorname=str(investorname))).fetchall()
        session.close()
        return result  # 如果是列表,只需要返回结果集直接返回即可

    # 处理post请求的响应结果，包含多个参数
    def post(self):
        args = request.get_json(force=True)
        #ecapserialno = str(uuid.uuid1()).replace('-', '')  # 销售机构订单号
       #appsheetserialno = ecapserialno  # 申请单号
        ecapserialno = args['ecapserialno']
        appsheetserialno=ecapserialno
        investorname = args['investorname']
        distributorcode = args['distributorcode']
        businesscode = args['businesscode']  # 22:申购，98:快取，26:转换管，24:普通赎回
        takeincomeflag = args['takeincomeflag']  # 下拉 305，926 默认305
        transactiondate = args['transactiondate']  # 申请工作日
        orgibusitime = args['orgibusitime']  # 原始下单时间，支持时间控件
        applicationvol = args['applicationvol']  # 申请份额
        applicationamount = args['applicationamount']  # 申请金额
        try:
            targetinvestorname = args['targetinvestorname']  # 交易对手姓名
            targetdistributorcode = args['targetdistributorcode']  # 交易对手所在销售商
        except Exception:
            targetinvestorname=''
            targetdistributorcode=''

        config = os.getenv('FLASK_CONFIG')
        print investorname, businesscode, takeincomeflag, transactiondate
        # 必填字段校验
        if investorname is None \
                or businesscode is None \
                or takeincomeflag is None \
                or transactiondate is None \
                or orgibusitime is None \
                or applicationvol is None \
                or applicationamount is None:
            return {'returncode': '9999', 'returnmsg': u'必填字段不能省略'}, status.HTTP_406_NOT_ACCEPTABLE
        if businesscode in ['026', '033'] and targetdistributorcode is None:
            return {'returncode': '9998', 'returnmsg': u'非交易过户和转托管必须填对方销售商'}, status.HTTP_406_NOT_ACCEPTABLE
        if businesscode == '033' and (targetinvestorname is None or targetinvestorname == investorname):
            return {'returncode': '9997', 'returnmsg': u'非交易过户必须填对方姓名并且不能为同一个人'}, status.HTTP_406_NOT_ACCEPTABLE
        print businesscode, applicationvol, applicationamount, float(applicationvol) <= 0
        if (businesscode in ['024', '098', '033', '026'] and float(applicationvol) <= 0) or (
                        businesscode in ['022'] and float(applicationamount) <= 0):
            return {'returncode': '9996', 'returnmsg': u'指定交易类型的申请金额或者申请份额不合法'}, status.HTTP_406_NOT_ACCEPTABLE
        if businesscode == '022' and (takeincomeflag <> '000' or takeincomeflag is None):
            return {'returncode': '9995', 'returnmsg': u'申购类型的收益带出标志应该为000或者为空'}, status.HTTP_406_NOT_ACCEPTABLE

        # 参数校验

        host = '106.15.183.29'
        port = '1521'
        sid = 'transdb'
        user = 'kdta_ta_zo'
        password = '1'

        cstr = 'oracle+cx_oracle://{user}:{password}@{host}:{port}/{sid}'.format(user=user, password=password,
                                                                                 host=host,
                                                                                 port=port, sid=sid)
        db_engine = create_engine(cstr, echo=False)
        DB_Session = sessionmaker(bind=db_engine, autocommit=True)
        session = DB_Session()
        # 执行插入语句
        s = ("""insert into temp_ecpay_trade
  (ecapserialno,
   appsheetserialno,
   transactionaccountid,
   fundcode,
   distributorcode,
   businesscode,
   takeincomeflag,
   targettransactionaccount,
   targetdistributorcode,
   transactiondate,
   orgibusitime,
   applicationvol,
   applicationamount,
   custtype)
  select '{ecapserialno}', --ecapserialno
         '{appsheetserialno}', --appsheetserialno
         t2.transactionaccountid,
         '001211',
         t2.distributorcode,
         '{businesscode}',
         '{takeincomeflag}',
         (select t2.transactionaccountid
            from acct_fund t, acct_trans t2
           where t.investorname = '{targetinvestorname}'
             and t.taaccountid = t2.taaccountid
             and t2.distributorcode = '{targetdistributorcode}'),
         (select t2.distributorcode
            from acct_fund t, acct_trans t2
           where t.investorname = '{targetinvestorname}'
             and t.taaccountid = t2.taaccountid
             and t2.distributorcode = '{targetdistributorcode}'),
         '{transactiondate}',
         '{orgibusitime}',
         '{applicationvol}',
         '{applicationamount}',
         t.invtp
    from acct_fund t, acct_trans t2
   where t.investorname = '{investorname}'
     and t.taaccountid = t2.taaccountid
     and t2.distributorcode = '{distributorcode}'""".format(ecapserialno=str(ecapserialno)
                                                            , appsheetserialno=str(appsheetserialno)
                                                            , distributorcode=str(distributorcode)
                                                            , businesscode=str(businesscode)
                                                            , takeincomeflag=str(takeincomeflag or '')
                                                            , targetdistributorcode=str(
                targetdistributorcode) if targetdistributorcode else ''
                                                            , transactiondate=str(transactiondate)
                                                            , investorname=str(investorname)
                                                            , targetinvestorname=str(targetinvestorname)
                                                            , orgibusitime=str(orgibusitime)
                                                            , applicationvol=applicationvol
                                                            , applicationamount=applicationamount
                                                            ))
        result = session.execute(s)
        session.close()
        return args
