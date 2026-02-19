from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask_cors import CORS
import random
import string
import os
from database_models import db, User, Product, Category, Cart, CartItem, Order, OrderItem, Payment
from datetime import datetime
from rapid_reviews import get_reviews
import mysql.connector
import requests

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_invoice_number():
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    rnd = ''.join(random.choices(string.digits, k=4))
    return f'INV{ts}{rnd}'

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')  # override with env in production
    jwt = JWTManager(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # GST configuration (default 5%)
    app.config['GST_RATE'] = float(os.environ.get('GST_RATE', 0.05))

    db.init_app(app)

    # Enable CORS for all routes (for development)
    CORS(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    # Serve index.html at root
    @app.route('/')
    def root():
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registration endpoint
    @app.route('/api/register', methods=['POST'])
    def api_register():
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name')
        if not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        user = User()
        user.email = email
        user.name = name
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # create an empty cart for user
        try:
            c = Cart(user_id=user.id)
            db.session.add(c)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return jsonify({'ok': True, 'message': 'Account created successfully'})

    # Debug endpoint
    @app.route('/api/test', methods=['GET'])
    def api_test():
        return jsonify({'ok': True, 'message': 'API is working', 'products': Product.query.count()})

    # Auth
    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error':'missing credentials'}), 400
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # login_user(user)  # Not needed with JWT
            access_token = create_access_token(identity=user.email)
            return jsonify({'ok':True,'admin':user.is_admin,'access_token':access_token})
        return jsonify({'error':'invalid credentials'}), 401
    # Protected profile endpoint (JWT required)
    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def profile():
        current_email = get_jwt_identity()
        user = User.query.filter_by(email=current_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict())

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def api_logout():
        logout_user()
        return jsonify({'ok':True})

    # Product endpoints
    @app.route('/api/products', methods=['GET','POST'])
    def products_list_create():
        if request.method == 'GET':
            items = Product.query.all()
            return jsonify([i.to_dict() for i in items])
        # create product (admin required)
        data = request.json or {}
        token = request.headers.get('Authorization','').replace('Bearer ','')
        # lightweight admin check by token identity
        try:
            if token:
                from flask_jwt_extended import decode_token
                identity = decode_token(token)['sub']
                u = User.query.filter_by(email=identity).first()
                if not u or not u.is_admin:
                    return jsonify({'error':'admin required'}), 403
        except Exception:
            return jsonify({'error':'invalid token'}), 401
        item = Product()
        item.name = data.get('name','')
        item.description = data.get('description','')
        item.price = float(data.get('price',0))
        item.stock = int(data.get('stock',0))
        item.image_url = data.get('image_url','')
        item.category_id = data.get('category_id')
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201

    @app.route('/api/products/<int:item_id>', methods=['GET','PUT','DELETE'])
    def product_item(item_id):
        item = Product.query.get_or_404(item_id)
        if request.method == 'GET':
            return jsonify(item.to_dict())
        # admin-only for updates
        token = request.headers.get('Authorization','').replace('Bearer ','')
        try:
            if token:
                from flask_jwt_extended import decode_token
                identity = decode_token(token)['sub']
                u = User.query.filter_by(email=identity).first()
                if not u or not u.is_admin:
                    return jsonify({'error':'admin required'}), 403
        except Exception:
            return jsonify({'error':'invalid token'}), 401
        if request.method == 'PUT':
            data = request.json or {}
            item.name = data.get('name', item.name)
            item.description = data.get('description', item.description)
            item.price = float(data.get('price', item.price))
            item.stock = int(data.get('stock', item.stock))
            item.image_url = data.get('image_url', item.image_url)
            item.category_id = data.get('category_id', item.category_id)
            db.session.commit()
            return jsonify(item.to_dict())
        db.session.delete(item)
        db.session.commit()
        return jsonify({'ok':True})

    # Categories
    @app.route('/api/categories', methods=['GET','POST'])
    def categories_list_create():
        if request.method == 'GET':
            q = Category.query.all()
            return jsonify([c.to_dict() for c in q])
        data = request.json or {}
        c = Category(name=data.get('name',''))
        db.session.add(c)
        db.session.commit()
        return jsonify(c.to_dict()), 201

    # Cart endpoints (JWT required)
    def get_current_user():
        identity = get_jwt_identity()
        if not identity:
            return None
        return User.query.filter_by(email=identity).first()

    @app.route('/api/cart', methods=['GET'])
    @jwt_required()
    def get_cart():
        user = get_current_user()
        if not user: return jsonify({'error':'not found'}), 404
        cart = Cart.query.filter_by(user_id=user.id).first()
        items = []
        if cart:
            cis = CartItem.query.filter_by(cart_id=cart.id).all()
            for ci in cis:
                p = Product.query.get(ci.product_id)
                items.append({'id':ci.id,'product': p.to_dict() if p else None,'quantity':ci.quantity})
        return jsonify({'cart_id': cart.id if cart else None, 'items': items})

    @app.route('/api/cart/add', methods=['POST'])
    @jwt_required()
    def cart_add():
        user = get_current_user()
        if not user: return jsonify({'error':'not found'}), 404
        data = request.json or {}
        try:
            product_id = int(data.get('product_id'))
            qty = int(data.get('quantity',1))
        except Exception:
            return jsonify({'error':'invalid input'}), 400
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart = Cart(user_id=user.id)
            db.session.add(cart); db.session.commit()
        ci = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if ci:
            ci.quantity += qty
        else:
            ci = CartItem(cart_id=cart.id, product_id=product_id, quantity=qty)
            db.session.add(ci)
        db.session.commit()
        return jsonify({'ok':True})

    @app.route('/api/cart/update', methods=['POST'])
    @jwt_required()
    def cart_update():
        user = get_current_user()
        if not user: return jsonify({'error':'not found'}), 404
        data = request.json or {}
        try:
            product_id = int(data.get('product_id'))
            qty = int(data.get('quantity',0))
        except Exception:
            return jsonify({'error':'invalid input'}), 400
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart: return jsonify({'error':'no cart'}), 404
        ci = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not ci: return jsonify({'error':'item not found'}), 404
        if qty <= 0:
            db.session.delete(ci)
        else:
            ci.quantity = qty
        db.session.commit()
        return jsonify({'ok':True})

    @app.route('/api/cart/remove', methods=['POST'])
    @jwt_required()
    def cart_remove():
        user = get_current_user()
        if not user: return jsonify({'error':'not found'}), 404
        data = request.json or {}
        try:
            product_id = int(data.get('product_id'))
        except Exception:
            return jsonify({'error':'invalid input'}), 400
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart: return jsonify({'error':'no cart'}), 404
        ci = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if ci:
            db.session.delete(ci)
            db.session.commit()
        return jsonify({'ok':True})

    # Checkout: create order from cart
    @app.route('/api/checkout', methods=['POST'])
    @jwt_required()
    def checkout():
        user = get_current_user()
        if not user: return jsonify({'error':'not found'}), 404
        data = request.json or {}
        payment_method = data.get('payment_method','unknown')
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart: return jsonify({'error':'cart empty'}), 400
        items = CartItem.query.filter_by(cart_id=cart.id).all()
        if not items: return jsonify({'error':'cart empty'}), 400
        subtotal = 0.0
        for ci in items:
            p = Product.query.get(ci.product_id)
            if not p: continue
            subtotal += (p.price * ci.quantity)
        gst_rate = app.config.get('GST_RATE', 0.05)
        gst_amount = round(subtotal * gst_rate, 2)
        total = round(subtotal + gst_amount, 2)
        order = Order(user_id=user.id, invoice_number=generate_invoice_number(), total_amount=total, gst_amount=gst_amount, status='placed')
        db.session.add(order)
        db.session.commit()
        for ci in items:
            p = Product.query.get(ci.product_id)
            if not p: continue
            oi = OrderItem(order_id=order.id, product_id=p.id, quantity=ci.quantity, price=p.price)
            db.session.add(oi)
            # reduce stock
            try:
                p.stock = max(0, p.stock - ci.quantity)
            except Exception:
                pass
            db.session.delete(ci)
        # create a payment record (pending)
        pay = Payment(order_id=order.id, payment_method=payment_method, payment_status='pending', amount=total)
        db.session.add(pay)
        db.session.commit()
        return jsonify({'ok':True, 'order_id': order.id, 'invoice': order.invoice_number})

    # Orders
    @app.route('/api/orders', methods=['GET'])
    @jwt_required()
    def list_orders():
        user = get_current_user()
        if not user: return jsonify({'error':'not found'}), 404
        orders = Order.query.filter_by(user_id=user.id).order_by(Order.order_date.desc()).all()
        out = []
        for o in orders:
            items = OrderItem.query.filter_by(order_id=o.id).all()
            out.append({'order': o.to_dict(), 'items':[it.to_dict() for it in items]})
        return jsonify(out)

    @app.route('/api/orders/<int:order_id>', methods=['GET'])
    @jwt_required()
    def order_detail(order_id):
        user = get_current_user()
        if not user: return jsonify({'error':'not found'}), 404
        o = Order.query.get_or_404(order_id)
        if o.user_id != user.id and not user.is_admin:
            return jsonify({'error':'forbidden'}), 403
        items = OrderItem.query.filter_by(order_id=o.id).all()
        return jsonify({'order': o.to_dict(), 'items': [it.to_dict() for it in items]})

    # Reviews (proxy to RapidAPI service)
    @app.route('/api/reviews')
    def reviews_proxy():
        asin = request.args.get('asin')
        if not asin:
            return jsonify({'ok': False, 'error': 'missing asin'}), 400
        res = get_reviews(asin)
        if not res.get('ok'):
            return jsonify(res), 502
        return jsonify(res)

    # Admin: view all orders
    @app.route('/api/admin/orders', methods=['GET'])
    @jwt_required()
    def admin_orders():
        user = get_current_user()
        if not user or not user.is_admin: return jsonify({'error':'admin required'}), 403
        orders = Order.query.order_by(Order.order_date.desc()).all()
        out = []
        for o in orders:
            items = OrderItem.query.filter_by(order_id=o.id).all()
            out.append({'order': o.to_dict(), 'items':[it.to_dict() for it in items]})
        return jsonify(out)

    @app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
    @jwt_required()
    def admin_update_order(order_id):
        user = get_current_user()
        if not user or not user.is_admin: return jsonify({'error':'admin required'}), 403
        o = Order.query.get_or_404(order_id)
        data = request.json or {}
        o.status = data.get('status', o.status)
        db.session.commit()
        return jsonify(o.to_dict())

    # Printable invoice page (HTML)
    @app.route('/invoice/<int:order_id>')
    @jwt_required()
    def invoice_page(order_id):
        user = get_current_user()
        if not user: return "Unauthorized", 401
        o = Order.query.get_or_404(order_id)
        if o.user_id != user.id and not user.is_admin:
            return "Forbidden", 403
        items = OrderItem.query.filter_by(order_id=o.id).all()
        rows = ''
        subtotal = 0.0
        for it in items:
            p = Product.query.get(it.product_id)
            name = p.name if p else f'Product {it.product_id}'
            line_total = (it.price or 0.0) * (it.quantity or 0)
            subtotal += line_total
            rows += f"<tr><td>{name}</td><td style='text-align:center'>{it.quantity}</td><td style='text-align:right'>₹{it.price:.2f}</td><td style='text-align:right'>₹{line_total:.2f}</td></tr>"
        gst = o.gst_amount or 0.0
        total = o.total_amount or round(subtotal + gst,2)
        html = f'''
        <html><head><title>Invoice {o.invoice_number}</title>
        <style>body{{font-family:Arial;padding:20px}}table{{width:100%;border-collapse:collapse}}td,th{{padding:8px;border-bottom:1px solid #eee}}</style>
        </head><body>
        <h2>Invoice: {o.invoice_number}</h2>
        <div>Order Date: {o.order_date.strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div>Customer: {user.name or user.email}</div>
        <table><thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead><tbody>{rows}</tbody></table>
        <div style='margin-top:12px'>Subtotal: ₹{subtotal:.2f}</div>
        <div>GST: ₹{gst:.2f}</div>
        <div style='font-weight:800;margin-top:8px'>Grand Total: ₹{total:.2f}</div>
        <div style='margin-top:16px;color:gray'>Thank you for your purchase.</div>
        </body></html>
        '''
        return html

    # Profit stats: return total revenue, cost, profit per day (simple aggregation)
    @app.route('/api/stats/profit', methods=['GET'])
    def profit_stats():
        # Aggregate revenue by payment date from payments table
        rows = db.session.query(Payment).all()
        data = {}
        for p in rows:
            key = p.created_at.strftime('%Y-%m-%d')
            data.setdefault(key, 0.0)
            data[key] += float(p.amount or 0.0)
        out = []
        for k in sorted(data.keys()):
            out.append({'date': k, 'revenue': data[k]})
        return jsonify(out)

    # Image upload endpoint
    @app.route('/api/upload_image', methods=['POST'])
    def upload_image():
        if 'image' not in request.files:
            return jsonify({'error':'no file'}), 400
        f = request.files['image']
        if not f.filename:
            return jsonify({'error':'no filename'}), 400
        filename = secure_filename(f.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(path)
        return jsonify({'url':f'/uploads/{filename}'})

    # serve uploads
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Serve static files (HTML, JS, CSS) from project root
    @app.route('/<path:filename>')
    def serve_static(filename):
        # Skip API routes - let API endpoints handle them
        if filename.startswith('api/'):
            return "Not Found", 404
        # Don't serve index.html here - it should go through the root route
        if filename == 'index.html':
            return "Not Found", 404
        # Only serve files with allowed extensions for security
        allowed_ext = ('.html', '.js', '.css', '.png', '.jpg', '.jpeg', '.avif', '.gif', '.webp', '.mp3', '.wav', '.ogg')
        if not filename.lower().endswith(allowed_ext):
            return "Not Found", 404
        
        # Try to serve the file
        try:
            response = send_from_directory('.', filename)
            # Add CORS headers explicitly
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            # Cache static files for 1 hour
            response.headers['Cache-Control'] = 'public, max-age=3600'
            return response
        except Exception as e:
            return f"Error serving {filename}: {str(e)}", 404

    # Touch file to trigger reload when static assets change
    return app

if __name__ == '__main__':
    import os
    app = create_app()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
