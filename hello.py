#encoding:utf8
from flask import  Flask,render_template
import pandas as pd
import tushare as ts
import numpy as np
app = Flask(__name__)
@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

@app.route("/monitor", methods=["GET"])
def monitor():
    return render_template('AppMonitor.html')

@app.route('/indexquote',methods=['GET', 'POST'])
def indexquote():
    df=ts.get_rrr()
    df=df.sort(columns='date')
    return df.to_json(orient='records')

@app.route('/monitor',methods=['GET', 'POST'])
def appstat():
    '''
    根据随机数生成几类API的统计数据，并返回给前端
    这里做一个生成随机数的测试数据方便测试前端JS界面，做一个动态的ECHARTS图表，再做一个按天统计的ECHARTS图表
    :return:
    '''
    df=pd.DataFrame()
    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)