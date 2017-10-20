#encoding:utf8
'''
'''
__author__ = 'xuyuming'

from app import db
class lianjiadeal(db.Model):
    __tablename__ = 'lianjiadeal'
    #id = db.Column(db.Integer, primary_key=True) #代理主键
    chanxiang = db.Column(db.String(16), nullable=False, default=u'unkown')
    danjia = db.Column(db.String(16), nullable=False)
    huxing = db.Column(db.String(64), nullable=False)
    itemid = db.Column(db.String(64), nullable=False, primary_key=True)
    itemurl = db.Column(db.String(48), nullable=False)
    loucheng = db.Column(db.String(64) ,default=u'unkown')
    mianji = db.Column(db.String(16), nullable=False)
    pianqu = db.Column(db.String(64), nullable=False)
    quxian = db.Column(db.String(64), nullable=False)
    xiaoqu = db.Column(db.String(64), nullable=False)
    zongjia = db.Column(db.String(64), nullable=False)
    signdate = db.Column(db.String(10),default='')
    def __repr__(self):
        return '<lianjiadeal %r>' % self.itemid