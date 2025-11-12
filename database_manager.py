import os
import logging
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        supabase_url = os.getenv('VITE_SUPABASE_URL')
        supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in .env")

        self.client: Client = create_client(supabase_url, supabase_key)

    async def add_tracked_item(self, item: Dict) -> Optional[str]:
        try:
            data = {
                'vinted_id': str(item['id']),
                'title': item['title'],
                'price': float(item['price']),
                'brand': item.get('brand', ''),
                'size': item.get('size', ''),
                'condition': item.get('condition', ''),
                'url': item['url'],
                'image_url': item.get('image_url', ''),
                'estimated_resell_price': float(item.get('market_price', 0)),
                'profit_margin': float(item.get('profit_potential', 0)),
                'category': item.get('category', 'other'),
                'seller_rating': float(item.get('seller_rating', 0)),
                'posted_at': item.get('posted_at'),
                'is_available': True
            }

            response = self.client.table('tracked_items').insert(data).execute()

            if response.data:
                item_id = response.data[0]['id']
                logger.info(f"Item added: {item_id}")
                return item_id

            return None

        except Exception as e:
            logger.error(f"Error adding tracked item: {e}")
            return None

    async def log_found_item(self, item: Dict, keyword: str):
        try:
            data = {
                'vinted_id': str(item['id']),
                'title': item['title'],
                'price': float(item['price']),
                'brand': item.get('brand', ''),
                'market_price': float(item.get('market_price', 0)),
                'profit_margin': float(item.get('profit_potential', 0)),
                'search_keyword': keyword,
                'found_at': datetime.now().isoformat()
            }

            self.client.table('found_items_log').insert(data).execute()
            logger.info(f"Item logged: {item['title']}")

        except Exception as e:
            logger.error(f"Error logging found item: {e}")

    async def get_recent_items(self, hours: int = 1, limit: int = 50) -> List[Dict]:
        try:
            since = (datetime.now() - timedelta(hours=hours)).isoformat()

            response = self.client.table('tracked_items').select(
                '*'
            ).gte('discovered_at', since).order('discovered_at', desc=True).limit(limit).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error getting recent items: {e}")
            return []

    async def get_items_by_profit(self, min_profit: float = 15, limit: int = 50) -> List[Dict]:
        try:
            response = self.client.table('tracked_items').select(
                '*'
            ).gte('profit_margin', min_profit).order('profit_margin', desc=True).limit(limit).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error getting items by profit: {e}")
            return []

    async def get_items_by_brand(self, brand: str, limit: int = 20) -> List[Dict]:
        try:
            response = self.client.table('tracked_items').select(
                '*'
            ).ilike('brand', f'%{brand}%').order('discovered_at', desc=True).limit(limit).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error getting items by brand: {e}")
            return []

    async def add_broadcast(self, item_id: str, channel_id: int, message_id: int):
        try:
            data = {
                'item_id': item_id,
                'channel_id': channel_id,
                'message_id': message_id,
                'broadcasted_at': datetime.now().isoformat()
            }

            self.client.table('channel_broadcasts').insert(data).execute()
            logger.info(f"Broadcast logged: item {item_id} to channel {channel_id}")

        except Exception as e:
            logger.error(f"Error logging broadcast: {e}")

    async def check_item_exists(self, vinted_id: str) -> bool:
        try:
            response = self.client.table('tracked_items').select(
                'id'
            ).eq('vinted_id', str(vinted_id)).execute()

            return len(response.data) > 0

        except Exception as e:
            logger.error(f"Error checking item existence: {e}")
            return False

    async def get_stats(self) -> Dict:
        try:
            total_items = self.client.table('tracked_items').select('id', count='exact').execute()
            total_found = self.client.table('found_items_log').select('id', count='exact').execute()

            avg_profit = self.client.table('tracked_items').select('profit_margin').execute()
            avg_profit_value = 0
            if avg_profit.data:
                profits = [item['profit_margin'] for item in avg_profit.data if item['profit_margin']]
                avg_profit_value = sum(profits) / len(profits) if profits else 0

            return {
                'total_tracked': total_items.count if total_items.count else 0,
                'total_found': total_found.count if total_found.count else 0,
                'avg_profit': round(avg_profit_value, 2)
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_tracked': 0, 'total_found': 0, 'avg_profit': 0}
