#encoding:utf8
'''
如何正确理解yield关键字的行为
'''
__author__ = 'xuyuming'
def createGenerator():
    mylist = range(3)
    print u'this will be executed only when for ... in ..called only once'
    for i in mylist:
        print 'test3'
        yield i*i
    print 'test2'
mygenerator = createGenerator()
print 'test'
for i in mygenerator:
    print(i)
