"""
直接上传数据到 Railway PostgreSQL
使用 psycopg2 直接连接，不依赖 Flask
"""
import sqlite3
import psycopg2

# Railway PostgreSQL 连接信息
PG_HOST = "yamabiko.proxy.rlwy.net"
PG_PORT = 31771
PG_USER = "postgres"
PG_PASSWORD = "uuYxhqwGZugqVqYrLlOdxmrPHpayIXPQ"
PG_DATABASE = "railway"

# 本地 SQLite 路径
SQLITE_PATH = "instance/cpims.db"

def main():
    print("=" * 60)
    print("🚀 直接上传数据到 Railway PostgreSQL")
    print("=" * 60)
    print()
    
    # 1. 连接 SQLite
    print("📂 连接本地 SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()
    print("✅ SQLite 连接成功")
    print()
    
    # 2. 连接 PostgreSQL
    print("🐘 连接 Railway PostgreSQL...")
    try:
        pg_conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            database=PG_DATABASE
        )
        pg_conn.autocommit = False
        pg_cur = pg_conn.cursor()
        print("✅ PostgreSQL 连接成功")
    except Exception as e:
        print(f"❌ PostgreSQL 连接失败: {e}")
        return
    print()
    
    # 3. 创建表 (使用复数表名匹配 Flask-SQLAlchemy)
    print("📋 创建数据表...")
    
    create_tables_sql = """
    DROP TABLE IF EXISTS sales CASCADE;
    DROP TABLE IF EXISTS browse_logs CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        address VARCHAR(500),
        phone VARCHAR(50)
    );
    
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        reg_date DATE,
        category VARCHAR(100),
        model VARCHAR(100),
        unit VARCHAR(50),
        price DECIMAL(10,2) NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0
    );
    
    CREATE TABLE browse_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
        browse_time TIMESTAMP,
        platform VARCHAR(50)
    );
    
    CREATE TABLE sales (
        id SERIAL PRIMARY KEY,
        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        sale_date DATE,
        unit_price DECIMAL(10,2),
        quantity INTEGER,
        total_amount DECIMAL(12,2),
        payment_method VARCHAR(50)
    );
    """
    
    pg_cur.execute(create_tables_sql)
    pg_conn.commit()
    print("✅ 表创建成功")
    print()
    
    # 4. 迁移用户数据
    print("👥 上传用户数据...")
    sqlite_cur.execute("SELECT id, username, address, phone FROM users")
    users = sqlite_cur.fetchall()
    
    for user in users:
        pg_cur.execute(
            'INSERT INTO users (id, username, address, phone) VALUES (%s, %s, %s, %s)',
            (user['id'], user['username'], user['address'], user['phone'])
        )
    pg_conn.commit()
    print(f"✅ 上传了 {len(users)} 个用户")
    
    # 5. 迁移商品数据
    print("📦 上传商品数据...")
    sqlite_cur.execute("SELECT id, name, reg_date, category, model, unit, price, stock FROM products")
    products = sqlite_cur.fetchall()
    
    for p in products:
        pg_cur.execute(
            'INSERT INTO products (id, name, reg_date, category, model, unit, price, stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            (p['id'], p['name'], p['reg_date'], p['category'], p['model'], p['unit'], p['price'], p['stock'])
        )
    pg_conn.commit()
    print(f"✅ 上传了 {len(products)} 个商品")
    
    # 6. 迁移浏览记录
    print("👀 上传浏览记录...")
    sqlite_cur.execute("SELECT id, user_id, product_id, browse_time, platform FROM browse_logs")
    logs = sqlite_cur.fetchall()
    
    batch_size = 100
    for i in range(0, len(logs), batch_size):
        batch = logs[i:i+batch_size]
        for log in batch:
            pg_cur.execute(
                'INSERT INTO browse_logs (id, user_id, product_id, browse_time, platform) VALUES (%s, %s, %s, %s, %s)',
                (log['id'], log['user_id'], log['product_id'], log['browse_time'], log['platform'])
            )
        pg_conn.commit()
        print(f"   进度: {min(i+batch_size, len(logs))}/{len(logs)}")
    print(f"✅ 上传了 {len(logs)} 条浏览记录")
    
    # 7. 迁移销售记录
    print("💰 上传销售记录...")
    sqlite_cur.execute("SELECT id, product_id, user_id, sale_date, unit_price, quantity, total_amount, payment_method FROM sales")
    sales = sqlite_cur.fetchall()
    
    for i in range(0, len(sales), batch_size):
        batch = sales[i:i+batch_size]
        for s in batch:
            pg_cur.execute(
                'INSERT INTO sales (id, product_id, user_id, sale_date, unit_price, quantity, total_amount, payment_method) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (s['id'], s['product_id'], s['user_id'], s['sale_date'], s['unit_price'], s['quantity'], s['total_amount'], s['payment_method'])
            )
        pg_conn.commit()
        print(f"   进度: {min(i+batch_size, len(sales))}/{len(sales)}")
    print(f"✅ 上传了 {len(sales)} 条销售记录")
    print()
    
    # 8. 重置序列
    print("🔄 重置序列...")
    pg_cur.execute(f"SELECT setval('users_id_seq', {max(u['id'] for u in users)}, true)")
    pg_cur.execute(f"SELECT setval('products_id_seq', {max(p['id'] for p in products)}, true)")
    pg_cur.execute(f"SELECT setval('browse_logs_id_seq', {max(l['id'] for l in logs)}, true)")
    pg_cur.execute(f"SELECT setval('sales_id_seq', {max(s['id'] for s in sales)}, true)")
    pg_conn.commit()
    print("✅ 序列重置完成")
    print()
    
    # 9. 验证数据
    print("🔍 验证数据...")
    pg_cur.execute('SELECT COUNT(*) FROM users')
    user_count = pg_cur.fetchone()[0]
    pg_cur.execute('SELECT COUNT(*) FROM products')
    product_count = pg_cur.fetchone()[0]
    pg_cur.execute('SELECT COUNT(*) FROM browse_logs')
    log_count = pg_cur.fetchone()[0]
    pg_cur.execute('SELECT COUNT(*) FROM sales')
    sale_count = pg_cur.fetchone()[0]
    
    print(f"   用户: {user_count}")
    print(f"   商品: {product_count}")
    print(f"   浏览记录: {log_count}")
    print(f"   销售记录: {sale_count}")
    print()
    
    # 关闭连接
    sqlite_conn.close()
    pg_conn.close()
    
    print("=" * 60)
    print("🎉 数据上传完成！")
    print("=" * 60)
    print()
    print("现在去 Railway 控制台刷新 Database 页面查看数据")

if __name__ == '__main__':
    main()
