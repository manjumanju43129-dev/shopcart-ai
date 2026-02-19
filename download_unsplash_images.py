#!/usr/bin/env python3
"""
Download product images using Unsplash Search API and save to uploads folder.
Usage:
  python download_unsplash_images.py --access-key <KEY> [--dry-run] [--limit N] [--delay 0.5] [--batch 50]

Notes:
- This will perform a search per product using product name and category.
- Unsplash API rate limits apply (typically 50 requests/hour for demo, check your plan).
- Images are saved to the app's UPLOAD_FOLDER and product.image_url is updated to point to /uploads/<filename>.
"""
import argparse
import time
import os
import re
import requests
from urllib.parse import quote_plus
from werkzeug.utils import secure_filename
from app import create_app
from database_models import db, Product, Category
from PIL import Image
import requests
from io import BytesIO

parser = argparse.ArgumentParser()
parser.add_argument('--access-key', required=True, help='Unsplash Access Key')
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--limit', type=int, default=0)
parser.add_argument('--delay', type=float, default=0.5)
parser.add_argument('--batch', type=int, default=50)
args = parser.parse_args()

app = create_app()
with app.app_context():
    upload_folder = app.config.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    query = Product.query.order_by(Product.id)
    total = query.count()
    limit = args.limit or total
    print(f'Total products: {total}, will process: {limit}')

    headers = {'Authorization': f'Client-ID {args.access_key}'}
    processed = 0
    updated = 0

    for p in query.limit(limit).all():
        processed += 1
        # build search query
        cat_name = None
        if p.category_id:
            c = Category.query.get(p.category_id)
            cat_name = c.name if c else None
        qparts = [p.name] + ([cat_name] if cat_name else [])
        q = ' '.join([str(x) for x in qparts if x])
        if not q.strip():
            q = 'product'
        try:
            url = f'https://api.unsplash.com/search/photos?query={quote_plus(q)}&per_page=1'
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f'[{processed}] Search failed for id={p.id} q="{q}" status={r.status_code}')
                time.sleep(args.delay)
                continue
            data = r.json()
            results = data.get('results') or []
            if not results:
                print(f'[{processed}] No image found for id={p.id} q="{q}"')
                time.sleep(args.delay)
                continue
            img_url = results[0]['urls'].get('regular') or results[0]['urls'].get('full')
            if not img_url:
                print(f'[{processed}] No image URL in result for id={p.id} q="{q}"')
                time.sleep(args.delay)
                continue
            # download image
            ext = '.jpg'
            fname_base = f'{p.id}-{re.sub(r"[^A-Za-z0-9]+","-", p.name or "product")}'
            fname = secure_filename(fname_base)[:120] + ext
            dest = os.path.join(upload_folder, fname)
            if not args.dry_run:
                # stream download
                with requests.get(img_url, stream=True, timeout=30) as img_r:
                    if img_r.status_code == 200:
                        with open(dest, 'wb') as fh:
                            for chunk in img_r.iter_content(chunk_size=8192):
                                if chunk:
                                    fh.write(chunk)
                    else:
                        print(f'[{processed}] Failed to download image for id={p.id} (status {img_r.status_code})')
                        time.sleep(args.delay)
                        continue
                # update product image_url
                p.image_url = f'/uploads/{fname}'
                db.session.add(p)
                updated += 1
                if processed % args.batch == 0:
                    db.session.commit()
                    print(f'Committed after {processed} items. Updated so far: {updated}')
            else:
                print(f'[DRY] Would download for id={p.id} -> {dest} (img source {img_url})')
        except Exception as e:
            print(f'[{processed}] Exception for id={p.id}: {e}')
        time.sleep(args.delay)

    if not args.dry_run:
        db.session.commit()
        print(f'Final commit done. Total updated: {updated}')

    print('Done')

# Add lazy loading to images
def lazy_load_images():
    images = get_images()  # Assuming this function fetches image URLs
    for image in images:
        print(f'<img src="{image}" loading="lazy" class="loading" onload="this.classList.remove(\'loading\'); this.classList.add(\'loaded\');">')

# Call the lazy load function
lazy_load_images()

# Function to download and resize images
def download_and_resize_image(url, save_path, size=(300, 300)):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img = img.resize(size, Image.ANTIALIAS)
        img.save(save_path, optimize=True, quality=85)
    else:
        print(f"Failed to download image: {url}")

# Example usage
images = get_images()  # Assuming this function fetches image URLs
for idx, image_url in enumerate(images):
    save_path = os.path.join('assets/images', f'image_{idx}.jpg')
    download_and_resize_image(image_url, save_path)
