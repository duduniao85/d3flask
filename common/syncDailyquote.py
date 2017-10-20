#encoding:utf8
'''
2017-10-17
每天自动同步万得的股票行情到阿里云数据库当中，以支持前端界面的可视化需求
'''
__author__ = 'xuyuming'
import cx_Oracle
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import time
# step1 从万得同步数据 万得数据库类型为oracle 同步数据为日交易复权行情 存量同步的数据
# 2017年9月1日（含）之前的数据，后续再想办法通过CSV文件进行同步，按年进行同步，同步3年即可
def getDailyQuote():
    #获取当前系统时间
    #today='20171019'
    #today2='2017-10-19'
    today=time.strftime('%Y%m%d',time.localtime(time.time()))
    today2=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    db_engine = create_engine('oracle://wind:wind@172.16.10.101:1521/orcl', echo=False)
    DB_Session = sessionmaker(bind=db_engine)
    session = DB_Session()
    s = (          "select "
          "F16_1090,"
          "to_char(to_date(F2_1425,'yyyymmdd'),'yyyy-mm-dd'),"#交易日期
          "F4_1425,"# 开盘价
          "F5_1425,"#最高价
          "F7_1425,"# 收盘价
          "F6_1425,"# 最低价
          "F8_1425*100,"# 成交量
          "F9_1425*1000" # 成交金额
          " from TB_OBJECT_1425 , TB_OBJECT_1090 "
          " where TB_OBJECT_1425.F1_1425=TB_OBJECT_1090.F2_1090 "
          " AND TB_OBJECT_1425.F2_1425="+"'"+today+"'"+" AND F4_1090='A'")#只取A股数据
    selectsql = text(s)
    result = session.execute(selectsql)  # 执行查询语句
    df_result = pd.DataFrame(result.fetchall())
    try:
        df_result.columns = ['secucode', 'tradeday', 'open', 'high','close','low','volume','amount']  # 列重命名
        df_result = df_result.set_index('secucode')
        print df_result.head()
        session.close()
    except Exception:
        print 'error! no data prepared for '+ today2
        session.close()
    else:
        # step2 将得到的数据同步到阿里云MYSQL ,直接采用先删除指定一天的行情，然后再插入
        db_url='mysql+pymysql://root:Wuxi1107@106.14.120.19:3306/test?charset=utf8mb4'
        mysql_engine = create_engine(db_url)
        DB_Session = sessionmaker(bind=mysql_engine)
        session = DB_Session()
        s = "delete from cron_dailyquote    where tradeday="+"'"+today2+"'" #删除指定日期行情的数据
        deletesql = text(s)
        result = session.execute(deletesql)  # 执行删除语句
        session.commit()
        session.close()
        df_result.to_sql('cron_dailyquote',mysql_engine,if_exists='append')

## todo 同步A股日行情指标
## todo 同步
getDailyQuote()