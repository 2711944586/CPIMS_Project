# 商品信息管理系统 (CPIMS)

基于Flask开发的商品信息管理系统，包含商品管理、销售查询、浏览记录等功能。

## 功能特性

- **系统封面** - 显示系统信息和开发者信息
- **统计大屏** - 销售数据统计、图表展示、库存预警
- **商品管理** - 添加、编辑、删除商品
- **销售查询** - 按商品名称查询销售记录
- **浏览记录** - 按用户名和日期查询

## 数据库设计

- **products** - 商品表（150条记录）
- **users** - 用户表（100条记录）
- **browse_logs** - 浏览表（1000条记录）
- **sales** - 销售表（600条记录）

总数据量：**1850条记录**

## 技术栈

- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Bootstrap 5.3.0
- Chart.js 4.4.0
- Faker 20.1.0
- Gunicorn 21.2.0

## 快速开始

### 1. 修改个人信息

编辑 `app/templates/cover.html`，修改姓名、学号、班级

### 2. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用（Windows）
start.bat

# 或手动启动
python run.py
```

访问 http://localhost:5000

### 3. 部署到Railway

```bash
# 初始化Git
git init
git add .
git commit -m "Initial commit"
git branch -M main

# 推送到GitHub
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

然后在 https://railway.app 选择 "Deploy from GitHub repo"

详细部署说明见 [DEPLOYMENT.md](DEPLOYMENT.md)

## 项目结构

```
CPIMS_Project/
├── app/
│   ├── __init__.py          # Flask应用
│   ├── models.py            # 数据库模型
│   ├── routes.py            # 路由视图
│   ├── seed.py              # 数据生成
│   ├── static/              # 静态资源
│   └── templates/           # HTML模板
├── config.py                # 配置文件
├── run.py                   # 启动入口
├── requirements.txt         # 依赖列表
├── Procfile                 # Railway配置
└── README.md                # 项目文档
```

## 开发信息

- 开发时间：2025年12月
- 技术栈：Flask + SQLAlchemy + Bootstrap 5
- 数据库：SQLite（开发）/ PostgreSQL（生产）

## 许可证

MIT License
