import os
import time
import requests

# Simple in-memory cache: {asin: (timestamp, data)}
_cache = {}
_CACHE_TTL = int(os.environ.get('REVIEWS_CACHE_TTL', 3600))

RAPIDAPI_HOST = 'real-time-amazon-data.p.rapidapi.com'
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')


def get_reviews(asin, country='US'):
    """Fetch top reviews for a product ASIN from RapidAPI service.
    Returns dict {ok: True, reviews: [...] } or {ok: False, error: '...'}
    """
    if not asin:
        return {'ok': False, 'error': 'missing asin'}

    now = int(time.time())
    cached = _cache.get(asin)
    if cached and (now - cached[0] < _CACHE_TTL):
        return {'ok': True, 'from_cache': True, 'reviews': cached[1]}

    if not RAPIDAPI_KEY:
        return {'ok': False, 'error': 'RAPIDAPI_KEY not set in environment'}

    url = f'https://{RAPIDAPI_HOST}/top-product-reviews'
    params = {'asin': asin, 'country': country}
    headers = {
        'x-rapidapi-host': RAPIDAPI_HOST,
        'x-rapidapi-key': RAPIDAPI_KEY
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        # store in cache
        _cache[asin] = (now, data)
        return {'ok': True, 'from_cache': False, 'reviews': data}
    except requests.RequestException as e:
        return {'ok': False, 'error': str(e)}
