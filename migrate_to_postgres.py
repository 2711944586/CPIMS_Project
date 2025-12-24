"""
数据迁移脚本：从本地 SQLite 迁移到 Railway PostgreSQL
"""
import os
import sys

# PostgreSQL 连接信息
POSTGRES_URL = "postgresql://postgres:uuYxhqwGZugqVqYrLlOdxmrPHpayIXPQ@yamabiko.proxy.rlwy.net:31771/railway"

# 本地 SQLite 数据库路径
SQLITE_URL = "sqlite:///instance/cpims.db"

def migrate_data():
    """执行数据迁移"""
    print("=" * 70)
    print("🚀 开始数据迁移：SQLite → PostgreSQL")
    print("=" * 70)
    print()
    
    # 检查本地数据库是否存在
    if not os.path.exists("instance/cpims.db"):
        print("❌ 错误：本地数据库文件不存在！")
        print("   路径：instance/cpims.db")
        print()
        print("💡 解决方法：")
        print("   1. 先运行 python run.py 生成本地数据库")
        print("   2. 或者直接在云端生成数据（不需要迁移）")
        return False
    
    try:
        # 导入模型
        from app.models import User, Product, BrowseLog, Sale, db
        from app import create_app
        
        # 第一步：从 SQLite 读取数据
        print("📂 从本地 SQLite 读取数据...")
        sqlite_app = create_app()
        sqlite_app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URL
        
        users_data = []
        products_data = []
        logs_data = []
        sales_data = []
        
        with sqlite_app.app_context():
            # 读取用户
            users = User.query.all()
            for user in users:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'address': user.address,
                    'phone': user.phone
                })
            print(f"   读取了 {len(users_data)} 个用户")
            
            # 读取商品
            products = Product.query.all()
            for product in products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'reg_date': product.reg_date,
                    'category': product.category,
                    'model': product.model,
                    'unit': product.unit,
                    'price': product.price,
                    'stock': product.stock
                })
            print(f"   读取了 {len(products_data)} 个商品")
            
            # 读取浏览记录
            logs = BrowseLog.query.all()
            for log in logs:
                logs_data.append({
                    'id': log.id,
                    'user_id': log.user_id,
                    'product_id': log.product_id,
                    'browse_time': log.browse_time,
                    'platform': log.platform
                })
            print(f"   读取了 {len(logs_data)} 条浏览记录")
            
            # 读取销售记录
            sales = Sale.query.all()
            for sale in sales:
                sales_data.append({
                    'id': sale.id,
                    'product_id': sale.product_id,
                    'user_id': sale.user_id,
                    'sale_date': sale.sale_date,
                    'unit_price': sale.unit_price,
                    'quantity': sale.quantity,
                    'total_amount': sale.total_amount,
                    'payment_method': sale.payment_method
                })
            print(f"   读取了 {len(sales_data)} 条销售记录")
        
        print("✅ SQLite 数据读取完成")
        print()
        
        # 第二步：写入到 PostgreSQL
        print("🐘 连接到 Railway PostgreSQL 数据库...")
        postgres_app = create_app()
        postgres_app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL
        
        with postgres_app.app_context():
            print("✅ PostgreSQL 连接成功")
            print()
            
            # 创建表
            print("📋 在 PostgreSQL 中创建数据表...")
            db.create_all()
            print("✅ 数据表创建成功")
            print()
            
            # 清空现有数据
            print("🧹 清空 PostgreSQL 中的现有数据...")
            db.session.query(Sale).delete()
            db.session.query(BrowseLog).delete()
            db.session.query(Product).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("✅ 清空完成")
            print()
            
            # 写入用户数据
            print("👥 写入用户数据...")
            for user_data in users_data:
                user = User(**user_data)
                db.session.add(user)
            db.session.commit()
            print(f"✅ 写入了 {len(users_data)} 个用户")
            print()
            
            # 写入商品数据
            print("📦 写入商品数据...")
            for product_data in products_data:
                product = Product(**product_data)
                db.session.add(product)
            db.session.commit()
            print(f"✅ 写入了 {len(products_data)} 个商品")
            print()
            
            # 写入浏览记录
            print("👀 写入浏览记录...")
            for log_data in logs_data:
                log = BrowseLog(**log_data)
                db.session.add(log)
            db.session.commit()
            print(f"✅ 写入了 {len(logs_data)} 条浏览记录")
            print()
            
            # 写入销售记录
            print("💰 写入销售记录...")
            for sale_data in sales_data:
                sale = Sale(**sale_data)
                db.session.add(sale)
            db.session.commit()
            print(f"✅ 写入了 {len(sales_data)} 条销售记录")
            print()
            
            # 重置序列（PostgreSQL 需要）
            print("🔄 重置 PostgreSQL 序列...")
            try:
                from sqlalchemy import text
                if len(users_data) > 0:
                    db.session.execute(text(f"SELECT setval('user_id_seq', {max(u['id'] for u in users_data)}, true)"))
                if len(products_data) > 0:
                    db.session.execute(text(f"SELECT setval('product_id_seq', {max(p['id'] for p in products_data)}, true)"))
                if len(logs_data) > 0:
                    db.session.execute(text(f"SELECT setval('browse_log_id_seq', {max(l['id'] for l in logs_data)}, true)"))
                if len(sales_data) > 0:
                    db.session.execute(text(f"SELECT setval('sale_id_seq', {max(s['id'] for s in sales_data)}, true)"))
                db.session.commit()
                print("✅ 序列重置完成")
            except Exception as e:
                print(f"⚠️  序列重置跳过（可能不需要）: {str(e)}")
            print()
        
        user_count = len(users_data)
        product_count = len(products_data)
        log_count = len(logs_data)
        sale_count = len(sales_data)
        
        # 显示迁移摘要
        print("=" * 70)
        print("🎉 数据迁移完成！")
        print("=" * 70)
        print()
        print("📊 迁移摘要：")
        print(f"   ✅ 用户：{user_count} 条")
        print(f"   ✅ 商品：{product_count} 条")
        print(f"   ✅ 浏览记录：{log_count} 条")
        print(f"   ✅ 销售记录：{sale_count} 条")
        print(f"   ✅ 总计：{user_count + product_count + log_count + sale_count} 条数据")
        print()
        print("🌐 下一步：")
        print("   1. 访问你的 Railway 网站")
        print("   2. 查看数据是否正确显示")
        print("   3. 测试增删查改功能")
        print()
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ 迁移失败！")
        print("=" * 70)
        print()
        print(f"错误信息：{str(e)}")
        print()
        print("💡 常见问题解决：")
        print()
        print("1. 连接被拒绝：")
        print("   - 检查 PostgreSQL 连接信息是否正确")
        print("   - 确认 Railway 数据库正在运行")
        print("   - 检查网络连接")
        print()
        print("2. 表已存在：")
        print("   - 脚本会自动清空现有数据")
        print("   - 如果还有问题，在 Railway 删除并重新创建数据库")
        print()
        print("3. 权限错误：")
        print("   - 确认数据库用户有写入权限")
        print("   - 检查连接字符串是否正确")
        print()
        return False

if __name__ == '__main__':
    print()
    print("⚠️  重要提示：")
    print("   - 此操作会清空 PostgreSQL 中的现有数据")
    print("   - 请确保已备份重要数据")
    print("   - 迁移过程可能需要几分钟")
    print()
    
    response = input("确认开始迁移？(输入 yes 继续): ")
    
    if response.lower() == 'yes':
        print()
        success = migrate_data()
        sys.exit(0 if success else 1)
    else:
        print()
        print("❌ 迁移已取消")
        sys.exit(0)
