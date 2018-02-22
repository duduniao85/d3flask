#encoding:utf8
'''
'''
__author__ = 'xuyuming'
# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.ext import restful
from config import config

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__,static_url_path='')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    #
    # # 注册蓝本
    # # 增加auth蓝本
    # from app.api_1_0 import api as api_1_0_blueprint
    # app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
    #
    # # 附加路由和自定义的错误页面

    return app