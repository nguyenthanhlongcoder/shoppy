from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import db, app
from shop.products.models import Addproduct

def MegerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False
@app.route('/addcart', methods=["POST"])
def AddCart():
    try:
        product_id = request.form.get("product_id")
        quanlity = request.form.get("quanlity")
        color = request.form.get("colors")
        product = Addproduct.query.filter_by(id=product_id).first()
        
        if request.method == "POST":
            DictItems = {product_id:{'name': product.name, 'price':float(product.price), 'discount':  product.discount, 'color': color, 'quanlity':quanlity, 'image': product.image_1}}

            if 'Shoppingcart' in session:
                print('Session in shoppingcart')
                if product_id in session['Shoppingcart']:
                    session.modified = True
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            itemquanlity = item['quanlity']
                            item['quanlity'] = int(itemquanlity) + int(quanlity)
                            
                else:
                    session['Shoppingcart'] = MegerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
            
            
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
    
@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quanlity'])
        grandtotal += subtotal
        subtotal -= discount
    return render_template('products/carts.html', grandtotal=grandtotal)

@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session and len(session('Shoppingcart')) <= 0:
        return redirect(url_for('home'))
    if request.method == 'POST':
        quanlity = request.form.get('quanlity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['color'] = color
                    item['quanlity'] = quanlity
                    flash('Item is updated')
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))
        
@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))

        return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))
    
@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
    