import os
from os.path import join, dirname
from dotenv import load_dotenv

_dotenv_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(_dotenv_path)

BASE_URL = os.environ.get('BASE_URL', "http://localhost:8000")
BASE_CATALOG_URL = BASE_URL + "/api/catalog"
BASE_ORDER_URL = BASE_URL + "/api/order"
CART_URL = BASE_URL + "/api/cart/rasa/"

FALLBACK_LOCATION_ID: str = os.environ.get('FALLBACK_LOCATION_ID', "LA5P7YSWK795X")
FALLBACK_VENDOR_ID: str = os.environ.get('FALLBACK_VENDOR_ID', "MLZ6B533AYQSS")
