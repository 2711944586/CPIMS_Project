"""
修复版数据迁移脚本：从本地 SQLite 迁移到 Railway PostgreSQL
确保数据正确写入 PostgreSQL
"""
import os
import sys

# PostgreSQL 连接信息
POSTGRES_URL = "postgresql://postgres:uuYxhqwGZugqVqYrLlOdxmrPHpayIXPQ@yamabiko.proxy.rlwy.net:31771/railway"

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
        return False
    
    try:
        # 第一步：从 SQLite 读取所有数据
        print("📂 步骤 1/3：从本地 SQLite 读取数据...")
        
        from app import create_app
        from app.models import db, User, Product, BrowseLog, Sale
        
        # 创建 SQLite 应用实例
        sqlite_app = create_app()
        sqlite_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/cpims.db'
        
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
                    'price': float(product.price),
                    'stock': product.stock
                })
            
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
            
            # 读取销售记录
            sales = Sale.query.all()
            for sale in sales:
                sales_data.append({
                    'id': sale.id,
                    'product_id': sale.product_id,
                    'user_id': sale.user_id,
                    'sale_date': sale.sale_date,
                    'unit_price': float(sale.unit_price),
                    'quantity': sale.quantity,
                    'total_amount': float(sale.total_amount),
                    'payment_method': sale.payment_method
                })
        
        print(f"   ✅ 用户：{len(users_data)} 条")
        print(f"   ✅ 商品：{len(products_data)} 条")
        print(f"   ✅ 浏览记录：{len(logs_data)} 条")
        print(f"   ✅ 销售记录：{len(sales_data)} 条")
        print()
        
        # 第二步：连接到 PostgreSQL 并创建表
        print("🐘 步骤 2/3：连接到 PostgreSQL 并创建表...")
        
        # 创建 PostgreSQL 应用实例
        postgres_app = create_app()
        postgres_app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL
        postgres_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
        
        with postgres_app.app_context():
            # 测试连接
            try:
                db.engine.connect()
                print("   ✅ PostgreSQL 连接成功")
            except Exception as e:
                print(f"   ❌ PostgreSQL 连接失败：{str(e)}")
                return False
            
            # 删除所有表（如果存在）
            print("   🗑️  删除旧表...")
            db.drop_all()
            
            # 创建所有表
            print("   📋 创建新表...")
            db.create_all()
            print("   ✅ 表创建成功")
            print()
            
            # 第三步：写入数据到 PostgreSQL
            print("💾 步骤 3/3：写入数据到 PostgreSQL...")
            
            # 写入用户
            print("   👥 写入用户...")
            for user_data in users_data:
                user = User(**user_data)
                db.session.add(user)
            db.session.commit()
            print(f"   ✅ 已写入 {len(users_data)} 个用户")
            
            # 写入商品
            print("   📦 写入商品...")
            for product_data in products_data:
                product = Product(**product_data)
                db.session.add(product)
            db.session.commit()
            print(f"   ✅ 已写入 {len(products_data)} 个商品")
            
            # 写入浏览记录
            print("   👀 写入浏览记录...")
            batch_size = 100
            for i in range(0, len(logs_data), batch_size):
                batch = logs_data[i:i+batch_size]
                for log_data in batch:
                    log = BrowseLog(**log_data)
                    db.session.add(log)
                db.session.commit()
                print(f"      进度：{min(i+batch_size, len(logs_data))}/{len(logs_data)}")
            print(f"   ✅ 已写入 {len(logs_data)} 条浏览记录")
            
            # 写入销售记录
            print("   💰 写入销售记录...")
            for i in range(0, len(sales_data), batch_size):
                batch = sales_data[i:i+batch_size]
                for sale_data in batch:
                    sale = Sale(**sale_data)
                    db.session.add(sale)
                db.session.commit()
                print(f"      进度：{min(i+batch_size, len(sales_data))}/{len(sales_data)}")
            print(f"   ✅ 已写入 {len(sales_data)} 条销售记录")
            print()
            
            # 验证数据
            print("🔍 验证数据...")
            user_count = User.query.count()
            product_count = Product.query.count()
            log_count = BrowseLog.query.count()
            sale_count = Sale.query.count()
            
            print(f"   PostgreSQL 中的数据：")
            print(f"   - 用户：{user_count} 条")
            print(f"   - 商品：{product_count} 条")
            print(f"   - 浏览记录：{log_count} 条")
            print(f"   - 销售记录：{sale_count} 条")
            print()
            
            if (user_count == len(users_data) and 
                product_count == len(products_data) and 
                log_count == len(logs_data) and 
                sale_count == len(sales_data)):
                print("   ✅ 数据验证通过！所有数据已正确写入")
            else:
                print("   ⚠️  警告：数据数量不匹配")
                return False
        
        # 显示迁移摘要
        print()
        print("=" * 70)
        print("🎉 数据迁移完成！")
        print("=" * 70)
        print()
        print("📊 迁移摘要：")
        print(f"   ✅ 用户：{len(users_data)} 条")
        print(f"   ✅ 商品：{len(products_data)} 条")
        print(f"   ✅ 浏览记录：{len(logs_data)} 条")
        print(f"   ✅ 销售记录：{len(sales_data)} 条")
        print(f"   ✅ 总计：{len(users_data) + len(products_data) + len(logs_data) + len(sales_data)} 条数据")
        print()
        print("🌐 验证步骤：")
        print("   1. 登录 Railway 控制台")
        print("   2. 进入 Postgres 服务")
        print("   3. 点击 'Data' 标签")
        print("   4. 查看各个表的数据")
        print()
        print("   或者访问你的网站查看数据是否显示")
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
        import traceback
        print("详细错误：")
        traceback.print_exc()
        print()
        return False

if __name__ == '__main__':
    print()
    print("⚠️  重要提示：")
    print("   - 此操作会删除 PostgreSQL 中的所有现有数据")
    print("   - 然后重新创建表并导入数据")
    print("   - 请确保已备份重要数据")
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
