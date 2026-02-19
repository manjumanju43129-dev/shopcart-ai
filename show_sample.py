from app import create_app
from database_models import Product

app = create_app()
with app.app_context():
    total = Product.query.count()
    print(f'Total products: {total}')
    print('\nSample products (first 5):')
    for p in Product.query.order_by(Product.id).limit(5).all():
        print(f'{p.id} | {p.name} | {p.image_url}')
