import aiohttp
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
import json
import re

logger = logging.getLogger(__name__)

class VintedScraper:
    def __init__(self):
        self.base_url = "https://www.vinted.fr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.session = None

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def search_items(self, keyword: str, max_price: float) -> List[Dict]:
        try:
            session = await self.get_session()

            search_url = f"{self.base_url}/api/v2/catalog/items"
            params = {
                'search_text': keyword,
                'price_to': int(max_price),
                'order': 'newest_first',
                'per_page': 20
            }

            async with session.get(search_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Search failed with status {response.status}")
                    return []

                data = await response.json()
                items = data.get('items', [])

                filtered_items = []
                for item in items:
                    processed_item = await self.process_item(item, keyword)
                    if processed_item and self.is_good_deal(processed_item):
                        filtered_items.append(processed_item)

                return filtered_items

        except Exception as e:
            logger.error(f"Error searching items: {e}")
            return []

    async def process_item(self, item: Dict, keyword: str) -> Dict:
        try:
            price = float(item.get('price', '0'))
            title = item.get('title', '')
            item_id = item.get('id', '')

            brand_title = item.get('brand_title', '')
            size_title = item.get('size_title', '')
            status = item.get('status', '')

            photo = item.get('photo')
            image_url = photo.get('full_size_url', '') if photo else ''

            user = item.get('user', {})
            seller = user.get('login', 'N/A')

            url = f"{self.base_url}/items/{item_id}"

            estimated_market_price = self.estimate_market_price(title, brand_title, price)
            discount_percent = self.calculate_discount(price, estimated_market_price)
            profit_potential = self.calculate_profit_potential(price, estimated_market_price)

            return {
                'id': item_id,
                'title': title,
                'price': price,
                'brand': brand_title,
                'size': size_title,
                'condition': status,
                'seller': seller,
                'image_url': image_url,
                'url': url,
                'estimated_market_price': estimated_market_price,
                'discount_percent': discount_percent,
                'profit_potential': profit_potential
            }

        except Exception as e:
            logger.error(f"Error processing item: {e}")
            return None

    def estimate_market_price(self, title: str, brand: str, current_price: float) -> float:
        title_lower = title.lower()
        brand_lower = brand.lower() if brand else ''

        premium_brands = ['nike', 'adidas', 'jordan', 'supreme', 'gucci', 'louis vuitton', 'dior']
        mid_brands = ['zara', 'h&m', 'pull&bear', 'bershka', 'stradivarius']

        multiplier = 2.5

        if any(pb in brand_lower or pb in title_lower for pb in premium_brands):
            multiplier = 3.0
        elif any(mb in brand_lower or mb in title_lower for mb in mid_brands):
            multiplier = 2.0

        if 'neuf' in title_lower or 'jamais porté' in title_lower:
            multiplier += 0.5

        estimated_price = current_price * multiplier

        return round(estimated_price, 2)

    def calculate_discount(self, current_price: float, market_price: float) -> float:
        if market_price <= 0:
            return 0

        discount = ((market_price - current_price) / market_price) * 100
        return round(max(0, discount), 1)

    def calculate_profit_potential(self, buy_price: float, estimated_sell_price: float) -> float:
        fees_percent = 0.15
        shipping_cost = 5

        potential_revenue = estimated_sell_price * (1 - fees_percent)
        profit = potential_revenue - buy_price - shipping_cost

        return round(max(0, profit), 2)

    def is_good_deal(self, item: Dict) -> bool:
        min_discount = 30
        min_profit = 5

        discount = item.get('discount_percent', 0)
        profit = item.get('profit_potential', 0)

        return discount >= min_discount and profit >= min_profit

    async def close(self):
        if self.session:
            await self.session.close()
