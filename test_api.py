#!/usr/bin/env python3
import requests
import json

print("Testing /api/products endpoint...")
r = requests.get('http://localhost:10000/api/products')
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")
print(f"Content length: {len(r.text)} bytes")

try:
    data = r.json()
    print(f"Data type: {type(data)}")
    print(f"Is list: {isinstance(data, list)}")
    print(f"Products count: {len(data) if isinstance(data, list) else 'N/A'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"\nFirst product keys: {data[0].keys()}")
        print(f"First product: {json.dumps(data[0], indent=2)}")
    else:
        print(f"Data: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error parsing JSON: {e}")
    print(f"Response text (first 1000 chars): {r.text[:1000]}")

