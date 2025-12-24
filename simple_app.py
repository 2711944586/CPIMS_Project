"""
简化版应用 - 用于测试 Railway 部署
"""
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    db_url = os.environ.get('DATABASE_URL', 'Not set')
    return f"""
    <h1>CPIMS 测试页面</h1>
    <p>应用正在运行！</p>
    <p>DATABASE_URL: {db_url[:50]}...</p>
    <p><a href="/test_db">测试数据库连接</a></p>
    """

@app.route('/test_db')
def test_db():
    try:
        import psycopg2
        DATABASE_URL = os.environ.get('DATABASE_URL')
        
        if not DATABASE_URL:
            return "❌ DATABASE_URL 未设置"
        
        # 修复 URL
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM products")
        product_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM browse_logs")
        log_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM sales")
        sale_count = cur.fetchone()[0]
        
        conn.close()
        
        return f"""
        <h1>✅ 数据库连接成功！</h1>
        <ul>
            <li>用户: {user_count}</li>
            <li>商品: {product_count}</li>
            <li>浏览记录: {log_count}</li>
            <li>销售记录: {sale_count}</li>
        </ul>
        <p><a href="/">返回首页</a></p>
        """
    except Exception as e:
        return f"❌ 数据库连接失败: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
