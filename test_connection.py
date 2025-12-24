"""
测试 PostgreSQL 连接
"""
import os
import psycopg2

# 从环境变量获取连接信息
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:uuYxhqwGZugqVqYrLlOdxmrPHpayIXPQ@yamabiko.proxy.rlwy.net:31771/railway')

# 修复 postgres:// 为 postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"尝试连接到: {DATABASE_URL[:30]}...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 测试查询
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM products")
    product_count = cur.fetchone()[0]
    
    print(f"✅ 连接成功！")
    print(f"   用户数: {user_count}")
    print(f"   商品数: {product_count}")
    
    conn.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
