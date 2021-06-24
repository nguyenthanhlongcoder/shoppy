from flask import render_template, session, request, redirect, url_for, flash
from shop import app, db, bcrypt
from .forms import RegistrationForm, LoginForm
from .models import User
from shop.products.models import Addproduct, Brand, Category
from shop.customers.model import CustomerOrder, Register

import os


@app.route('/admin')
def admin():
    return render_template('admin/index.html')

@app.route('/product')
def products():
    if 'email' not in session:
        flash('Please login first','danger')
        return redirect(url_for('login'))
    
    products = Addproduct.query.all()
    return render_template('admin/product.html', title='Admin page', products = products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        
        user = User(name=  form.name.data,username= form.username.data,email = form.email.data,
                   password = hash_password)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('admin/register_page.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Welcome {form.email.data} Your are loggedin now', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong password please try again', 'danger')
    return render_template('admin/login_page.html', form = form)

@app.route('/brand')
def brands():
    if 'email' not in session:
        flash('Please login first','danger')
        return redirect(url_for('login'))
    
    brands = Brand.query.all()
    
    return render_template('admin/brand.html', title='Brand Page', brands = brands)


@app.route('/category')
def categories():
    if 'email' not in session:
        flash('Please login first','danger')
        return redirect(url_for('login'))
    
    categories = Category.query.all()
    
    return render_template('admin/category.html', title='Category Page', categories = categories)

@app.route('/getorders')
def getorders():
    if 'email' in session:
        orders = CustomerOrder.query.order_by(CustomerOrder.date_created.desc()).all()
       
    else:
        flash('Please login first','danger')
        return redirect(url_for('login'))
    return render_template('admin/orders.html',  orders=orders, Register = Register)

@app.route('/admin_order/<invoice>', methods=["GET", "POST"])
def admin_order(invoice):
    if 'email' in session:
        orders = CustomerOrder.query.filter_by(invoice = invoice).first()
        customer = Register.query.filter_by(id = orders.customer_id).first()
        grandTotal = 0
        discount = 0
        for _key, product in orders.orders.items():
            discount += (product['discount']/100) * float(product['price']) * int(product['quanlity'])
            grandTotal += float(product['price']) * int(product['quanlity'])
        if request.method == "POST":
            orders.status = request.form.get("status")
            db.session.commit()
            return redirect(url_for('getorders'))
    else:
        flash('Please login first','danger')
        return redirect(url_for('login'))
    return render_template('admin/admin_order.html',  orders=orders, Register = Register, customer = customer, discount = discount, grandTotal = grandTotal)