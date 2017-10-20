#encoding:utf8
'''
'''
__author__ = 'xuyuming'
#encoding:utf8
'''
'''
__author__ = 'xuyuming'
from app import db
class lianjiasale(db.Model):
    __tablename__ = 'lianjiasale'
    #id = db.Column(db.Integer, primary_key=True) #代理主键
    acreage = db.Column(db.String(16), nullable=False)
    cityCode = db.Column(db.String(6), nullable=False)
    dealAvgPrice = db.Column(db.String(16), nullable=False)
    districtName = db.Column(db.String(64), nullable=False)
    face = db.Column(db.String(16), nullable=False)
    floor_state = 	db.Column(db.String(64), nullable=False)
    hall = 	db.Column(db.String(6), nullable=False)
    houseSellId = db.Column(db.String(16), primary_key=True)# 唯一主键
    isRecommend = 	db.Column(db.String(6), nullable=False)
    label 	= 	db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.String(16), nullable=False)
    longitude = db.Column(db.String(16), nullable=False)
    metroRemark	= db.Column(db.String(64), nullable=False)
    plateName = db.Column(db.String(16), nullable=False)
    propertyName = db.Column(db.String(64), nullable=False)
    propertyNo = db.Column(db.String(16), nullable=False)
    referAvgPrice = db.Column(db.String(16), nullable=False)
    room = db.Column(db.String(6), nullable=False)
    showPrice = db.Column(db.String(16), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    unitPrice = db.Column(db.String(16), nullable=False)
    insertdate 	=	db.Column(db.String(10), nullable=False)
    def __repr__(self):
        return '<lianjiasale %r>' % self.houseSellId
