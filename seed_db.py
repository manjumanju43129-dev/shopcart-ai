from app import create_app
from database_models import db, User, Category, Product, Cart
import random

app = create_app()

SAMPLE_CATEGORIES = [
    {'name': 'Electronics'},
    {'name': 'Fashion'},
    {'name': 'Home & Kitchen'},
    {'name': 'Mobile Phones'},
    {'name': 'Accessories'},
    {'name': 'Sports & Outdoors'},
    {'name': 'Books'},
    {'name': 'Beauty'},
    {'name': 'Toys & Games'},
    {'name': 'Grocery'},
]

# Generate 1000+ products
SAMPLE_PRODUCTS = []

# Electronics
electronics = [
    ('Wireless Bluetooth Headphones', 'High-quality audio with 20-hour battery', 1299, 999),
    ('USB-C Fast Charging Cable', 'Durable 2M cable with fast charging support', 299, 199),
    ('Portable SSD 500GB', 'Ultra-fast external storage with USB 3.1', 4999, 3999),
    ('LED Desk Lamp', 'Bright LED lamp with adjustable brightness', 1499, 999),
    ('Wireless Mouse', 'Silent mouse with 2.4GHz receiver', 599, 399),
    ('USB Hub 4-Port', 'Compact USB 3.0 hub for multiple devices', 799, 499),
    ('Phone Stand', 'Adjustable mobile phone stand for desk', 399, 249),
    ('Screen Protector Pack', 'Tempered glass screen protector (2 pack)', 299, 199),
    ('Keyboard Backlit Mechanical', 'RGB mechanical gaming keyboard', 2999, 1999),
    ('Webcam 1080p HD', 'Clear HD webcam with microphone', 1999, 1299),
]

# Fashion
fashion = [
    ('Cotton T-Shirt', 'Comfortable 100% cotton t-shirt for men', 399, 299),
    ('Denim Jeans', 'Casual blue denim jeans with stretchable fabric', 1299, 899),
    ('Casual Running Shoes', 'Lightweight shoes perfect for daily wear', 1799, 999),
    ('Winter Jacket', 'Warm jacket with water-resistant coating', 2999, 1999),
    ('Casual Shirt', 'Formal casual shirt in multiple colors', 799, 499),
    ('Sports Shorts', 'Quick-dry sports shorts for gym', 599, 399),
    ('Socks Pack', 'Pack of 6 comfortable cotton socks', 299, 199),
    ('Belt Leather', 'Premium leather belt with metal buckle', 699, 399),
    ('Sweater Wool', 'Warm wool sweater for winter', 1499, 999),
    ('Casual Sneakers', 'White casual sneakers for everyday wear', 1299, 899),
]

# Home & Kitchen
home = [
    ('Non-Stick Frying Pan', '28cm non-stick frying pan with silicone handle', 899, 599),
    ('Kitchen Knife Set', 'Set of 6 stainless steel kitchen knives', 1299, 799),
    ('Mixer Blender', 'Powerful 500W mixer grinder', 2499, 1699),
    ('Dinner Plate Set', 'Set of 6 ceramic dinner plates', 699, 499),
    ('Tea Kettle', 'Stainless steel tea kettle 2L', 499, 299),
    ('Cutting Board', 'Bamboo cutting board with handle', 399, 249),
    ('Kitchen Storage Jars', 'Set of 3 glass storage containers', 599, 399),
    ('Dish Drainer Rack', 'Stainless steel dish drying rack', 799, 499),
    ('Table Runner', 'Cotton table runner with printed design', 349, 199),
    ('Bed Sheet Set', 'Double bed cotton sheet set', 1299, 799),
]

# Mobile Phones
mobiles = [
    ('Smartphone 6.5" FHD', '6.5" FHD display with 128GB storage', 19999, 14999),
    ('Phone Case Premium', 'Shockproof phone case for all models', 399, 249),
    ('Tempered Glass Screen Guard', 'Anti-blue light screen protector', 299, 199),
    ('Phone Charger 65W', 'Fast charging 65W USB-C charger', 1299, 799),
    ('Bluetooth Speaker', 'Portable wireless speaker with 10-hour battery', 2499, 1799),
    ('Phone Mount Car', 'Universal car phone mount dashboard', 399, 249),
    ('Phone Cooling Fan', 'Mobile phone cooler for gaming', 599, 399),
    ('USB-C Hub Mobile', '7-in-1 USB-C hub for smartphones', 1999, 1299),
    ('Camera Lens Protector', 'Glass protector for camera lenses', 199, 99),
    ('Phone Stand Holder', 'Adjustable phone stand for desk', 249, 149),
]

# Accessories
accessories = [
    ('Sunglasses UV Protection', 'UV400 protection sunglasses', 599, 399),
    ('Watch Analog', 'Casual analog wristwatch', 1299, 799),
    ('Wallet Leather', 'Premium leather bifold wallet', 899, 599),
    ('Cap Baseball', 'Adjustable baseball cap', 299, 199),
    ('Bag Backpack', '30L travel backpack with USB port', 1299, 899),
    ('Scarf Winter', 'Warm woolen winter scarf', 399, 249),
    ('Gloves Winter', 'Thermal winter gloves', 299, 199),
    ('Umbrella Compact', 'Compact automatic umbrella', 399, 249),
    ('Key Chain Metal', 'Durable metal key chain', 99, 49),
    ('Hair Clip Set', 'Set of 10 decorative hair clips', 199, 99),
]

# Sports & Outdoors
sports = [
    ('Cricket Bat Wooden', 'Professional cricket bat', 1999, 1299),
    ('Football Synthetic', 'Official size synthetic football', 599, 399),
    ('Yoga Mat', '6mm non-slip yoga mat', 799, 499),
    ('Dumbbells Set', 'Set of 5kg dumbbells pair', 1299, 899),
    ('Bicycle MTB 26"', 'Mountain bike 21-speed', 7999, 5999),
    ('Skateboard Wooden', 'Professional skateboard deck', 1899, 1299),
    ('Swimming Goggles', 'Anti-fog swimming goggles', 399, 249),
    ('Fitness Rope Jump', 'Speed jump rope with ball bearings', 299, 199),
    ('Sleeping Bag', 'Outdoor camping sleeping bag', 1499, 999),
    ('Camping Tent 2-person', '2-person waterproof tent', 2499, 1799),
]

# Books
books = [
    ('Python Programming', 'Learn Python in 30 days', 299, 199),
    ('Data Science Guide', 'Complete guide to data science', 499, 349),
    ('Web Development', 'Full-stack web development course book', 399, 299),
    ('Business Strategy', 'Strategic business planning guide', 449, 299),
    ('Self Help Book', 'Personal development and success', 349, 249),
    ('Novel Fiction', 'Bestselling fiction novel', 299, 199),
    ('History Book', 'World history from ancient times', 549, 399),
    ('Cooking Recipe', '100 easy recipes for home cooking', 349, 249),
    ('Travel Guide', 'Complete travel guide to India', 399, 299),
    ('Art Book', 'Modern art and photography', 549, 399),
]

# Beauty
beauty = [
    ('Face Wash', 'Gentle face wash for all skin types', 299, 199),
    ('Shampoo Bottle', '200ml nourishing hair shampoo', 349, 249),
    ('Moisturizer Cream', 'Hydrating moisturizer with SPF 30', 499, 349),
    ('Lipstick Matte', 'Long-lasting matte lipstick', 299, 199),
    ('Face Mask Sheet', 'Pack of 10 hydrating face masks', 399, 249),
    ('Sunscreen SPF50', 'Broad-spectrum sunscreen lotion', 349, 249),
    ('Eye Serum', 'Anti-aging under-eye serum', 599, 399),
    ('Nail Polish Set', 'Pack of 5 nail polish colors', 349, 249),
    ('Perfume', '100ml premium body perfume', 1299, 899),
    ('Hair Oil', 'Pure coconut hair oil 200ml', 199, 99),
]

# Toys & Games
toys = [
    ('Building Blocks Set', '500pc educational building blocks', 899, 599),
    ('Puzzle Game', '1000-piece jigsaw puzzle', 399, 249),
    ('Board Game', 'Family board game set', 499, 349),
    ('Action Figure', 'Superhero action figure 15cm', 399, 249),
    ('Remote Control Car', '1:16 scale RC car', 1299, 899),
    ('Drone Beginner', 'Beginner-friendly drone with camera', 4999, 3499),
    ('Chess Set', 'Wooden chess board with pieces', 599, 399),
    ('Card Game', 'Poker playing card deck', 99, 49),
    ('Doll Dress-up', 'Fashion doll with accessories', 499, 349),
    ('Kite Set', 'Colorful kites with string pack', 199, 99),
]

# Grocery
grocery = [
    ('Basmati Rice 1kg', 'Premium long-grain basmati rice', 399, 299),
    ('Olive Oil', '500ml extra virgin olive oil', 599, 449),
    ('Sugar 1kg', 'Refined white sugar', 99, 69),
    ('Tea Bags', 'Pack of 50 black tea bags', 199, 149),
    ('Coffee Powder', '200g instant coffee powder', 299, 199),
    ('Honey Jar', '500ml pure honey', 399, 299),
    ('Nuts Mix', 'Mixed nuts and dry fruits 200g', 499, 349),
    ('Flour Bag', '5kg all-purpose flour', 199, 129),
    ('Spice Mix', 'Garam masala 100g', 99, 69),
    ('Biscuits Pack', 'Chocolate cream biscuits 200g', 99, 59),
]

# Compile all products
all_product_data = electronics + fashion + home + mobiles + accessories + sports + books + beauty + toys + grocery

# Map categories
category_map = {
    'Electronics': electronics,
    'Fashion': fashion,
    'Home & Kitchen': home,
    'Mobile Phones': mobiles,
    'Accessories': accessories,
    'Sports & Outdoors': sports,
    'Books': books,
    'Beauty': beauty,
    'Toys & Games': toys,
    'Grocery': grocery,
}

# Generate products with proper category mapping
for category_name, products in category_map.items():
    for idx, (name, desc, price, disc_price) in enumerate(products):
        rating = round(random.uniform(3.5, 4.9), 1)
        stock = random.randint(10, 100)
        asin = f'B{random.randint(10000000, 99999999)}'
        SAMPLE_PRODUCTS.append({
            'name': name,
            'description': desc,
            'price': price,
            'discount_price': disc_price,
            'stock': stock,
            'image_url': 'o2_featured_v2.avif',
            'rating': rating,
            'category': category_name,
            'asin': asin if random.random() > 0.3 else None
        })

# Generate 900+ additional product variations to reach 1000+
product_prefixes = ['Premium', 'Deluxe', 'Professional', 'Standard', 'Ultra', 'Compact', 'Portable', 'Heavy-Duty', 'Lightweight', 'Smart']
color_variants = ['Black', 'White', 'Blue', 'Red', 'Green', 'Silver', 'Gold', 'Grey', 'Pink', 'Purple']
size_variants = ['Small', 'Medium', 'Large', 'XL', '32GB', '64GB', '128GB', '256GB', '2L', '5L']

for _ in range(900):
    category_name = random.choice(list(category_map.keys()))
    base_product = random.choice(category_map[category_name])
    prefix = random.choice(product_prefixes)
    variant = random.choice(color_variants + size_variants)
    
    name = f'{prefix} {base_product[0]} - {variant}'
    desc = f'{base_product[1]} (Variant: {variant})'
    price = float(base_product[2]) * random.uniform(0.8, 1.3)
    disc_price = price * random.uniform(0.7, 0.9)
    
    SAMPLE_PRODUCTS.append({
        'name': name,
        'description': desc,
        'price': round(price, 2),
        'discount_price': round(disc_price, 2),
        'stock': random.randint(5, 200),
        'image_url': 'o2_featured_v2.avif',
        'rating': round(random.uniform(3.0, 5.0), 1),
        'category': category_name,
        'asin': f'B{random.randint(10000000, 99999999)}' if random.random() > 0.4 else None
    })

with app.app_context():
    print('Creating database tables...')
    db.create_all()

    # create categories
    cat_map = {}
    for c in SAMPLE_CATEGORIES:
        existing = Category.query.filter_by(name=c['name']).first()
        if not existing:
            existing = Category(name=c['name'])
            db.session.add(existing)
    db.session.commit()
    for c in Category.query.all():
        cat_map[c.name] = c.id

    # create products in batches
    print(f'Creating {len(SAMPLE_PRODUCTS)} products...')
    batch_size = 100
    for i, p in enumerate(SAMPLE_PRODUCTS):
        if not Product.query.filter_by(name=p['name']).first():
            pr = Product(
                name=p['name'], 
                description=p['description'], 
                price=p['price'],
                discount_price=p.get('discount_price'), 
                stock=p['stock'], 
                image_url=p.get('image_url'), 
                rating=p.get('rating', 0.0),
                category_id=cat_map.get(p['category']), 
                asin=p.get('asin')
            )
            db.session.add(pr)
        if (i + 1) % batch_size == 0:
            db.session.commit()
            print(f'  ... {i + 1}/{len(SAMPLE_PRODUCTS)} products created')
    db.session.commit()
    print(f'Products creation complete. Total: {Product.query.count()}')

    # create an admin user
    admin_email = 'admin@example.com'
    if not User.query.filter_by(email=admin_email).first():
        u = User(name='Admin', email=admin_email, role='admin')
        u.set_password('admin123')
        db.session.add(u)
        db.session.commit()
        # create cart
        try:
            c = Cart(user_id=u.id)
            db.session.add(c)
            db.session.commit()
        except Exception:
            db.session.rollback()

    # create a sample customer
    cust_email = 'user@example.com'
    if not User.query.filter_by(email=cust_email).first():
        u = User(name='Sample User', email=cust_email, role='customer')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        try:
            c = Cart(user_id=u.id)
            db.session.add(c)
            db.session.commit()
        except Exception:
            db.session.rollback()

    print('✅ Seeding complete!')
    print(f'📊 Database Stats:')
    print(f'   - Categories: {Category.query.count()}')
    print(f'   - Products: {Product.query.count()}')
    print(f'   - Users: {User.query.count()}')
    print(f'\n🔐 Admin credentials:')
    print(f'   Email: {admin_email}')
    print(f'   Password: admin123')
    print(f'\n👤 Sample user credentials:')
    print(f'   Email: {cust_email}')
    print(f'   Password: password')
