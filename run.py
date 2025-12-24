from app import create_app, db
from app.seed import seed_data
import os

app = create_app()

# 在应用上下文中初始化数据库
with app.app_context():
    db.create_all()
    
    # 检查是否需要填充数据（仅当数据库为空时）
    from app.models import Product
    if Product.query.count() == 0:
        print("检测到空数据库，开始填充数据...")
        seed_data()
        print("数据填充完成！")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
