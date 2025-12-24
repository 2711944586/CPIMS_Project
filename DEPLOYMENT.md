# Railway 部署指南

## 📋 部署前准备

本项目支持：
- ✅ **本地开发**：使用 SQLite 数据库
- ✅ **云端部署**：使用 PostgreSQL 数据库（Railway 提供）
- ✅ **数据持久化**：云端数据不会丢失
- ✅ **完整功能**：增删查改功能完全可用

---

## 🚀 快速部署步骤

### 步骤 1：准备 GitHub 仓库

```bash
# 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit: CPIMS Project"
git branch -M main

# 推送到 GitHub（替换为你的仓库地址）
git remote add origin https://github.com/2711944586/CPIMS_Project.git
git push -u origin main
```

### 步骤 2：在 Railway 部署

1. **访问 Railway**
   - 打开 https://railway.app
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的 CPIMS_Project 仓库

3. **添加 PostgreSQL 数据库**
   - 在项目中点击 "New"
   - 选择 "Database"
   - 选择 "Add PostgreSQL"
   - Railway 会自动创建数据库并设置 `DATABASE_URL` 环境变量

4. **等待部署完成**
   - Railway 会自动检测 Python 项目
   - 自动安装依赖（requirements.txt）
   - 自动运行启动命令（Procfile）
   - 首次启动会自动创建表并填充 1850+ 条数据

5. **获取访问地址**
   - 点击项目中的 "Settings"
   - 在 "Domains" 部分点击 "Generate Domain"
   - 获得类似 `https://你的项目.up.railway.app` 的地址

---

## 💾 关于数据库

### 本地开发（SQLite）
- 数据存储在 `instance/cpims.db`
- 适合开发和测试
- 数据在本地文件中

### 云端部署（PostgreSQL）
- Railway 自动提供 PostgreSQL 数据库
- **数据持久化**：重启不会丢失
- **完全支持增删查改**：所有功能正常工作
- 自动初始化 1850+ 条测试数据

### 数据迁移说明

**重要**：本地 SQLite 数据无法直接上传到云端 PostgreSQL。

如果需要迁移本地数据到云端：

#### 方法 1：手动导出导入（推荐用于少量数据）
1. 在本地导出数据为 CSV 或 JSON
2. 部署后通过管理界面手动添加

#### 方法 2：使用数据库迁移工具（推荐用于大量数据）
```bash
# 安装 pgloader（需要先安装 PostgreSQL 客户端）
# 然后使用 pgloader 迁移
pgloader sqlite://instance/cpims.db postgresql://用户名:密码@主机:端口/数据库名
```

#### 方法 3：修改 seed.py 使用真实数据（最简单）
如果你想在云端使用特定数据：
1. 修改 `app/seed.py` 文件
2. 将 Faker 生成的随机数据改为你的真实数据
3. 重新部署，系统会自动填充

---

## 🔧 环境变量配置（可选）

在 Railway 项目设置中可以添加：

| 变量名 | 说明 | 是否必需 |
|--------|------|---------|
| `DATABASE_URL` | PostgreSQL 连接 | 自动设置 |
| `SECRET_KEY` | Flask 密钥 | 建议设置 |

设置 SECRET_KEY：
```
SECRET_KEY=你的随机密钥字符串
```

---

## 🧪 本地测试

### Windows
```bash
start.bat
```

### 手动运行
```bash
python run.py
```

访问 http://localhost:5000

### 重新初始化数据库
```bash
# 删除现有数据库
del instance\cpims.db

# 重新运行（会自动创建并填充数据）
python run.py
```

---

## ✅ 部署后验证

1. **访问封面页**
   - 打开你的 Railway 域名
   - 应该看到系统封面页

2. **测试数据大屏**
   - 点击"进入系统"
   - 查看统计数据和图表

3. **测试增删查改**
   - 进入"商品管理"
   - 尝试添加新商品
   - 尝试编辑商品
   - 尝试删除商品
   - 刷新页面确认数据已保存

4. **测试查询功能**
   - 进入"销售查询"
   - 输入商品名称查询
   - 进入"浏览记录"
   - 按用户名和日期查询

---

## 📊 数据说明

系统自动生成的测试数据：
- **100 个用户**：随机姓名、地址、电话
- **150 个商品**：8 个品类，随机价格和库存
- **1000 条浏览记录**：随机时间、平台
- **600 条销售记录**：随机订单、支付方式

**所有数据在云端都是持久化的**，你可以：
- ✅ 添加新商品
- ✅ 编辑商品信息
- ✅ 删除商品
- ✅ 查询销售记录
- ✅ 查询浏览记录
- ✅ 数据在重启后保留

---

## 🔄 更新部署

```bash
# 修改代码后
git add .
git commit -m "更新说明"
git push

# Railway 会自动检测并重新部署
```

---

## ❓ 常见问题

### Q: 部署后看不到数据？
**A**: 检查部署日志，确保数据库初始化成功。可以在 Railway 控制台查看日志。

### Q: 添加商品后刷新页面数据消失？
**A**: 确保已添加 PostgreSQL 数据库。如果只部署了应用没有数据库，数据会在重启时丢失。

### Q: 如何查看数据库内容？
**A**: 
1. 在 Railway 项目中点击 PostgreSQL 服务
2. 点击 "Data" 标签查看表内容
3. 或使用 "Connect" 获取连接信息，用 pgAdmin 等工具连接

### Q: 如何清空数据重新开始？
**A**: 
1. 在 Railway 删除 PostgreSQL 服务
2. 重新添加 PostgreSQL
3. 重新部署应用（会自动填充新数据）

### Q: 本地数据能上传到云端吗？
**A**: SQLite 和 PostgreSQL 是不同的数据库系统，不能直接上传文件。建议：
- 使用自动生成的测试数据
- 或部署后手动添加真实数据
- 或使用数据库迁移工具（pgloader）

### Q: 增删查改功能在云端能用吗？
**A**: ✅ **完全可以！** 只要添加了 PostgreSQL 数据库，所有功能都正常工作，数据会持久化保存。

---

## 📞 技术支持

如遇到问题：
1. 查看 Railway 部署日志
2. 检查是否添加了 PostgreSQL 数据库
3. 确认 `DATABASE_URL` 环境变量已自动设置
4. 查看浏览器控制台是否有错误

---

## 🎉 部署成功！

部署完成后，你将拥有：
- 🌐 一个公开访问的网站
- 💾 持久化的 PostgreSQL 数据库
- 📊 1850+ 条测试数据
- ✨ 完整的增删查改功能
- 📈 实时数据分析大屏
- 🎨 现代化的用户界面

享受你的商品信息管理系统吧！
