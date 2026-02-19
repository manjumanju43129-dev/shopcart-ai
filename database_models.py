from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='customer')  # 'customer' or 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'role': self.role}


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, default=0.0)
    discount_price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(400), default='')
    rating = db.Column(db.Float, default=0.0)
    asin = db.Column(db.String(80), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'discount_price': self.discount_price,
            'rating': self.rating,
            'asin': self.asin,
            'stock': self.stock,
            'image_url': self.image_url,
            'category_id': self.category_id
        }


class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id}


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {'id': self.id, 'cart_id': self.cart_id, 'product_id': self.product_id, 'quantity': self.quantity}


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    invoice_number = db.Column(db.String(120), nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    gst_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(60), default='pending')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_date': self.order_date.isoformat(),
            'invoice_number': self.invoice_number,
            'total_amount': self.total_amount,
            'gst_amount': self.gst_amount,
            'status': self.status
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {'id': self.id, 'order_id': self.order_id, 'product_id': self.product_id, 'quantity': self.quantity, 'price': self.price}


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_method = db.Column(db.String(120), default='unknown')
    payment_status = db.Column(db.String(60), default='pending')
    amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'order_id': self.order_id, 'payment_method': self.payment_method, 'payment_status': self.payment_status, 'amount': self.amount, 'created_at': self.created_at.isoformat()}

