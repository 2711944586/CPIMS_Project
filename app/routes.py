from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from datetime import datetime
from .models import db, Product, Sale, BrowseLog, User

main = Blueprint('main', __name__)

# --- 1. 系统封面窗体 (要求 II.1) ---
@main.route('/')
def cover():
    # 模拟 Autoexec 宏打开窗体
    return render_template('cover.html')

# --- 2. 系统导航/统计大屏 (要求 II.2 & II.4) ---
@main.route('/dashboard')
def dashboard():
    current_year = datetime.now().year
    
    # 统计数据：今年销售总金额、今年销售商品总数
    total_sales = db.session.query(func.sum(Sale.total_amount))\
        .filter(func.extract('year', Sale.sale_date) == current_year).scalar() or 0
    
    total_qty = db.session.query(func.sum(Sale.quantity))\
        .filter(func.extract('year', Sale.sale_date) == current_year).scalar() or 0
    
    # 新增统计：商品总数、用户总数
    total_products = Product.query.count()
    total_users = User.query.count()
    
    # 图表数据1：每日用户浏览次数分布直方图
    # PostgreSQL 和 SQLite 的日期处理
    if 'postgresql' in str(db.engine.url):
        # PostgreSQL: 使用 CAST 或 DATE()
        daily_logs = db.session.query(
            func.cast(BrowseLog.browse_time, db.Date).label('date'),
            func.count(BrowseLog.id).label('cnt')
        ).group_by(text('date')).order_by(text('date')).limit(30).all()
    else:
        # SQLite
        daily_logs = db.session.query(
            func.date(BrowseLog.browse_time).label('date'),
            func.count(BrowseLog.id).label('cnt')
        ).group_by('date').order_by('date').limit(30).all()
    
    chart_dates = [str(item.date) for item in daily_logs]
    chart_counts = [item.cnt for item in daily_logs]
    
    # 图表数据2：品类销售分布（饼图）
    category_sales = db.session.query(
        Product.category,
        func.sum(Sale.total_amount).label('amount')
    ).join(Sale).group_by(Product.category).all()
    
    category_labels = [item.category or '未分类' for item in category_sales]
    category_amounts = [float(item.amount) for item in category_sales]
    
    # 图表数据3：月度销售趋势（折线图）
    # PostgreSQL 使用 to_char，SQLite 使用 strftime
    from sqlalchemy import text
    if 'postgresql' in str(db.engine.url):
        # PostgreSQL
        monthly_sales = db.session.query(
            func.to_char(Sale.sale_date, 'YYYY-MM').label('month'),
            func.sum(Sale.total_amount).label('amount'),
            func.sum(Sale.quantity).label('qty')
        ).filter(func.extract('year', Sale.sale_date) == current_year)\
         .group_by(text('month')).order_by(text('month')).all()
    else:
        # SQLite
        monthly_sales = db.session.query(
            func.strftime('%Y-%m', Sale.sale_date).label('month'),
            func.sum(Sale.total_amount).label('amount'),
            func.sum(Sale.quantity).label('qty')
        ).filter(func.extract('year', Sale.sale_date) == current_year)\
         .group_by('month').order_by('month').all()
    
    month_labels = [item.month for item in monthly_sales]
    month_amounts = [float(item.amount) for item in monthly_sales]
    month_quantities = [item.qty for item in monthly_sales]
    
    # 图表数据4：热门商品TOP10
    top_products = db.session.query(
        Product.name,
        func.sum(Sale.quantity).label('total_qty'),
        func.sum(Sale.total_amount).label('total_amount')
    ).join(Sale).group_by(Product.id)\
     .order_by(func.sum(Sale.quantity).desc()).limit(10).all()
    
    top_product_names = [item.name for item in top_products]
    top_product_sales = [item.total_qty for item in top_products]
    
    # 预警检查：库存低于10件的商品数量
    low_stock_count = Product.query.filter(Product.stock < 10).count()
    
    # 平台浏览分布
    platform_stats = db.session.query(
        BrowseLog.platform,
        func.count(BrowseLog.id).label('cnt')
    ).group_by(BrowseLog.platform).all()
    
    platform_labels = [item.platform for item in platform_stats]
    platform_counts = [item.cnt for item in platform_stats]

    return render_template('dashboard.html',
                           total_sales=f"{total_sales:,.2f}",
                           total_qty=total_qty,
                           total_products=total_products,
                           total_users=total_users,
                           chart_dates=chart_dates,
                           chart_counts=chart_counts,
                           category_labels=category_labels,
                           category_amounts=category_amounts,
                           month_labels=month_labels,
                           month_amounts=month_amounts,
                           month_quantities=month_quantities,
                           top_product_names=top_product_names,
                           top_product_sales=top_product_sales,
                           platform_labels=platform_labels,
                           platform_counts=platform_counts,
                           low_stock_count=low_stock_count)

# --- 3. 商品管理 (数据编辑窗体) (要求 II.3 & 其它设计要求) ---
@main.route('/products')
def products_manage():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('products.html', products=products)

@main.route('/products/save', methods=['POST'])
def product_save():
    """
    实现"保存"按钮功能
    - 表单验证（必填字段、数据类型、价格>0、库存≥0）
    - 保存功能（创建和更新）
    - 显示成功/错误消息（Flash messages）
    """
    try:
        p_id = request.form.get('id')
        name = request.form.get('name', '').strip()
        reg_date_str = request.form.get('reg_date', '').strip()
        category = request.form.get('category', '').strip()
        model = request.form.get('model', '').strip()
        unit = request.form.get('unit', '').strip()
        price_str = request.form.get('price', '').strip()
        stock_str = request.form.get('stock', '').strip()
        
        # 验证必填字段
        if not name:
            flash('商品名称不能为空', 'error')
            return redirect(url_for('main.products_manage'))
        
        if not price_str:
            flash('单价不能为空', 'error')
            return redirect(url_for('main.products_manage'))
        
        if not stock_str:
            flash('库存不能为空', 'error')
            return redirect(url_for('main.products_manage'))
        
        # 验证数据类型和范围
        try:
            price = float(price_str)
            if price <= 0:
                flash('单价必须大于0', 'error')
                return redirect(url_for('main.products_manage'))
        except ValueError:
            flash('单价必须是有效的数字', 'error')
            return redirect(url_for('main.products_manage'))
        
        try:
            stock = int(stock_str)
            if stock < 0:
                flash('库存不能为负数', 'error')
                return redirect(url_for('main.products_manage'))
        except ValueError:
            flash('库存必须是有效的整数', 'error')
            return redirect(url_for('main.products_manage'))
        
        # 处理登记日期
        reg_date = None
        if reg_date_str:
            try:
                from datetime import datetime as dt
                reg_date = dt.strptime(reg_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('登记日期格式不正确', 'error')
                return redirect(url_for('main.products_manage'))
        
        if p_id:  # 编辑现有商品
            p = Product.query.get(p_id)
            if not p:
                flash('商品不存在', 'error')
                return redirect(url_for('main.products_manage'))
            
            p.name = name
            p.price = price
            p.stock = stock
            p.category = category if category else None
            p.model = model if model else None
            p.unit = unit if unit else None
            if reg_date:
                p.reg_date = reg_date
            
            db.session.commit()
            flash('商品更新成功', 'success')
        else:  # 新增商品
            p = Product(
                name=name,
                price=price,
                stock=stock,
                category=category if category else None,
                model=model if model else None,
                unit=unit if unit else None,
                reg_date=reg_date
            )
            db.session.add(p)
            db.session.commit()
            flash('商品添加成功', 'success')
        
        return redirect(url_for('main.products_manage'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'保存失败: {str(e)}', 'error')
        return redirect(url_for('main.products_manage'))

@main.route('/products/delete/<int:id>', methods=['POST'])
def product_delete(id):
    """
    实现删除功能（级联删除相关记录）
    """
    try:
        p = Product.query.get(id)
        if not p:
            flash('商品不存在', 'error')
            return redirect(url_for('main.products_manage'))
        
        # SQLAlchemy会自动处理级联删除（因为模型中配置了cascade="all, delete-orphan"）
        db.session.delete(p)
        db.session.commit()
        flash('商品删除成功（相关浏览记录和销售记录已同步删除）', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('main.products_manage'))

# --- 4. 销售查询 (数据查询窗体) (要求 II.3 & 其它 II.2) ---
@main.route('/sales')
def sales_query():
    # 参数查询：接收一个值
    keyword = request.args.get('param_keyword', '')
    
    query = Sale.query.join(Product).join(User)
    
    if keyword:
        # 允许输入商品名或用户名进行查询
        query = query.filter(Product.name.contains(keyword))
    
    sales = query.order_by(Sale.sale_date.desc()).all()
    return render_template('sales.html', sales=sales, keyword=keyword)

# --- 5. 浏览记录查询 (额外的数据查询窗体) (要求 II.3) ---
@main.route('/browse_logs')
def browse_logs():
    """
    实现浏览记录查询功能
    - JOIN User和Product表显示用户名和商品名
    - 支持按用户名筛选
    - 支持按日期范围筛选
    """
    username = request.args.get('username', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    
    # 基础查询：JOIN User和Product表
    query = BrowseLog.query.join(User).join(Product)
    
    # 按用户名筛选
    if username:
        query = query.filter(User.username.contains(username))
    
    # 按日期范围筛选
    if start_date:
        try:
            from datetime import datetime as dt
            start_dt = dt.strptime(start_date, '%Y-%m-%d')
            query = query.filter(BrowseLog.browse_time >= start_dt)
        except ValueError:
            flash('开始日期格式不正确', 'error')
    
    if end_date:
        try:
            from datetime import datetime as dt
            end_dt = dt.strptime(end_date, '%Y-%m-%d')
            # 包含结束日期的整天
            from datetime import timedelta
            end_dt = end_dt + timedelta(days=1)
            query = query.filter(BrowseLog.browse_time < end_dt)
        except ValueError:
            flash('结束日期格式不正确', 'error')
    
    # 按浏览时间降序排列
    logs = query.order_by(BrowseLog.browse_time.desc()).all()
    
    return render_template('browse_logs.html', 
                         logs=logs, 
                         username=username,
                         start_date=start_date,
                         end_date=end_date)
