import os
import time
import requests

# Simple in-memory cache: {url: (timestamp, data)}
_cache = {}
_CACHE_TTL = int(os.environ.get('IMAGE_CACHE_TTL', 86400))

# RapidAPI host for the image conversion tool
RAPIDIMAGE_HOST = os.environ.get('RAPIDIMAGE_HOST', '1688-product2.p.rapidapi.com')
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')


def convert_image_url(url):
    """Convert/normalize an external image URL using the RapidAPI image convert endpoint.
    Returns {'ok': True, 'result': {...}} or {'ok': False, 'error': '...'}
    """
    if not url:
        return {'ok': False, 'error': 'missing url'}

    now = int(time.time())
    cached = _cache.get(url)
    if cached and (now - cached[0] < _CACHE_TTL):
        return {'ok': True, 'from_cache': True, 'result': cached[1]}

    if not RAPIDAPI_KEY:
        return {'ok': False, 'error': 'RAPIDAPI_KEY not set in environment'}

    api_url = f'https://{RAPIDIMAGE_HOST}/1688/tools/image/convert_url'
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': RAPIDIMAGE_HOST,
        'x-rapidapi-key': RAPIDAPI_KEY
    }
    payload = {'url': url}
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        _cache[url] = (now, data)
        return {'ok': True, 'from_cache': False, 'result': data}
    except requests.RequestException as e:
        return {'ok': False, 'error': str(e)}
