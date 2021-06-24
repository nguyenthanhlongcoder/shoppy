from shop.admin.routes import categories
from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import db, app, photos, search
from .models import Brand, Category, Addproduct
from .forms import Addproducts
import secrets, os

@app.route('/')
def home():
    page = request.args.get('page', type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/index.html', products = products)


@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields = ['name', 'description'], limit=3)
    return render_template('products/result.html', products = products)

@app.context_processor
def inject_brand():
    brands = Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return dict(brands = brands, categories = categories)

@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', type=int)
    get_b = Brand.query.filter_by(id = id).first_or_404()
    brand = Addproduct.query.filter_by(brand = get_b).paginate(page=page, per_page=8)
    
    return render_template('products/index.html', brand = brand, get_b =get_b)

@app.route('/category/<int:id>')
def get_category(id):
    page = request.args.get('page', type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category = get_cat).paginate(page=page, per_page=8)

    return render_template('products/index.html', get_cat_prod = get_cat_prod, get_cat=get_cat)

@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', product = product)

@app.route('/addbrand', methods=["GET", "POST"])
def addbrand():
    if 'email' not in session:
        flash('Please login first','danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getbrand = request.form.get("brand")
        try:
            brand = Brand(name = getbrand)
            db.session.add(brand)
            flash(f'The Brand {getbrand} was added to your database', 'success')
            db.session.commit()
        except Exception as e:
            print(e)
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html', brands = 'brands')

@app.route('/addcategory', methods=["GET", "POST"])
def addcategory():
    if 'email' not in session:
        flash('Please login first','danger')
        return redirect(url_for('login'))

    if request.method == "POST":
        getcategory = request.form.get("category")
        try:
            category = Category(name = getcategory)
            db.session.add(category)
            flash(f'The Category {getcategory} was added to your database', 'success')
            db.session.commit()
        except Exception as e:
            print(e)
        return redirect(url_for('addcategory'))
    return render_template('products/addcategory.html', categories = 'categories')

@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if 'email' not in session:
        flash('Please login first','danger')
        return redirect(url_for('login'))
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        
        image_1 = photos.save(request.files.get('image_1'), name = secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name = secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name = secrets.token_hex(10) + ".")

        addpro = Addproduct(name = name, price = price, discount =discount, stock =stock, colors = colors, description = description, brand_id = brand, category_id = category, image_1 = image_1, image_2 = image_2, image_3 = image_3)
        db.session.add(addpro)
        flash(f'The product {name} has been added to your datatbase', 'success')
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('products/addproduct.html', form = form, brands= brands, categories = categories)

@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.brand_id = brand
        product.category_id = category
        product.colors = form.colors.data
        product.stock = form.stock.data
        product.description = form.description.data
        
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/img/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name = secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name = secrets.token_hex(10) + ".")
 
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/img/" + product.image_1))
                product.image_2 = photos.save(request.files.get('image_2'), name = secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name = secrets.token_hex(10) + ".")
                 
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/img/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name = secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name = secrets.token_hex(10) + ".")
                
        db.session.commit()
        flash(f'Your product hase been updated', 'success')
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.description.data = product.description
    form.stock.data = product.stock
    form.colors.data = product.colors
    return render_template('products/updateproduct.html', form = form, brands = brands, categories = categories, product = product)

@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'Your brand has been updated')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title="Update Brand Page", updatebrand = updatebrand)

@app.route('/deletebrand/<int:id>', methods=['GET', 'POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand {brand.name} has been deleted', 'success')
        return redirect(url_for('admin'))
    
    flash(f'The brand {brand.name} cant be deleted', 'danger')
    return redirect(url_for('admin'))
    
@app.route('/deletecategory/<int:id>', methods=['GET', 'POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'The category {category.name} has been deleted', 'success')
        return redirect(url_for('admin'))
    
    flash(f'The category {category.name} cant be deleted', 'danger')
    return redirect(url_for('admin'))


@app.route('/deleteproduct/<int:id>', methods=['GET', 'POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/img/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/img/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/img/" + product.image_3))
        except Exception as e:
            print(e)
 
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} has been deleted', 'success')
        return redirect(url_for('admin'))
    
    flash(f'The product {product.name} cant be deleted', 'danger')
    return redirect(url_for('admin'))


@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    
    if request.method == "POST":
        updatecategory.name = category
        flash(f'Your category has been updated')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('products/updatebrand.html', title="Update Category Page", updatecategory = updatecategory)