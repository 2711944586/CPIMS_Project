import os

class Config:
    # 数据库连接配置 - 支持Railway部署
    # Railway会自动提供DATABASE_URL环境变量（PostgreSQL）
    database_url = os.environ.get('DATABASE_URL')
    
    # 修复Railway的postgres://为postgresql://
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///cpims.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_change_in_production'