#encoding:utf8
'''
'''
__author__ = 'xuyuming'
#该文件包含了所有的资源，注册资源地方，

# -*- coding: utf-8 -*-

import os
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate,MigrateCommand
from flask import Flask,render_template
from flask.ext.script import Manager,Shell
from common.utils import lock,unlock,LOCK_EX
from flask import Flask
from flask.ext import restful
from flask.ext.restful import Resource, Api
import atexit
#import fcntl
import logging
import tushare as ts
from app import create_app, db
from flask_apscheduler import APScheduler
from common.tasks import  crawlLianjiaSaleData,crawlLianjiaChengjiao,crawlDailyQuote
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)
def make_shell_context():
    return dict(app=app, db=db)
manager.add_command("shell", Shell(make_context=make_shell_context))#用于测试
manager.add_command('db',MigrateCommand)
#定时任务，打印USERS
def lianjiatask(a,b):
    #开始抓取挂牌房源
    logging.info('task runs!')
    crawlLianjiaSaleData(app)
    crawlLianjiaChengjiao(app)
    #crawlDailyQuote()
#定义日志记录方式
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
                    datefmt='%Y-%m-%d %H:%M:%S',filename='cronlog.txt',filemode='a')
#将应用封装为API
api = Api(app)
#测试

@app.route('/')
def index():
    return render_template('AppMonitor.html')
@app.route('/demo')
def demo():
    return render_template('demo.html')

#直接从tushare返回相应数据进行可视化操作，在操作性能相对可控的情况可以不落地直接查询此数据，后续在加上交互
#存款准备金率的变化
@app.route('/fundamental/rrr')
def rrr():
    return ts.get_rrr().sort_values(by=('date'),ascending=True).to_json(orient='records')
#三大产业对GPD的拉动


#Todo 指定股票代码的K线图，指定URL,然后生成对应的图表
from app.resources.stock import DailyQuote
api.add_resource(DailyQuote, '/dailyquote/<secucode>')
#TODO 指定行业涨幅变化势势图




# TODO  缺少注册和登录模块
##############################
#注册定时任务
# f = open("scheduler.lock", "wb")
# try:
#     fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
#     scheduler = APScheduler()
#     scheduler._logger=logging
#     scheduler.init_app(app)
#     scheduler.start()
# except:
#     pass
# def unlock():
#     fcntl.flock(f, fcntl.LOCK_UN)
#     f.close()
# atexit.register(unlock)
if __name__ == '__main__':
    # init_db()
    # app.debug = True
    # app.run()
    manager.run()
