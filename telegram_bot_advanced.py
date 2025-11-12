import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from telegram.error import TelegramError
from advanced_scraper import AdvancedVintedScraper
from database_manager import DatabaseManager
from datetime import datetime
import json

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

CHANNEL_ID = None
SEARCH_RUNNING = False

class AdvancedVintedBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

        self.scraper = AdvancedVintedScraper()
        self.db = DatabaseManager()
        self.channel_id = int(os.getenv('TELEGRAM_CHANNEL_ID', 0)) if os.getenv('TELEGRAM_CHANNEL_ID') else None
        self.sent_items = set()
        self.search_task = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = (
            "🚀 VINTED LUXURY HUNTER BOT v2.0\n\n"
            "Recherche automatique des meilleures affaires de luxe!\n\n"
            "📋 Commandes:\n"
            "/search_luxury - Rechercher marques de luxe\n"
            "/search_mispriced - Trouver articles mal tarifés\n"
            "/search <keyword> - Chercher par mot-clé\n"
            "/set_channel - Définir canal de diffusion\n"
            "/stats - Voir statistiques\n"
            "/stop - Arrêter les recherches\n"
            "/help - Aide complète"
        )
        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "📖 GUIDE D'UTILISATION COMPLET\n\n"
            "🔍 RECHERCHES:\n"
            "/search_luxury - Recherche articles de marques ultra-luxe\n"
            "/search_mispriced - Trouve articles sous-évalués\n"
            "/search nike,adidas - Multi-recherche simultanée\n\n"
            "📡 CANAL DE DIFFUSION:\n"
            "/set_channel - Envoie tous les articles trouvés au canal\n\n"
            "📊 ANALYSE:\n"
            "/stats - Affiche les trouvailles totales\n"
            "/top_brands - Marques les plus trouvées\n"
            "/recent - Dernières 10 affaires\n\n"
            "⚙️ GESTION:\n"
            "/stop - Arrête les recherches\n"
            "/help - Affiche cette aide\n\n"
            "💡 ASTUCES:\n"
            "• Le bot recherche 24/7 si configuré\n"
            "• Profit = prix revente - frais - expédition\n"
            "• Marques ultra-luxe: x4 du prix d'achat\n"
            "• Articles mal tarifés: réduction >25%"
        )
        await update.message.reply_text(help_text)

    async def set_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if update.effective_chat.type != Chat.CHANNEL:
                await update.message.reply_text(
                    "⚠️ Utilisez cette commande dans le canal où vous voulez recevoir les articles"
                )
                return

            channel_id = update.effective_chat.id
            with open('.env', 'a') as f:
                f.write(f"\nTELEGRAM_CHANNEL_ID={channel_id}\n")

            self.channel_id = channel_id
            logger.info(f"Channel set to {channel_id}")
            await update.message.reply_text(f"✅ Canal défini: {channel_id}")

        except Exception as e:
            logger.error(f"Error setting channel: {e}")
            await update.message.reply_text(f"❌ Erreur: {e}")

    async def search_luxury(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔍 Recherche marques de luxe en cours...")

        try:
            items = await self.scraper.search_luxury_brands(max_price=150)

            if not items:
                await update.message.reply_text("Aucune affaire trouvée pour le moment")
                return

            await update.message.reply_text(f"✅ {len(items)} article(s) de luxe détecté(s)!")

            for item in items[:10]:
                await self._send_item_message(update.effective_chat.id, item, context)
                await asyncio.sleep(0.5)

            if self.channel_id:
                await self._broadcast_to_channel(items[:20], context)

        except Exception as e:
            logger.error(f"Error in search_luxury: {e}")
            await update.message.reply_text(f"❌ Erreur: {e}")

    async def search_mispriced(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔍 Recherche articles mal tarifés...")

        try:
            items = await self.scraper.search_mispriced_items(max_price=100)

            if not items:
                await update.message.reply_text("Aucun article mal tarifé trouvé")
                return

            await update.message.reply_text(f"✅ {len(items)} article(s) sous-évalué(s) trouvé(s)!")

            for item in items[:10]:
                await self._send_item_message(update.effective_chat.id, item, context)
                await asyncio.sleep(0.5)

            if self.channel_id:
                await self._broadcast_to_channel(items[:20], context)

        except Exception as e:
            logger.error(f"Error in search_mispriced: {e}")
            await update.message.reply_text(f"❌ Erreur: {e}")

    async def search_keyword(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(
                "Usage: /search keyword1,keyword2,keyword3\n"
                "Exemple: /search gucci,prada,chanel"
            )
            return

        keywords = ' '.join(context.args).split(',')
        keywords = [kw.strip() for kw in keywords]

        await update.message.reply_text(f"🔍 Recherche {len(keywords)} mots-clés...")

        try:
            items = await self.scraper.search_specific_keywords(keywords, max_price=120)

            if not items:
                await update.message.reply_text("Aucun article trouvé")
                return

            await update.message.reply_text(f"✅ {len(items)} article(s) trouvé(s)!")

            for item in items[:15]:
                await self._send_item_message(update.effective_chat.id, item, context)
                await asyncio.sleep(0.5)

            if self.channel_id:
                await self._broadcast_to_channel(items, context)

        except Exception as e:
            logger.error(f"Error in search_keyword: {e}")
            await update.message.reply_text(f"❌ Erreur: {e}")

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            stats = await self.db.get_stats()

            stats_text = (
                "📊 STATISTIQUES\n\n"
                f"📦 Articles trouvés: {stats['total_found']}\n"
                f"💾 En base de données: {stats['total_tracked']}\n"
                f"💰 Profit moyen: {stats['avg_profit']}€\n\n"
                "Continuez à faire des recherches!"
            )

            await update.message.reply_text(stats_text)

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await update.message.reply_text(f"❌ Erreur: {e}")

    async def _send_item_message(self, chat_id, item: Dict, context):
        try:
            text = (
                f"🔥 OPPORTUNITÉ DÉTECTÉE\n\n"
                f"📦 {item['title']}\n"
                f"👨‍💼 Marque: {item['brand']}\n"
                f"💰 Prix Vinted: {item['price']}€\n"
                f"📈 Prix marché estimé: {item['market_price']}€\n"
                f"📉 Réduction: {item['discount_percent']}%\n"
                f"💵 Profit potentiel: +{item['profit_potential']}€\n"
                f"📏 Taille: {item['size']}\n"
                f"⭐ État: {item['condition']}\n"
                f"👤 Vendeur: {item['seller']}\n"
                f"⭐ Note: {item['seller_rating']}%\n"
                f"📂 Catégorie: {item['category']}\n\n"
                f"🔗 {item['url']}"
            )

            keyboard = [
                [InlineKeyboardButton("Voir l'annonce", url=item['url'])],
                [InlineKeyboardButton("Copier le prix", callback_data=f"copy_{item['price']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if item.get('image_url'):
                try:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=item['image_url'],
                        caption=text[:1024],
                        reply_markup=reply_markup
                    )
                except:
                    await context.bot.send_message(chat_id, text, reply_markup=reply_markup)
            else:
                await context.bot.send_message(chat_id, text, reply_markup=reply_markup)

            item_id = item['id']
            if item_id not in self.sent_items:
                await self.db.add_tracked_item(item)
                await self.db.log_found_item(item, 'manual_search')
                self.sent_items.add(item_id)

        except Exception as e:
            logger.error(f"Error sending item message: {e}")

    async def _broadcast_to_channel(self, items: List[Dict], context):
        if not self.channel_id:
            return

        try:
            for item in items[:10]:
                if item['id'] in self.sent_items:
                    continue

                text = (
                    f"🔥 AFFAIRE DÉTECTÉE!\n\n"
                    f"📦 {item['title']}\n"
                    f"💰 Prix: {item['price']}€ → {item['market_price']}€\n"
                    f"💵 Profit: +{item['profit_potential']}€\n"
                    f"📉 -{item['discount_percent']}%"
                )

                keyboard = [[InlineKeyboardButton("Voir", url=item['url'])]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                try:
                    await context.bot.send_message(
                        chat_id=self.channel_id,
                        text=text,
                        reply_markup=reply_markup
                    )

                    await self.db.add_broadcast(item['id'], self.channel_id, 0)
                    self.sent_items.add(item['id'])
                    await asyncio.sleep(0.3)

                except Exception as e:
                    logger.error(f"Error broadcasting item: {e}")

        except Exception as e:
            logger.error(f"Error in broadcast: {e}")

    async def stop_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        global SEARCH_RUNNING
        SEARCH_RUNNING = False
        await update.message.reply_text("⏹️ Recherches arrêtées")

    def run(self):
        app = Application.builder().token(self.token).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("search_luxury", self.search_luxury))
        app.add_handler(CommandHandler("search_mispriced", self.search_mispriced))
        app.add_handler(CommandHandler("search", self.search_keyword))
        app.add_handler(CommandHandler("set_channel", self.set_channel))
        app.add_handler(CommandHandler("stats", self.stats))
        app.add_handler(CommandHandler("stop", self.stop_search))

        logger.info("Advanced Bot started!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = AdvancedVintedBot()
    bot.run()
