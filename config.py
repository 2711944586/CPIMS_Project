import os

class Config:
    # 数据库连接配置
    database_url = os.environ.get('DATABASE_URL')
    
    # 修复 Railway 的 postgres:// 为 postgresql://
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # 本地开发使用 SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///cpims.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
