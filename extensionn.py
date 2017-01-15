__author__ = 'Administrator'
#encoding:utf8
"""
@author:xuyuming
@contact:283548048@qq.com
@time:2016/12/29 22:44
""" 
from flask.ext.script import Manager
from flask import  Flask
app= Flask(__name__)
@app.route('/')
def index():
    return '<h1>hello world!<h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1>hello,%s!</h1>' % name,400



manager=Manager(app)

@manager.command
def test():
    print 'test'

if __name__ == '__main__':
    manager.run()