import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

MAX_PRICE = float(os.getenv('MAX_PRICE', 50))
MIN_DISCOUNT_PERCENT = float(os.getenv('MIN_DISCOUNT_PERCENT', 30))
MIN_PROFIT = float(os.getenv('MIN_PROFIT', 5))

CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', 15))

VINTED_BASE_URL = "https://www.vinted.fr"

PREMIUM_BRANDS = [
    'nike', 'adidas', 'jordan', 'supreme', 'gucci', 'louis vuitton',
    'dior', 'chanel', 'prada', 'yeezy', 'off-white', 'balenciaga'
]

MID_TIER_BRANDS = [
    'zara', 'h&m', 'pull&bear', 'bershka', 'stradivarius',
    'mango', 'asos', 'uniqlo'
]

SEARCH_KEYWORDS = os.getenv('VINTED_SEARCH_KEYWORDS', 'nike,adidas,jordan').split(',')
