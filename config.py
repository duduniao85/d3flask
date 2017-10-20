#encoding:utf8
'''
'''
#from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os
__author__ = 'xuyuming'

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    '''
    提供与生产和测试无关的配置
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[datacollector.cn]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky>@example.com'
    #FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    JOBS = [
        {
            'id': 'job1',
            'func': 'manage:lianjiatask',
            'args': (1, 2),
            'trigger': {
                    'type': 'cron',
                    'day_of_week':'0-6',
                    'hour':'17',
                    'minute':'59' },
            #'seconds': 86400
        }
    ]
    SCHEDULER_API_ENABLED = True
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/python?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Wuxi1107@localhost:3306/test?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #任务调度信息
    # SCHEDULER_JOBSTORES = {
    #     'default': SQLAlchemyJobStore(url='mysql+pymysql://root:root@localhost:3306/python?charset=utf8mb4')
    # }
    # SCHEDULER_EXECUTORS = {
    #     'default': {'type': 'processpool', 'max_workers': 1}
    # }
    # SCHEDULER_JOB_DEFAULTS = {
    #     'coalesce': False,
    #     'max_instances': 1
    # }

config = {
    'development': DevelopmentConfig,
    # 'testing': TestingConfig,        #UAT测试环境配置
    'production': ProductionConfig,  #生产环境配置
    'default': DevelopmentConfig
}

