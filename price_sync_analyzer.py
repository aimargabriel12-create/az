import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class PriceSyncAnalyzer:
    """
    Analyzes market prices and suggests resale prices across multiple platforms
    """

    PLATFORM_FEES = {
        'vinted': 0.125,
        'depop': 0.105,
        'vestiaire': 0.15,
        'grailed': 0.08,
    }

    PLATFORM_MARGINS = {
        'vinted': 1.0,
        'depop': 1.3,
        'vestiaire': 1.4,
        'grailed': 1.5,
    }

    @staticmethod
    def analyze_item_price(item: Dict) -> Dict:
        """
        Analyze item and provide comprehensive pricing recommendations
        """
        vinted_price = float(item['price'])
        market_price = float(item.get('market_price', vinted_price * 2.5))
        brand = item.get('brand', '').lower()
        condition = item.get('condition', 'bon').lower()
        category = item.get('category', 'other')

        condition_factor = PriceSyncAnalyzer._get_condition_factor(condition)
        category_multiplier = PriceSyncAnalyzer._get_category_multiplier(category)
        brand_multiplier = PriceSyncAnalyzer._get_brand_multiplier(brand)

        adjusted_market_price = market_price * condition_factor * category_multiplier

        recommendations = {
            'item_id': item['id'],
            'item_title': item['title'],
            'current_vinted_price': vinted_price,
            'estimated_market_price': round(adjusted_market_price, 2),
            'platforms': {},
            'best_platform': None,
            'best_profit': 0,
            'shipping_cost': 5
        }

        shipping_cost = 5

        for platform, fee_rate in PriceSyncAnalyzer.PLATFORM_FEES.items():
            margin = PriceSyncAnalyzer.PLATFORM_MARGINS.get(platform, 1.0)
            resell_price = adjusted_market_price * margin
            net_revenue = resell_price * (1 - fee_rate)
            profit = net_revenue - vinted_price - shipping_cost

            recommendations['platforms'][platform] = {
                'resell_price': round(resell_price, 2),
                'net_revenue': round(net_revenue, 2),
                'profit': round(max(0, profit), 2),
                'fee_rate': fee_rate * 100,
                'margin_multiplier': margin
            }

            if profit > recommendations['best_profit']:
                recommendations['best_profit'] = profit
                recommendations['best_platform'] = platform

        return recommendations

    @staticmethod
    def _get_condition_factor(condition: str) -> float:
        """Get price multiplier based on condition"""
        condition_map = {
            'neuf': 1.0,
            'new': 1.0,
            'excellent': 0.85,
            'tres bon': 0.75,
            'bon': 0.65,
            'acceptable': 0.5,
            'used': 0.55,
        }

        for key, factor in condition_map.items():
            if key in condition.lower():
                return factor

        return 0.65

    @staticmethod
    def _get_category_multiplier(category: str) -> float:
        """Get multiplier based on product category"""
        category_map = {
            'shoes': 1.1,
            'bags': 1.2,
            'accessories': 0.9,
            'outerwear': 1.0,
            'tops': 0.8,
            'bottoms': 0.85,
            'watches': 1.3,
            'other': 1.0
        }

        return category_map.get(category, 1.0)

    @staticmethod
    def _get_brand_multiplier(brand: str) -> float:
        """Get multiplier based on brand prestige"""
        ultra_luxury = {
            'louis vuitton': 1.3,
            'gucci': 1.25,
            'prada': 1.25,
            'chanel': 1.3,
            'dior': 1.2,
            'hermes': 1.4,
            'fendi': 1.15,
            'balenciaga': 1.15,
            'yves saint laurent': 1.1,
            'valentino': 1.1,
            'givenchy': 1.05
        }

        luxury = {
            'burberry': 1.05,
            'coach': 0.95,
            'michael kors': 0.9,
            'versace': 1.05,
            'dolce gabbana': 1.0
        }

        premium = {
            'nike': 1.0,
            'adidas': 0.95,
            'jordan': 1.05,
            'supreme': 1.2,
            'off-white': 1.15
        }

        brand_lower = brand.lower()

        for brand_name, multiplier in ultra_luxury.items():
            if brand_name in brand_lower:
                return multiplier

        for brand_name, multiplier in luxury.items():
            if brand_name in brand_lower:
                return multiplier

        for brand_name, multiplier in premium.items():
            if brand_name in brand_lower:
                return multiplier

        return 1.0

    @staticmethod
    def get_price_timeline(items: List[Dict]) -> Dict:
        """
        Analyze price trends for items with same brand/category
        """
        by_brand = {}

        for item in items:
            brand = item.get('brand', 'unknown')
            if brand not in by_brand:
                by_brand[brand] = []

            by_brand[brand].append({
                'price': item['price'],
                'timestamp': item.get('discovered_at', datetime.now().isoformat())
            })

        timeline = {}
        for brand, prices in by_brand.items():
            sorted_prices = sorted(prices, key=lambda x: x['timestamp'])
            if len(sorted_prices) > 1:
                first_price = sorted_prices[0]['price']
                last_price = sorted_prices[-1]['price']
                avg_price = sum(p['price'] for p in sorted_prices) / len(sorted_prices)

                timeline[brand] = {
                    'first_seen_price': first_price,
                    'latest_price': last_price,
                    'average_price': round(avg_price, 2),
                    'trend': 'up' if last_price > first_price else 'down',
                    'count': len(sorted_prices)
                }

        return timeline

    @staticmethod
    def format_recommendation(recommendation: Dict) -> str:
        """Format recommendation as readable string"""
        text = (
            f"💼 ANALYSE DE PRIX\n\n"
            f"📦 {recommendation['item_title']}\n"
            f"💰 Prix d'achat (Vinted): {recommendation['current_vinted_price']}€\n"
            f"📈 Prix marché: {recommendation['estimated_market_price']}€\n\n"
            f"🎯 MEILLEURES PLATEFORMES DE REVENTE:\n\n"
        )

        sorted_platforms = sorted(
            recommendation['platforms'].items(),
            key=lambda x: x[1]['profit'],
            reverse=True
        )

        for platform, data in sorted_platforms[:3]:
            emoji = "🥇" if platform == recommendation['best_platform'] else "•"
            text += (
                f"{emoji} {platform.upper()}\n"
                f"   Prix de revente: {data['resell_price']}€\n"
                f"   Profit net: +{data['profit']}€\n"
                f"   (Frais: {data['fee_rate']:.1f}%)\n\n"
            )

        best_data = recommendation['platforms'][recommendation['best_platform']]
        text += (
            f"✅ RECOMMANDATION: {recommendation['best_platform'].upper()}\n"
            f"💵 Profit maximal: +{recommendation['best_profit']}€\n"
            f"📊 ROI: {round((recommendation['best_profit'] / recommendation['current_vinted_price'] * 100), 1)}%"
        )

        return text
