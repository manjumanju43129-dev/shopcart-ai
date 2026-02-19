"""Batch-convert product image URLs via RapidAPI image convert endpoint.

Usage:
  Set environment variable RAPIDAPI_KEY to your RapidAPI key first.
  Then run: python batch_convert_images.py --limit 1000

This script loads the Flask app context from `app.create_app()` and updates
`Product.image_url` when a converted URL is returned by the API.

Note: The script will sleep between requests to avoid hitting rate limits.
"""
import os
import time
import argparse
from app import create_app
from database_models import db, Product
from rapid_image import convert_image_url


def main(limit=None, delay=0.5, dry_run=True):
    app = create_app()
    with app.app_context():
        query = Product.query.order_by(Product.id.asc())
        if limit:
            query = query.limit(limit)
        products = query.all()
        print(f"Found {len(products)} products to process")
        updated = 0
        for idx, p in enumerate(products, start=1):
            src = (p.image_url or '').strip()
            if not src:
                print(f"{idx}/{len(products)}: id={p.id} no image, skipping")
                continue
            print(f"{idx}/{len(products)}: id={p.id} converting {src}")
            res = convert_image_url(src)
            if not res.get('ok'):
                print(f"  -> failed: {res.get('error')}")
            else:
                data = res.get('result')
                # Heuristic: look for a URL in top-level keys or nested 'url' fields
                new_url = None
                if isinstance(data, str) and data.startswith('http'):
                    new_url = data
                elif isinstance(data, dict):
                    # common places to find returned URL
                    for k in ('url','converted_url','data','result'):
                        v = data.get(k)
                        if isinstance(v, str) and v.startswith('http'):
                            new_url = v; break
                    if not new_url:
                        # try deeper search
                        def find_url(obj):
                            if isinstance(obj, str) and obj.startswith('http'):
                                return obj
                            if isinstance(obj, dict):
                                for vv in obj.values():
                                    r = find_url(vv)
                                    if r: return r
                            if isinstance(obj, list):
                                for item in obj:
                                    r = find_url(item)
                                    if r: return r
                            return None
                        new_url = find_url(data)

                if new_url:
                    print(f"  -> got converted url: {new_url}")
                    if not dry_run:
                        p.image_url = new_url
                        db.session.add(p)
                        db.session.commit()
                    updated += 1
                else:
                    print("  -> no usable url found in API response; skipping")

            time.sleep(delay)

        print(f"Done. Updated {updated} products (dry_run={dry_run})")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=None, help='Max products to process')
    ap.add_argument('--delay', type=float, default=float(os.environ.get('IMAGE_RATE_DELAY', '0.45')),
                    help='Seconds to sleep between requests')
    ap.add_argument('--apply', action='store_true', help='Apply changes to DB (default is dry-run)')
    args = ap.parse_args()
    if not os.environ.get('RAPIDAPI_KEY'):
        print('RAPIDAPI_KEY not set in environment. Export it before running.')
    main(limit=args.limit, delay=args.delay, dry_run=(not args.apply))
