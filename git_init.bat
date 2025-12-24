@echo off
echo ========================================
echo   Git 仓库初始化
echo ========================================
echo.

echo [1/5] 初始化Git仓库...
git init

echo.
echo [2/5] 添加所有文件...
git add .

echo.
echo [3/5] 创建首次提交...
git commit -m "Initial commit: 商品信息管理系统 - 完整功能实现"

echo.
echo [4/5] 设置主分支为main...
git branch -M main

echo.
echo [5/5] 完成！
echo.
echo ========================================
echo   下一步操作：
echo ========================================
echo.
echo 1. 在GitHub创建新仓库
echo 2. 运行以下命令连接远程仓库：
echo    git remote add origin https://github.com/你的用户名/仓库名.git
echo    git push -u origin main
echo.
echo 3. 然后在Railway部署：
echo    - 访问 https://railway.app
echo    - 选择 "Deploy from GitHub repo"
echo    - 选择你的仓库
echo.
pause
