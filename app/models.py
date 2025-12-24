from . import db
from datetime import datetime

# 1. 商品信息表 (Products)
# 需求：编号、名称、登记日期、品类、型号、单位、单价、剩余数量
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True) # 商品编号
    name = db.Column(db.String(100), nullable=False) # 商品名称
    reg_date = db.Column(db.Date, default=datetime.now) # 登记日期
    category = db.Column(db.String(50)) # 品类
    model = db.Column(db.String(50)) # 型号
    unit = db.Column(db.String(10)) # 计量单位
    price = db.Column(db.Numeric(10, 2), nullable=False) # 单价
    stock = db.Column(db.Integer, default=0) # 剩余数量
    
    # 关联
    logs = db.relationship('BrowseLog', backref='product', cascade="all, delete-orphan")
    sales = db.relationship('Sale', backref='product', cascade="all, delete-orphan")

# 2. 用户信息表 (Users)
# 需求：编号、用户名、收件地址、联系电话
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True) # 用户编号
    username = db.Column(db.String(50), nullable=False) # 用户名
    address = db.Column(db.String(200)) # 收件地址
    phone = db.Column(db.String(20)) # 联系电话
    
    # 关联 - 添加cascade删除配置
    logs = db.relationship('BrowseLog', backref='user', cascade="all, delete-orphan")
    sales = db.relationship('Sale', backref='user', cascade="all, delete-orphan")

# 3. 用户浏览信息表 (BrowseLogs)
# 需求：用户编号、商品编号、浏览时间、浏览方式
class BrowseLog(db.Model):
    __tablename__ = 'browse_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False) # 外键
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False) # 外键
    browse_time = db.Column(db.DateTime, default=datetime.now) # 浏览时间
    platform = db.Column(db.String(20)) # 浏览方式 (PC/APP)

# 4. 商品销售信息表 (Sales)
# 需求：商品编号、用户编号、销售日期、单价、数量、总金额、支付方式
class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False) # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False) # 外键
    sale_date = db.Column(db.Date, default=datetime.now) # 销售日期
    unit_price = db.Column(db.Numeric(10, 2), nullable=False) # 单价
    quantity = db.Column(db.Integer, nullable=False) # 数量
    total_amount = db.Column(db.Numeric(10, 2), nullable=False) # 总金额
    payment_method = db.Column(db.String(20)) # 支付方式