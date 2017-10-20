#encoding:utf8
'''
定义一些常用的工具函数：
1，md5加密
2，前推OFFSET天的日期
3，判断是否是一个有效的日期字符串
4，继承将数据全部转换大写，用于将返回值统一转成大写
'''
__author__ = 'xuyuming'

from flask_restful import Resource, fields, marshal_with
import hashlib
import time
import datetime



###############################################定义通用函数######################################################
# 1 用于后续用户名和密码的校验，客户端与服务端同时加密，实现密码的校验
def getMd5(src):
    '''
    将指定的字符串加密得到相应的MD5加密码串
    '''
    m2 = hashlib.md5()
    m2.update(src)
    return m2.hexdigest()
def getLastNdate(baseDateStr, offset):
    '''
    获取前推OFFSET天的日期
    :param offset:
    :return:
    '''
    baseDate = datetime.datetime.strptime(baseDateStr, '%Y-%m-%d')
    # 得到开始日期
    startday = baseDate + datetime.timedelta(days=offset)
    return datetime.datetime.strftime(startday, '%Y-%m-%d')
#TODO 此处增加邮件发送支持 建议使用Flask-Mail
############################################自定义输入字段########################################################
def is_valid_date(value,name):
  '''
  判断是否是一个有效的日期字符串
  '''
  try:
    time.strptime(value, "%Y-%m-%d")
    return value
  except:
    raise ValueError(u"parameter '{}' is not dateformat(YYYY-MM-DD). your param value is : {}".format(name, value))
############################################继承fields.Raw，实现输入字段格式自定义###############################
class AllCapsString(fields.Raw):
    '''
    继承将数据全部转换大写，用于将返回值统一转成大写
    '''
    def format(self, value):
        return value.upper()



##########################################跨操作系统文件加锁的问题################################################
import os
import multiprocessing

if os.name == 'nt':
    import win32con, win32file, pywintypes
    LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
    LOCK_SH = 0 # The default value
    LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
    __overlapped = pywintypes.OVERLAPPED(  )

    def lock(file, flags):
        hfile = win32file._get_osfhandle(file.fileno(  ))
        win32file.LockFileEx(hfile, flags, 0, 0xffff0000, __overlapped)

    def unlock(file):
        hfile = win32file._get_osfhandle(file.fileno(  ))
        win32file.UnlockFileEx(hfile, 0, 0xffff0000, __overlapped)
elif os.name == 'posix':
    from fcntl import LOCK_EX, LOCK_SH, LOCK_NB

    def lock(file, flags):
        fcntl.flock(file.fileno(  ), flags)

    def unlock(file):
        fcntl.flock(file.fileno(  ), fcntl.LOCK_UN)
else:
    raise RuntimeError("File Locker only support NT and Posix platforms!")

