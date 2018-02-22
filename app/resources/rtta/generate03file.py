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
from flask import Flask, jsonify
import json
# import cx_Oracle


class genFile(restful.Resource):
    def generateFile(self, datalist, batchno, busidate, agencyno, filepath):
        '''
        根据指定的数据列表，生成统计数据，根据销售商代码+批次号+业务日期 生成指定的文件名，一次生成1个
        :param datalist: 数据集列表
        :param batchno:  批次号
        :param busidate: 业务日期
        :param agencyno: 销售商代码
        :param filepath: 文件路径
        :return: 无返回
        '''
        contentlist = []  # 记录明细数据
        totalcount = 0  # 记录汇总信息，等于datalist里面所有的记录数的和
        totalamout = 0.00  # 总的申请金额
        totalvol = 0.00  # 的总申请份额
        for data in datalist:
            totalcount += 1
            content = ''  # 初始化单行数据
            totalamout += float(data['applicationamount'])
            totalvol += float(data['applicationvol'])
            print (data['ecapserialno']+'|'+data['takeincomeflag'] if data['takeincomeflag'] else ''+'|'+"")
            # content=str(float(data['applicationvol']))+'|'+str(float(data['applicationamount']))
            content = '{ecapserialno}|{appsheetserialno}|{transactionaccountid}|{fundcode}|{distributorcode}|{businesscode}|{takeincomeflag}|{targettransactionaccount}|{targetdistributorcode}|{transactiondate}|{orgibusitime}|{applicationvol}|{applicationamount}|{custtype}|'\
                .format(ecapserialno=data['ecapserialno']
                        ,appsheetserialno=data['appsheetserialno']
                        ,transactionaccountid=data['transactionaccountid']
                        ,fundcode=data['fundcode']
                        ,distributorcode=data['distributorcode']
                        ,businesscode=data['businesscode']
                        ,takeincomeflag=data['takeincomeflag'] if data['takeincomeflag'] else ''
                        ,targettransactionaccount=data['targettransactionaccount'] if data['targettransactionaccount'] else ''
                        ,targetdistributorcode=data['targetdistributorcode'] if data['targetdistributorcode'] else ''
                        ,transactiondate=data['transactiondate']
                        ,orgibusitime=data['orgibusitime']
                        ,applicationvol=data['applicationvol']
                        ,applicationamount=data['applicationamount']
                        ,custtype=data['custtype'])
            content += '\n'
            print content
            content = content.encode("gb2312")
            contentlist.append(content)
        suminfo = u'总笔数:' + str(totalcount) + '|' + u'总金额:' + str(totalamout) + '|' + u'总份额:' + str(totalvol) + '\n'
        headinfo = u'销售机构订单号|申请单编号|交易账号|基金代码|机构代码|业务类型|收益归属标识|目标交易账号|目标机构代码|交易申请所属交易日|交易时间|申请份额|申请金额|个人/机构标识|备注\n'
        filename = filepath+r'\60_%s_trade_apply_%s_%s.txt'%(agencyno,busidate,batchno)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(filename, 'w') as f:
            f.write(suminfo.encode("gb2312"))
            f.write(headinfo.encode("gb2312"))
            for line in contentlist:
                f.write(line)
            f.close()

    '''
    生成类似支付定发过来的非标交易文件,获取日期参数
    '''
    # 处理post请求的响应结果，包含多个参数
    def post(self):
        args = request.get_json(force=True)
        busidate = args['busidate']
        #指定本地测试库需要的案例
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
        result = session.execute('''select * from temp_ecpay_trade t
                                 where DISTRIBUTORCODE='304' and substr(orgibusitime,0,8) = :busidate''',
                                 {'busidate': busidate}).fetchall()
        session.close()
        # 上面完成相应的数据读取之后
        # 使用result list表对象的filter方法，生成子列表，每个小时的子列表，再发送到指定的函数当中快速生成指定的非标03文件
        filepath=r'c:\software\rtta\file\60\input\01008\%s'%(busidate) #网商的文件目录
        print filepath
        for i in range(24):
            self.generateFile(filter(lambda x:x['orgibusitime'][8:10]==str(i).zfill(2),result),str(i).zfill(2), busidate, '304', filepath)




        session = DB_Session()
        result = session.execute('''select * from temp_ecpay_trade t
                                 where DISTRIBUTORCODE='925' and substr(orgibusitime,0,8) = :busidate''',
                                 {'busidate': busidate}).fetchall()
        session.close()
        filepath=r'c:\software\rtta\file\60\input\01018\%s'%(busidate) #网商的文件目录
        print filepath
        for i in range(24):
            self.generateFile(filter(lambda x:x['orgibusitime'][8:10]==str(i).zfill(2),result),str(i).zfill(2), busidate, '925', filepath)
        return jsonify({'returncode': '0000','returnmsg':u'生成文件成功，请在服务器相应目录%s查看生成后的文件'%('c:\\software\\rtta\\file\\60\\input\\')})
