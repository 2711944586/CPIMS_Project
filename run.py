import os
from app import create_app, db
from app.seed import seed_data

app = create_app()

# 只在应用启动时初始化数据库（不在导入时）
def init_database():
    with app.app_context():
        try:
            db.create_all()
            # 检查是否需要填充数据
            from app.models import Product
            if Product.query.count() == 0:
                print("检测到空数据库，开始填充数据...")
                seed_data()
                print("数据填充完成！")
        except Exception as e:
            print(f"数据库初始化错误: {e}")

# 仅在直接运行时初始化
if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
