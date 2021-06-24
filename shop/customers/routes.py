from operator import is_not
from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response
import flask_login
from werkzeug.wrappers import response
from shop import app, bcrypt, db, login_manager
from flask_login import login_required, current_user, logout_user, login_user
from .forms import CustomerRegisterForm, CustomerLoginForm
from .model import Register, CustomerOrder
import secrets
import pdfkit
import stripe

Publishable_key = 'pk_test_51J5ApuDPIPFdlbVmfbx5vfrAfGnZl9jkz1DdiDG1XFap92zsYPInbubz4VYEWYdzWp5tDZ8DvbE3mPxmQxID36cN00xS7WNmLT'
stripe.api_key = 'sk_test_51J5ApuDPIPFdlbVmzH3Y8t16cEbVwSHFCi9w3O1UloIOspQ1JfdQx182tSGKxfgErXh7daQ0s8OQ3Ol9Rk4NfKIq00DS0Qedej'

@app.route('/payment', methods = ['POST'])
@login_required
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='Shoppy',
        amount=amount,
        currency='vnd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('customer/thanks.html')

@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm(request.form)
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user_test = Register.query.filter_by(email=form.email.data).first()
        if user_test is None:
            register = Register(name=form.name.data, username = form.username.data, email=form.email.data, password = hash_password, address=form.address.data, contact = form.contact.data)
            db.session.add(register)
            db.session.commit()
            return redirect(url_for('customerLogin'))
        else:
            flash('This email is already exists', category='danger')
            return render_template('customer/register.html', form = form)


    return render_template('customer/register.html', form = form)

@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Inconrrect email or password', category='danger')
        return redirect(url_for('customerLogin'))
    return  render_template('customer/login.html', form = form)

@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice= invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent','success')
            return redirect(url_for('orders', invoice = invoice))
        except Exception as e:
            print(e)
            flash('Something went wrong while get order', 'danger')
            return redirect(url_for('getCart'))
        
        
@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        discount = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id = customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount += (product['discount']/100) * float(product['price']) * int(product['quanlity'])
            grandTotal += float(product['price']) * int(product['quanlity'])
            
    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice = invoice, grandTotal = grandTotal, discount = discount, customer=customer, orders=orders)

@app.route('/get_pdf/<invoice>', methods=['GET','POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        discount = 0
        customer_id = current_user.id
        if request.method == 'POST':
            customer = Register.query.filter_by(id = customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount += (product['discount']/100) * float(product['price']) * int(product['quanlity'])
                grandTotal += float(product['price']) * int(product['quanlity'])
            
   
            rendered =  render_template('customer/pdf.html', invoice = invoice, grandTotal = grandTotal, discount = discount, customer=customer, orders=orders)

            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type']='application/pdf'
            response.headers['content-Disposition']='inline : filename=' + invoice + '.pdf'
            return response
    return request(url_for('orders'))

@app.route('/your_orders')
@login_required
def your_orders():
    if current_user.is_authenticated:
        orders = CustomerOrder.query.filter_by(customer_id = current_user.id).order_by(CustomerOrder.date_created.desc())
        return render_template('customer/your_orders.html', orders = orders)
    else:
        return render_template('customerLogin')
        
