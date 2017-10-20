#encoding:utf8
'''
'''
__author__ = 'xuyuming'
from app import db

class SalePriceChg(db.Model):
    __tablename__ = 'lianjiasalepricechg'
    id = db.Column(db.Integer, primary_key=True) #代理主键
    houseSellId = db.Column(db.String(16), nullable=False)# 唯一主键
    oldshowPrice = db.Column(db.String(16), nullable=False) #原挂牌价
    oldunitPrice = db.Column(db.String(16), nullable=False) #原单价
    newshowPrice = db.Column(db.String(16), nullable=False) #新挂牌价
    newunitPrice = db.Column(db.String(16), nullable=False) #新单价
    priceChg = db.Column(db.String(16), nullable=False) #新单价
    insertdate 	= db.Column(db.String(10), nullable=False)
    def __repr__(self):
        return '<lianjiasalepricechg %r>' % self.houseSellId
