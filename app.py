from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import webbrowser

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__,
            template_folder='shopping_mall/templates',
            static_folder='shopping_mall/static')
app.secret_key = 'secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'shoppingmall.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ====================== DB 모델 ======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

# ====================== 로그인/회원가입 ======================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

# ====================== 상품 목록 / 상세 ======================
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

# ====================== 장바구니 ======================
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect('/login')
    items = Cart.query.filter_by(user_id=session['user_id']).all()
    cart_data = []
    total = 0
    for item in items:
        product = Product.query.get(item.product_id)
        subtotal = product.price * item.quantity
        cart_data.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'qty': item.quantity,
            'subtotal': subtotal
        })
        total += subtotal
    return render_template('cart.html', cart=cart_data, total=total)

@app.route('/cart/add/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect('/login')
    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        db.session.add(Cart(user_id=session['user_id'], product_id=product_id, quantity=1))
    db.session.commit()
    return redirect('/cart')

# ====================== 주문 ======================
@app.route('/order')
def order():
    if 'user_id' not in session:
        return redirect('/login')
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if cart_items:
        new_order = Order(user_id=session['user_id'])
        db.session.add(new_order)
        Cart.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
    return render_template('order_complete.html')

# ====================== 관리자 페이지 ======================
@app.route('/admin')
def admin():
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['POST'])
def admin_add():
    name = request.form['name']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    desc = request.form['description']
    image = request.form['image']  # ← 추가
    db.session.add(Product(name=name, price=price, stock=stock, description=desc, image=image))
    db.session.commit()
    return redirect('/admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Product.query.first():
            db.session.add(Product(name='LG gram pro', price=2500000, stock=7, description='LG gram pro', image='LG_gram_pro.jpeg'))
            db.session.add(Product(name='Galaxy Watch Activate', price=250000, stock=20, description='Galaxy Watch Active', image='Galaxy_Watch_Activate.jpeg'))
            db.session.add(Product(name='LG OLED TV', price=3400000, stock=12, description='LG OLED TV', image='LG_OLED_TV.jpeg'))
            db.session.add(Product(name='Galaxy Tap S10', price=1700000, stock=40, description='Galaxy Tap S10', image='Galaxy_Tap_S10.jpeg'))
            db.session.add(Product(name='Galaxy S25 Ultra', price=1100000, stock=31, description='Galaxy S25 Ultra', image='Galaxy_S25_Ultra.jpg'))
            db.session.commit()

    webbrowser.open('http://127.0.0.1:5000')
    app.run(debug=True)


