#!/usr/bin/env python3
from database_models import db, Product, Category
from app import create_app

app = create_app()
with app.app_context():
    count = Product.query.count()
    print(f'Total products: {count}')
    
    cat_count = Category.query.count()
    print(f'Total categories: {cat_count}')
    
    products = Product.query.limit(3).all()
    print('\nSample products:')
    for p in products:
        print(f"  - {p.name} (${p.price}, discount: ${p.discount_price})")
