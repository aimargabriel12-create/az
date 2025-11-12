import aiohttp
import asyncio
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
import json
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class AdvancedVintedScraper:
    def __init__(self):
        self.base_url = "https://www.vinted.fr"
        self.headers = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)'
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
        ]
        self.session = None

    async def get_session(self):
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
            self.session = aiohttp.ClientSession(connector=connector)
        return self.session

    async def search_luxury_brands(self, max_price: float = 100) -> List[Dict]:
        luxury_brands = [
            'gucci', 'louis vuitton', 'prada', 'chanel', 'dior', 'fendi',
            'balenciaga', 'yves saint laurent', 'valentino', 'givenchy',
            'burberry', 'coach', 'michael kors', 'versace', 'dolce gabbana'
        ]

        all_items = []
        session = await self.get_session()

        tasks = [
            self._search_keyword(session, brand, max_price)
            for brand in luxury_brands
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
            await asyncio.sleep(0.5)

        return all_items

    async def search_mispriced_items(self, max_price: float = 80) -> List[Dict]:
        keywords = [
            'original', 'authentic', 'rare', 'limited edition',
            'vintage', 'deadstock', 'new with tags'
        ]

        all_items = []
        session = await self.get_session()

        tasks = [
            self._search_keyword(session, kw, max_price)
            for kw in keywords
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
            await asyncio.sleep(0.5)

        return all_items

    async def search_specific_keywords(self, keywords: List[str], max_price: float = 100) -> List[Dict]:
        all_items = []
        session = await self.get_session()

        tasks = [
            self._search_keyword(session, kw, max_price)
            for kw in keywords
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
            await asyncio.sleep(0.5)

        return all_items

    async def _search_keyword(self, session, keyword: str, max_price: float) -> List[Dict]:
        try:
            search_url = f"{self.base_url}/api/v2/catalog/items"
            params = {
                'search_text': keyword,
                'price_to': int(max_price),
                'order': 'newest_first',
                'per_page': 50
            }

            headers = random.choice(self.headers)
            headers['Accept'] = 'application/json'

            async with session.get(search_url, params=params, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"Search failed for '{keyword}': {response.status}")
                    return []

                data = await response.json()
                items = data.get('items', [])

                filtered_items = []
                for item in items:
                    processed_item = await self._process_item(item, keyword)
                    if processed_item and self._is_opportunity(processed_item):
                        filtered_items.append(processed_item)

                logger.info(f"Found {len(filtered_items)} opportunities for '{keyword}'")
                return filtered_items

        except asyncio.TimeoutError:
            logger.warning(f"Timeout searching for '{keyword}'")
            return []
        except Exception as e:
            logger.error(f"Error searching '{keyword}': {e}")
            return []

    async def _process_item(self, item: Dict, keyword: str) -> Dict:
        try:
            price = float(item.get('price', 0))
            title = item.get('title', '')
            item_id = item.get('id', '')

            brand_title = item.get('brand_title', '')
            size_title = item.get('size_title', '')
            status = item.get('status', '')

            photo = item.get('photo')
            image_url = photo.get('full_size_url', '') if photo else ''

            user = item.get('user', {})
            seller = user.get('login', 'N/A')
            seller_rating = user.get('average_positive_feedback', 0)

            url = f"{self.base_url}/items/{item_id}"

            market_price = self._estimate_market_price(title, brand_title, price)
            discount_percent = self._calculate_discount(price, market_price)
            profit_potential = self._calculate_profit_potential(price, market_price)

            return {
                'id': item_id,
                'title': title,
                'price': price,
                'brand': brand_title,
                'size': size_title,
                'condition': status,
                'seller': seller,
                'seller_rating': seller_rating,
                'image_url': image_url,
                'url': url,
                'market_price': market_price,
                'discount_percent': discount_percent,
                'profit_potential': profit_potential,
                'category': self._detect_category(title),
                'posted_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing item: {e}")
            return None

    def _estimate_market_price(self, title: str, brand: str, current_price: float) -> float:
        title_lower = title.lower()
        brand_lower = (brand or '').lower()

        ultra_luxury = ['louis vuitton', 'gucci', 'prada', 'chanel', 'dior']
        luxury = ['yves saint laurent', 'valentino', 'givenchy', 'fendi', 'balenciaga']
        premium = ['nike', 'adidas', 'jordan', 'supreme', 'off-white']
        mid_tier = ['zara', 'h&m', 'uniqlo']

        multiplier = 2.5

        if any(brand in brand_lower or brand in title_lower for brand in ultra_luxury):
            multiplier = 4.0
        elif any(brand in brand_lower or brand in title_lower for brand in luxury):
            multiplier = 3.5
        elif any(brand in brand_lower or brand in title_lower for brand in premium):
            multiplier = 3.0
        elif any(brand in brand_lower or brand in title_lower for brand in mid_tier):
            multiplier = 2.0

        condition_bonus = 0
        if 'neuf' in title_lower or 'jamais porté' in title_lower or 'new' in title_lower:
            condition_bonus = 0.8
        elif 'excellent' in title_lower or 'comme neuf' in title_lower:
            condition_bonus = 0.5

        estimated = (current_price * multiplier) + condition_bonus

        return round(estimated, 2)

    def _calculate_discount(self, current_price: float, market_price: float) -> float:
        if market_price <= 0:
            return 0
        discount = ((market_price - current_price) / market_price) * 100
        return round(max(0, discount), 1)

    def _calculate_profit_potential(self, buy_price: float, market_price: float) -> float:
        vinted_fees = 0.125
        shipping = 5
        depop_fees = 0.105

        conservative_resell = market_price * 0.75

        revenue = conservative_resell * (1 - depop_fees)
        profit = revenue - buy_price - shipping

        return round(max(0, profit), 2)

    def _is_opportunity(self, item: Dict) -> bool:
        discount = item.get('discount_percent', 0)
        profit = item.get('profit_potential', 0)
        market_price = item.get('market_price', 0)
        current_price = item.get('price', 0)

        if profit < 10:
            return False

        if discount < 25:
            return False

        if market_price <= current_price * 1.5:
            return False

        return True

    def _detect_category(self, title: str) -> str:
        title_lower = title.lower()

        if any(word in title_lower for word in ['shoe', 'sneaker', 'chaussure', 'baskets', 'boots']):
            return 'shoes'
        elif any(word in title_lower for word in ['bag', 'sac', 'backpack', 'purse']):
            return 'bags'
        elif any(word in title_lower for word in ['jacket', 'coat', 'hoodie', 'blouson', 'manteau']):
            return 'outerwear'
        elif any(word in title_lower for word in ['shirt', 't-shirt', 'tee', 'chemise']):
            return 'tops'
        elif any(word in title_lower for word in ['pants', 'jeans', 'trousers', 'pantalon']):
            return 'bottoms'
        elif any(word in title_lower for word in ['watch', 'montre']):
            return 'accessories'

        return 'other'

    async def close(self):
        if self.session:
            await self.session.close()
