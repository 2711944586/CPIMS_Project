from app import create_app, db
from app.seed import seed_data
import sys

app = create_app()

@app.cli.command()
def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")

@app.cli.command()
def seed():
    """填充测试数据"""
    with app.app_context():
        seed_data()

if __name__ == '__main__':
    # 自动初始化数据库
    with app.app_context():
        db.create_all()
        
        # 检查是否需要填充数据
        from app.models import Product
        if Product.query.count() == 0:
            print("检测到空数据库，开始填充数据...")
            seed_data()
    
    # 启动应用
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port, debug=True)