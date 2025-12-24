from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 打印数据库连接信息（隐藏密码）
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'postgresql' in db_uri:
        logger.info("使用 PostgreSQL 数据库")
    else:
        logger.info("使用 SQLite 数据库")
    
    try:
        db.init_app(app)
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

    # 注册蓝图
    from .routes import main
    app.register_blueprint(main)
    
    # 添加错误处理
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return f"Internal Server Error: {error}", 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return f"Error: {str(e)}", 500

    return app
