#!/usr/bin/env python3
"""
Assign product-specific image URLs using keyword-based image services.
Defaults to Unsplash source. Safe dry-run option to preview before committing.

Usage:
  python assign_images_by_keyword.py --dry-run --limit 50 --service unsplash
  python assign_images_by_keyword.py --apply --service loremflickr

Services supported:
 - unsplash: https://source.unsplash.com/600x450/?<keywords>
 - loremflickr: https://loremflickr.com/600/450/<keyword>
"""
import argparse
import re
from app import create_app
from database_models import db, Product, Category

STOPWORDS = set(["and","or","the","with","for","in","on","of","a","an","&"]) 

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--apply', action='store_true')
parser.add_argument('--limit', type=int, default=0, help='Limit number of products to process (0 = all)')
parser.add_argument('--service', choices=['unsplash','loremflickr'], default='unsplash')
args = parser.parse_args()

app = create_app()

def keywords_from_name(name, category_name=None):
    # normalize and split, keep alphanumeric tokens
    if not name:
        name = category_name or 'product'
    s = re.sub(r'[^A-Za-z0-9 ]+', ' ', name)
    parts = [p.strip() for p in s.split() if p.strip()]
    parts = [p for p in parts if p.lower() not in STOPWORDS]
    # prefer nouns/important words: pick first 3
    keys = parts[:3]
    if not keys and category_name:
        keys = [category_name]
    if not keys:
        keys = ['product']
    return keys

with app.app_context():
    query = Product.query.order_by(Product.id)
    total = query.count()
    limit = args.limit or total
    print(f'Total products in DB: {total} — will process up to {limit}')

    processed = 0
    changed = 0
    for p in query.limit(limit).all():
        cat = None
        if p.category_id:
            c = Category.query.get(p.category_id)
            cat = c.name if c else None
        keys = keywords_from_name(p.name, cat)
        if args.service == 'unsplash':
            q = ','.join(keys)
            new_url = f'https://source.unsplash.com/600x450/?{q}'
        else:
            # loremflickr supports single tag; use first keyword
            tag = keys[0].replace(' ', '%20')
            new_url = f'https://loremflickr.com/600/450/{tag}'

        processed += 1
        if p.image_url != new_url:
            print(f'[#{p.id}] {p.name} -> {new_url}')
            if args.apply:
                p.image_url = new_url
                db.session.add(p)
                changed += 1
        else:
            if processed % 50 == 0:
                print(f'[{processed}] No change for id={p.id}')

    if args.apply:
        db.session.commit()
        print(f'Applied changes: {changed} products updated')
    else:
        print(f'Dry-run complete: {processed} processed, {changed} would be changed')

print('Done')
