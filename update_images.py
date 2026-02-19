#!/usr/bin/env python3
"""
Assign unique image URLs to products using picsum.photos seeded images.
Usage:
  python update_images.py [--dry-run] [--batch N]
By default it applies changes. Use --dry-run to preview.
"""
import argparse
from app import create_app
from database_models import db, Product, Category

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true', help='Do not commit changes')
parser.add_argument('--batch', type=int, default=100, help='Commit batch size')
args = parser.parse_args()

app = create_app()
with app.app_context():
    products = Product.query.order_by(Product.id).all()
    total = len(products)
    print(f'Found {total} products')
    if total == 0:
        print('No products to update.')
        exit(0)

    changed = 0
    for i, p in enumerate(products, start=1):
        # create a stable seed using id and cleaned name
        name_clean = ''.join(c for c in (p.name or '') if c.isalnum())
        seed = f"{p.id}-{name_clean or 'product'}"
        new_url = f"https://picsum.photos/seed/{seed}/600/450"
        if p.image_url != new_url:
            print(f'[{i}/{total}] Updating Product id={p.id} name="{p.name}" -> {new_url}')
            p.image_url = new_url
            changed += 1
        else:
            if i % 50 == 0:
                print(f'[{i}/{total}] No change for id={p.id}')

        if not args.dry_run and (i % args.batch == 0):
            db.session.commit()
            print(f'Committed {i} items so far...')

    if not args.dry_run:
        db.session.commit()
        print('Final commit done.')

    print(f'Total products processed: {total}, changed: {changed}')
    if args.dry_run:
        print('Dry-run completed. No changes were committed.')
