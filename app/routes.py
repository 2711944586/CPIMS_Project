from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func, text
from datetime import datetime
from .models import db, Product, Sale, BrowseLog, User

main = Blueprint('main', __name__)

@main.route('/')
def cover():
    return render_template('cover.html')

@main.route('/dashboard')
def dashboard():
    current_year = datetime.now().year
    
    total_sales = db.session.query(func.sum(Sale.total_amount))\
        .filter(func.extract('year', Sale.sale_date) == current_year).scalar() or 0
    
    total_qty = db.session.query(func.sum(Sale.quantity))\
        .filter(func.extract('year', Sale.sale_date) == current_year).scalar() or 0
    
    total_products = Product.query.count()
    total_users = User.query.count()
    
    # 每日浏览
    if 'postgresql' in str(db.engine.url):
        daily_logs = db.session.query(
            func.cast(BrowseLog.browse_time, db.Date).label('date'),
            func.count(BrowseLog.id).label('cnt')
        ).group_by(text('date')).order_by(text('date')).limit(14).all()
    else:
        daily_logs = db.session.query(
            func.date(BrowseLog.browse_time).label('date'),
            func.count(BrowseLog.id).label('cnt')
        ).group_by('date').order_by('date').limit(14).all()
    
    chart_dates = [str(item.date)[-5:] for item in daily_logs]
    chart_counts = [item.cnt for item in daily_logs]
    
    # 品类分布
    category_sales = db.session.query(
        Product.category,
        func.sum(Sale.total_amount).label('amount')
    ).join(Sale).group_by(Product.category).all()
    
    category_labels = [item.category or '未分类' for item in category_sales]
    category_amounts = [float(item.amount) for item in category_sales]
    
    # 月度趋势
    if 'postgresql' in str(db.engine.url):
        monthly_sales = db.session.query(
            func.to_char(Sale.sale_date, 'YYYY-MM').label('month'),
            func.sum(Sale.total_amount).label('amount'),
            func.sum(Sale.quantity).label('qty')
        ).filter(func.extract('year', Sale.sale_date) == current_year)\
         .group_by(text('month')).order_by(text('month')).all()
    else:
        monthly_sales = db.session.query(
            func.strftime('%Y-%m', Sale.sale_date).label('month'),
            func.sum(Sale.total_amount).label('amount'),
            func.sum(Sale.quantity).label('qty')
        ).filter(func.extract('year', Sale.sale_date) == current_year)\
         .group_by('month').order_by('month').all()
    
    month_labels = [item.month[-2:] + '月' for item in monthly_sales]
    month_amounts = [float(item.amount) for item in monthly_sales]
    month_quantities = [item.qty for item in monthly_sales]
    
    # TOP10商品
    top_products = db.session.query(
        Product.name,
        func.sum(Sale.quantity).label('total_qty')
    ).join(Sale).group_by(Product.id)\
     .order_by(func.sum(Sale.quantity).desc()).limit(10).all()
    
    top_product_names = [item.name[:12] for item in top_products]
    top_product_sales = [item.total_qty for item in top_products]
    
    low_stock_count = Product.query.filter(Product.stock < 10).count()
    
    platform_stats = db.session.query(
        BrowseLog.platform,
        func.count(BrowseLog.id).label('cnt')
    ).group_by(BrowseLog.platform).all()
    
    platform_labels = [item.platform for item in platform_stats]
    platform_counts = [item.cnt for item in platform_stats]

    return render_template('dashboard.html',
                           total_sales=f"{total_sales:,.0f}",
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

@main.route('/products')
def products_manage():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('products.html', products=pagination.items, pagination=pagination)

@main.route('/products/save', methods=['POST'])
def product_save():
    try:
        p_id = request.form.get('id')
        name = request.form.get('name', '').strip()
        reg_date_str = request.form.get('reg_date', '').strip()
        category = request.form.get('category', '').strip()
        model = request.form.get('model', '').strip()
        unit = request.form.get('unit', '').strip()
        price_str = request.form.get('price', '').strip()
        stock_str = request.form.get('stock', '').strip()
        
        if not name:
            flash('商品名称不能为空', 'error')
            return redirect(url_for('main.products_manage'))
        
        try:
            price = float(price_str) if price_str else 0
            stock = int(stock_str) if stock_str else 0
        except ValueError:
            flash('价格或库存格式错误', 'error')
            return redirect(url_for('main.products_manage'))
        
        reg_date = None
        if reg_date_str:
            try:
                reg_date = datetime.strptime(reg_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if p_id:
            p = Product.query.get(p_id)
            if p:
                p.name = name
                p.price = price
                p.stock = stock
                p.category = category or None
                p.model = model or None
                p.unit = unit or None
                if reg_date:
                    p.reg_date = reg_date
                db.session.commit()
                flash('商品更新成功', 'success')
        else:
            p = Product(name=name, price=price, stock=stock,
                       category=category or None, model=model or None,
                       unit=unit or None, reg_date=reg_date)
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
    try:
        p = Product.query.get(id)
        if p:
            db.session.delete(p)
            db.session.commit()
            flash('商品删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    return redirect(url_for('main.products_manage'))

@main.route('/sales')
def sales_query():
    keyword = request.args.get('param_keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    query = Sale.query.join(Product).join(User)
    if keyword:
        query = query.filter(Product.name.contains(keyword))
    
    pagination = query.order_by(Sale.sale_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 统计数据（只统计当前筛选条件下的）
    stats_query = Sale.query.join(Product)
    if keyword:
        stats_query = stats_query.filter(Product.name.contains(keyword))
    
    total_amount = stats_query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
    total_qty = stats_query.with_entities(func.sum(Sale.quantity)).scalar() or 0
    total_count = stats_query.count()
    
    return render_template('sales.html', 
                          sales=pagination.items, 
                          pagination=pagination,
                          keyword=keyword,
                          total_amount=total_amount,
                          total_qty=total_qty,
                          total_count=total_count)

@main.route('/browse_logs')
def browse_logs():
    username = request.args.get('username', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    query = BrowseLog.query.join(User).join(Product)
    
    if username:
        query = query.filter(User.username.contains(username))
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(BrowseLog.browse_time >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            from datetime import timedelta
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(BrowseLog.browse_time < end_dt)
        except ValueError:
            pass
    
    pagination = query.order_by(BrowseLog.browse_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('browse_logs.html', 
                         logs=pagination.items,
                         pagination=pagination,
                         username=username,
                         start_date=start_date,
                         end_date=end_date,
                         total_count=pagination.total)
