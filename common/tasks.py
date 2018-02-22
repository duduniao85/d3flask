#encoding:utf8
'''
此文件用于定义若干定时任务，用于夜间自动跑批
'''
__author__ = 'xuyuming'
import datetime
import time
from app.models.lianjiasale import lianjiasale
from app.models.lianjiadeal import lianjiadeal
import tushare as ts
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import *
from app.models.lianjiasalepricechg import SalePriceChg
import requests
from selenium import webdriver
from app import db
from bs4 import BeautifulSoup
import urllib2
import os
from utils import getLastNdate
def getDealList(headers, pageUrl):
    """
    传入指定的需要抓取的页面
    返回需要抓取的明细项url列表,以及url列表对应明细项的签约日期
    """

    req = urllib2.Request(pageUrl, headers=headers)
    textdata = urllib2.urlopen(req).read()
    soup = BeautifulSoup(textdata, 'lxml')
    itemUrlList = soup.select(
        '#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div:nth-of-type(1) > a')
    # 签约日期
    itemDealDate = soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div:nth-of-type(2) > div.info-col.deal-item.main.strong-num')
    # ID
    itemIdList = soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > a')
    # 区县
    itemQuxianList = soup.select(
        '#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div:nth-of-type(3) > span > a:nth-of-type(1)')
    # 片区
    itemPianquList =soup.select(
        '#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div:nth-of-type(3) > span > a:nth-of-type(2)')
    #js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div:nth-child(3) > span > a:nth-child(4)
    # 楼层/层高,朝向，装修程度
    itemLoucengList = soup.select(
        '#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div:nth-of-type(2) > div.row1-text')
    # 面积 小区名称 房型
    itemMianjiList = soup.select(
        '#js-ershoufangList > div.content-wrapper > div.content > div > ul > li  > div > div.info-table > div:nth-of-type(1) > a')
    # 总价
    itemZongjiaList = soup.select(
        '#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div:nth-of-type(2) > div.info-col.price-item.main > span.strong-num')
    # 单价
    itemDanjiaList = soup.select(
        '#js-ershoufangList > div.content-wrapper > div.content > div > ul > li  > div > div.info-table > div:nth-of-type(3) > div.info-col.price-item.minor')
    itemList = []

    for itemUrl, itemDate, itemId, itemQuxian, itemPianqu, itemLouceng, itemMianji, itemZongjia, itemDanjia in \
            zip(itemUrlList, itemDealDate, itemIdList, itemQuxianList, itemPianquList, itemLoucengList, itemMianjiList,
                itemZongjiaList, itemDanjiaList):
        temp_strlist = list(itemLouceng.stripped_strings)
        item = {
            'itemurl': itemUrl.get('href'),
            'signdate': itemDate.get_text().replace(u'.',''),
            'itemid': itemId.get('key'),
            'quxian': itemQuxian.get_text(),
            'pianqu': itemPianqu.get_text(),
            'louceng': temp_strlist[0] if (len(temp_strlist) > 0) else '',  # 不是所有的房子都包含楼层信息，没有则置空
            'chaoxiang': temp_strlist[2] if (len(temp_strlist) > 2) else '',  # 不是所有的房子都包含朝向信息，没有则置空
            'mianji': itemMianji.get('title').split(' ')[2].replace(u'平米', ''),
            'zongjia': list(itemZongjia.stripped_strings)[0],
            'danjia': list(itemDanjia.stripped_strings)[0].replace(u'单价', ''),
            'xiaoqu': itemMianji.get('title').split(' ')[0],
            'huxing': itemMianji.get('title').split(' ')[1]
        }
        itemList.append(item)
    return itemList
def http_post_for_lianjiadeals(offset, headers):
    """
    抓取指定分页的挂牌房源数量
    http://soa.dooioo.com/api/v4/online/house/ershoufang/search
    :param params:查询参数集合
    :param offset:查询的偏移量
    :return:
    """
    url = r'http://soa.dooioo.com/api/v4/online/house/ershoufang/search?access_token=7poanTTBCymmgE0FOn1oKp&channel=ershoufang&cityCode=sh&client=pc&limit_count=200&limit_offset=' + str(
        offset)
    print url
    r = requests.get(url, headers=headers)
    return r.json()
def crawlLianjiaSaleData(app):
    '''
    抓取链家挂牌数据
    :return:
    '''
    #开始
    with app.app_context():
        hasMoreData=1
        headers2={'User-Agent':
                      'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36'
                  }
        headers1={'User-Agent':
                      'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'
                  }
        offset=1
        count=0
        while(True):
            time.sleep(2)
            if count%2==1:
                headers=headers2
            else:
                headers=headers2
            try:
                jsonObj= http_post_for_lianjiadeals(offset,headers)
            except Exception,e:
                print 'page'+str(offset)+u' 抓取异常'
                time.sleep(2)
                continue
            hasMoreData=jsonObj.get('data').get('has_more_data')
            if hasMoreData == 0 :#标记还有数据
                break
            itemList= jsonObj.get('data').get('list')
            if len(itemList)==0:#房源列表是否为空，如果为空，表示已经到循环的尽头，可以退出
                break
            for i in itemList:
                data=lianjiasale(
                    acreage=i['acreage'],
                    cityCode=i['cityCode'],
                    dealAvgPrice=i['dealAvgPrice'],
                    districtName=i['districtName'],
                    face=i.get('face','未知'),
                    floor_state=i['floor_state'],
                    hall=i['hall'],
                    houseSellId=i['houseSellId'],
                    isRecommend=i['isRecommend'],
                    label=i['label'],
                    latitude=i['latitude'],
                    longitude=i['longitude'],
                    metroRemark=i['metroRemark'],
                    plateName=i['plateName']	,
                    propertyName=i['propertyName'],
                    propertyNo=i['propertyNo'],
                    referAvgPrice=i['referAvgPrice'],
                    room=i['room'],
                    showPrice=i['showPrice'],
                    title=i.get('title','未知'),
                    unitPrice=i['unitPrice'],
                    insertdate=time.strftime('%Y-%m-%d',time.localtime(time.time()))
                )
                existList=lianjiasale.query.filter_by(houseSellId=i['houseSellId']).first()
                #不存在则插入
                if existList and ((float(i['showPrice'])-float(existList.showPrice))<>0):
                #存在，但总价和单价发生变化则，则更新相应的表字段,同时记录一条变化的交易记录
                    pricechg=SalePriceChg(
                        houseSellId = i['houseSellId'],# 唯一主键
                        oldshowPrice = existList.showPrice,#原挂牌价
                        oldunitPrice = existList.unitPrice,#原单价
                        newshowPrice = i['showPrice'], #新挂牌价
                        newunitPrice = i['unitPrice'], #新单价
                        priceChg = str(float(i['showPrice'])-float(existList.showPrice)), #总价变化
                        insertdate 	= time.strftime('%Y-%m-%d',time.localtime(time.time()))
                    )
                    db.session.add(pricechg)
                    existList.showPrice=i['showPrice']
                    existList.unitPrice=i['unitPrice']
                    #id相同则更新
                elif not existList:
                    db.session.add(data)
            db.session.commit()
            db.session.close()
            offset+=200
            count+=1

        #将每个数据对象更新到mysql数据库的当中
def crawlLianjiaChengjiao(app):
    '''
    定时抓取成交数据
    :return:
    '''
    #driver=webdriver.Chrome()
    with app.app_context():
        config = os.getenv('FLASK_CONFIG')
        if config=='default':
            executable_path=r'C:\Users\xuyuming\AppData\Roaming\Python\Scripts\phantomjs'
        else:
            executable_path=r'phantomjs'
        print executable_path
        driver=webdriver.PhantomJS(executable_path)
        driver.get("https://passport.lianjia.com/cas/login?service=http://user.sh.lianjia.com/index/ershou")
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys("18616153298")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("Wuxi1107")
        driver.find_element_by_xpath("//*[@id='loginUserForm']/ul/li[5]/button").submit()
        count=1
        print count
        time.sleep(5)#点击登录后休息1s
        cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
        cookiestr = ';'.join(item for item in cookie)
        headers = {'cookie':cookiestr}
        print headers
        #取当前数据库当中最新的成交日期
        newestTradeday = lianjiadeal.query.order_by('-signdate')[0].signdate
        print newestTradeday
        time.sleep(1)
        while(count<=2048):
            prefix=r'http://sh.lianjia.com'
            url=r'http://sh.lianjia.com/chengjiao/d'+str(count)
            print url
            try:
                scndHs4Sale=getDealList(headers,url)
                time.sleep(0.5) #每抓取一页休息0.5s
            except Exception,e:
                print 'page'+str(count)+' error'+str(e)
                time.sleep(1)
                continue

            if len(scndHs4Sale)== 0 :#
                break
            for item in scndHs4Sale:
                # if count%50 ==0 :
                #     time.sleep(1)  #50页休息一秒
                print item['signdate']
                if item['signdate']<newestTradeday:#如果之前的成交数居已经加载完成，则不需要重新加载
                    driver.quit()
                    return None
                data=lianjiadeal(
                    chanxiang = item['chaoxiang'], #朝向
                    danjia = item['danjia'], #单价
                    huxing = item['huxing'], #户型
                    itemid = item['itemid'], # 房源ID
                    itemurl= item['itemurl'],#相对链接
                    loucheng= item['louceng'], #楼层
                    mianji=item['mianji'], #面积
                    pianqu = item['pianqu'], #片区
                    quxian =item['quxian'], #区县
                    xiaoqu =item['xiaoqu'], #小区
                    zongjia =item['zongjia'], #成交总价
                    signdate=item['signdate']#签约日期
                )
                existList=lianjiadeal.query.filter_by(itemid=item['itemid']).first()
                if not existList:
                    db.session.add(data)
                    print item['itemid']+' inserted'
            count+=1
            db.session.commit()
            db.session.close()
        driver.quit()
# def crawlDailyQuote():
#     '''
#
#     :param app:
#     :return:
#     '''
#     config=os.getenv('FLASK_CONFIG')
#     if config == 'default':
#         db_url='mysql+pymysql://root:Wuxi1107@106.14.120.19:3306/test?charset=utf8mb4'
#     else:
#         db_url='mysql+pymysql://root:Wuxi1107@localhost:3306/test?charset=utf8mb4'
#     db_engine = create_engine(db_url, echo=True)
#     conn = db_engine.connect()
#     df = ts.get_stock_basics()
#     df.to_sql('stock_basics',db_engine,if_exists='replace',dtype={'code': CHAR(6)})
#     # 计算距离当前日期最大的工作日
#     today=time.strftime('%Y-%m-%d',time.localtime(time.time()))
#     s1=("select max(t.date) from cron_tradeday t where flag=1 and t.date <='"+ today+"'")
#     selectsql=text(s1)
#     maxTradeay = conn.execute(selectsql).first()
#     print maxTradeay
#     # 计算当前加载的最大工作日期
#     s = ("select secucode,max(t.tradeday) from cron_dailyquote t group by secucode ")
#     selectsql = text(s)
#     result = conn.execute(selectsql)  # 执行查询语句
#     df_result = pd.DataFrame(result.fetchall())
#     df_result.columns=['stockcode','max_tradeday']
#     df_result.set_index(df_result['stockcode'],inplace=True)
#     # 开始归档前复权历史行情至数据库当中，以便可以方便地计算后续选股模型
#     for code in set(list(df.index)):
#         try:
#             #如果当前股票已经是最新的行情数据，则直接跳过
#             if df_result.loc[code].values[1] == maxTradeay[0]:
#                 continue
#             startdate=getLastNdate(df_result.loc[code].values[1],1)
#         except Exception, e:
#             startdate='2013-01-01'
#         print code,startdate
#         try:
#             df_h_data = ts.get_h_data(code, start=startdate, retry_count=10, pause=0.01)  # 包含START
#         except Exception, e:
#             print str(e)
#             time.sleep(10)
#             continue
#         if df_h_data is not None:
#             try:
#                 df_h_data['secucode'] = code
#                 df_h_data.index.name = 'date'
#                 df_h_data['tradeday'] = df_h_data.index.strftime('%Y-%m-%d')
#                 print df_h_data
#                 time.sleep(1)
#                 df_h_data.to_sql('cron_dailyquote', db_engine, if_exists='append', index=False)
#             except Exception, e:  # 如果是新股，则有可能df_h_data是空对象，因此需要跳过此类情况不处理
#                 print str(e)
#                 continue
#     conn.close()


import threading
from Queue import Queue
from Queue import Empty
stock_queue = Queue()
data_queue = Queue()
lock = threading.Lock()

def crawlDailyQuote():
    '''
    用于测试多线程读取数据
    :return:
    '''
    #获取环境变量，取得相应的环境配置，上线时不需要再变更代码
    global stock_queue
    global data_queue
    config=os.getenv('FLASK_CONFIG')
    if config == 'default':
        db_url='mysql+pymysql://root:Wuxi1107@106.14.120.19:3306/test?charset=utf8mb4'
    else:
        db_url='mysql+pymysql://root:Wuxi1107@localhost:3306/test?charset=utf8mb4'
    db_engine = create_engine(db_url, echo=True)
    conn = db_engine.connect()
    #每周读一次，用于更新后台数据
    df = ts.get_stock_basics()
    df.to_sql('stock_basics',db_engine,if_exists='replace',dtype={'code': CHAR(6)})
    # 计算距离当前日期最大的工作日
    today=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    s1=("select max(t.date) from cron_tradeday t where flag=1 and t.date <='"+ today+"'")
    selectsql=text(s1)
    maxTradeay = conn.execute(selectsql).first()
    print maxTradeay
    # 计算当前加载的最大工作日期
    s = ("select secucode,max(t.tradeday) from cron_dailyquote t group by secucode ")
    selectsql = text(s)
    result = conn.execute(selectsql)  # 执行查询语句
    df_result = pd.DataFrame(result.fetchall())
    df_result.columns=['stockcode','max_tradeday']
    df_result.set_index(df_result['stockcode'],inplace=True)
    # 开始归档前复权历史行情至数据库当中，以便可以方便地计算后续选股模型
    for code in set(list(df.index)):
        try:
            #如果当前股票已经是最新的行情数据，则直接跳过,方便重跑
            #print maxTradeay[0],df_result.loc[code].values[1]
            if df_result.loc[code].values[1] == maxTradeay[0]:
                continue
            startdate=getLastNdate(df_result.loc[code].values[1],1)
        except Exception, e: # 取不到历史行情则直接获取所有行情
            startdate='2013-01-01'
        item={}
        item['code']=code
        item['startdate']=startdate
        stock_queue.put(item)

    for i in range(8):#使用5个线程读数据
        t = ThreadRead(stock_queue, data_queue)
        t.setDaemon(True)
        t.start()

    for i in range(7):#使用4个线程入库
        t = ThreadWrite(data_queue, lock, db_engine)
        t.setDaemon(True)
        t.start()

    data_queue.join()
    stock_queue.join()


class ThreadRead(threading.Thread):
    def __init__(self, queue, out_queue):
        '''
        用于根据股票代码、需要读取的日期，读取增量的日行情数据，其中queue用于保存需要读取的股票代码的列表
        :param queue:用于保存需要读取的股票代码的列表
        :param out_queue:用于保存需要写入到数据库表的结果集列表
        :return:
        '''
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.thread_stop = False
    def run(self):
        while not self.thread_stop:
            try:
                item = self.queue.get(block=True, timeout=30)
                print item
            except Empty:
                print("Nothing to do!read thread exit!")
                self.thread_stop=True
                break

            time.sleep(0.1)
            try:
                df_h_data = ts.get_h_data(item['code'], start=item['startdate'], retry_count=10, pause=0.01)
                if df_h_data is not None and len(df_h_data)>0:
                    df_h_data['secucode'] = item['code']
                    df_h_data.index.name = 'date'
                    print df_h_data.index,item['code'],item['startdate']
                    df_h_data['tradeday'] = df_h_data.index.strftime('%Y-%m-%d')
                    self.out_queue.put(df_h_data)
            except Exception, e:
                print str(e)+':'+item['code']
                self.queue.put(item)# 将没有爬取成功的数据放回队列里面去，以便下次重试。
                time.sleep(5)
                continue

            self.queue.task_done()
class ThreadWrite(threading.Thread):
    def __init__(self, queue, lock, db_engine):
        '''
        :param queue: 某种形式的任务队列，此处为tushare为每个股票返回的最新日复权行情数据
        :param lock:  暂时用连接互斥操作，防止mysql高并发，后续可尝试去掉
        :param db_engine:  mysql数据库的连接对象
        :return:no
        '''
        threading.Thread.__init__(self)

        self.queue = queue
        self.lock = lock
        self.db_engine = db_engine
        self.thread_stop= False
    def run(self):
        while not self.thread_stop:
            try:
                item = self.queue.get(block=True, timeout=60)
            except Empty:
                print("Nothing to do!write thread exit!")
                self.thread_stop=True
                break
            self._save_data(item)
            self.queue.task_done()

    def _save_data(self, item):
        try:
            item.to_sql('cron_dailyquote', self.db_engine, if_exists='append', index=False)
        except Exception, e:  # 如果是新股，则有可能df_h_data是空对象，因此需要跳过此类情况不处理
            print str(e)+ 'write error'
#crawlDailyQuote()

def stock_strategy_1():
    '''
    获取当前工作日成交量创2个月新低的股票，
    俗话说地量见地价，直接到存到一张结果表当中
    :return:
    '''
    pass

def stock_strategy_2():
    '''
    获取成交量为近2个月平均成交量2位以上，但涨幅为0%-2%的股票清单
    :return:
    '''
    #TODO 获取成交量为近2个月平均成交量2位以上，但涨幅为0%-2%的股票清单
    pass


