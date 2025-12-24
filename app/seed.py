from faker import Faker
from datetime import datetime, timedelta
import random
from . import db
from .models import Product, User, BrowseLog, Sale

fake = Faker('zh_CN')

def seed_data():
    """生成大量测试数据（500+条记录）"""
    
    # 清空现有数据
    db.session.query(Sale).delete()
    db.session.query(BrowseLog).delete()
    db.session.query(Product).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    print("开始生成数据...")
    
    # 1. 生成100个用户
    users = []
    for i in range(100):
        user = User(
            username=fake.name(),
            address=fake.address(),
            phone=fake.phone_number()
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()
    print(f"✓ 已生成 {len(users)} 个用户")
    
    # 2. 生成150个商品
    categories = ['电子产品', '家居用品', '服装鞋帽', '食品饮料', '图书文具', '运动户外', '美妆个护', '母婴玩具']
    units = ['件', '台', '个', '套', '盒', '瓶', '本', '双']
    
    products = []
    for i in range(150):
        category = random.choice(categories)
        product = Product(
            name=fake.word() + random.choice(['手机', '电脑', '耳机', '沙发', '衣服', '零食', '书籍', '球鞋'][:8]),
            reg_date=fake.date_between(start_date='-2y', end_date='today'),
            category=category,
            model=f"{random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])}{random.randint(100, 999)}",
            unit=random.choice(units),
            price=round(random.uniform(10, 5000), 2),
            stock=random.randint(0, 500)
        )
        products.append(product)
    db.session.add_all(products)
    db.session.commit()
    print(f"✓ 已生成 {len(products)} 个商品")
    
    # 3. 生成1000条浏览记录
    browse_logs = []
    platforms = ['PC', 'APP', '移动端', '小程序']
    for i in range(1000):
        log = BrowseLog(
            user_id=random.choice(users).id,
            product_id=random.choice(products).id,
            browse_time=fake.date_time_between(start_date='-1y', end_date='now'),
            platform=random.choice(platforms)
        )
        browse_logs.append(log)
    db.session.add_all(browse_logs)
    db.session.commit()
    print(f"✓ 已生成 {len(browse_logs)} 条浏览记录")
    
    # 4. 生成600条销售记录
    payment_methods = ['支付宝', '微信支付', '银行卡', '货到付款', '信用卡']
    sales = []
    for i in range(600):
        product = random.choice(products)
        quantity = random.randint(1, 10)
        unit_price = float(product.price)
        total = round(unit_price * quantity, 2)
        
        sale = Sale(
            product_id=product.id,
            user_id=random.choice(users).id,
            sale_date=fake.date_between(start_date='-1y', end_date='today'),
            unit_price=unit_price,
            quantity=quantity,
            total_amount=total,
            payment_method=random.choice(payment_methods)
        )
        sales.append(sale)
    db.session.add_all(sales)
    db.session.commit()
    print(f"✓ 已生成 {len(sales)} 条销售记录")
    
    print(f"\n数据生成完成！")
    print(f"总计: {len(users)} 用户, {len(products)} 商品, {len(browse_logs)} 浏览记录, {len(sales)} 销售记录")
    print(f"数据总量: {len(users) + len(products) + len(browse_logs) + len(sales)} 条")
