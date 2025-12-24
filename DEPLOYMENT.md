# Railway 部署指南

## 快速部署

### 方法一：GitHub部署（推荐）

1. **初始化Git仓库**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
```

2. **推送到GitHub**
```bash
# 在GitHub创建仓库后
git remote add origin https://github.com/2711944586/CPIMS_Project.git
git push -u origin main
```

3. **在Railway部署**
- 访问 https://railway.app
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择你的仓库
- 等待自动部署完成

### 方法二：Railway CLI部署

```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

## 配置说明

项目已包含所有必要配置：
- `Procfile`: 启动命令
- `runtime.txt`: Python版本
- `requirements.txt`: 依赖包

## 环境变量（可选）

- `DATABASE_URL`: 数据库连接（自动使用SQLite）
- `SECRET_KEY`: Flask密钥（建议设置）

## 本地测试

```bash
# Windows
start.bat

# 或手动运行
python run.py
```

访问 http://localhost:5000

## 常见问题

**Q: 部署失败？**
A: 检查部署日志，确保requirements.txt和Procfile正确

**Q: 数据丢失？**
A: SQLite数据在重启时会丢失，系统会自动重新生成

**Q: 如何更新？**
A: 推送代码到GitHub，Railway自动重新部署
