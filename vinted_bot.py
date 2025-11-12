import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from vinted_scraper import VintedScraper

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VintedBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.scraper = VintedScraper()
        self.user_subscriptions = {}
        self.sent_items = set()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = (
            "🤖 Bienvenue sur le Bot Vinted Deal Finder!\n\n"
            "Je recherche les meilleures affaires Vinted pour la revente.\n\n"
            "Commandes disponibles:\n"
            "/search <mot-clé> - Rechercher des articles\n"
            "/subscribe <mot-clé> - S'abonner aux alertes\n"
            "/unsubscribe <mot-clé> - Se désabonner\n"
            "/mysubscriptions - Voir vos abonnements\n"
            "/setprice <max> - Définir le prix maximum (€)\n"
            "/help - Afficher l'aide"
        )
        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "📖 Guide d'utilisation:\n\n"
            "1. /search nike - Recherche instantanée d'articles Nike\n"
            "2. /subscribe jordan - Recevez des alertes pour les articles Jordan\n"
            "3. /setprice 30 - Ne voir que les articles jusqu'à 30€\n\n"
            "Le bot analyse les prix du marché et vous envoie uniquement "
            "les bonnes affaires avec un potentiel de revente élevé."
        )
        await update.message.reply_text(help_text)

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /search <mot-clé>\nExemple: /search nike air max")
            return

        keyword = ' '.join(context.args)
        chat_id = update.effective_chat.id

        await update.message.reply_text(f"🔍 Recherche en cours pour '{keyword}'...")

        max_price = self.user_subscriptions.get(chat_id, {}).get('max_price',
                                                                  float(os.getenv('MAX_PRICE', 50)))

        items = await self.scraper.search_items(keyword, max_price)

        if not items:
            await update.message.reply_text(f"Aucune bonne affaire trouvée pour '{keyword}'")
            return

        await update.message.reply_text(f"✅ {len(items)} bonne(s) affaire(s) trouvée(s)!")

        for item in items[:5]:
            await self.send_item(chat_id, item, context)

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /subscribe <mot-clé>\nExemple: /subscribe nike")
            return

        keyword = ' '.join(context.args)
        chat_id = update.effective_chat.id

        if chat_id not in self.user_subscriptions:
            self.user_subscriptions[chat_id] = {'keywords': [], 'max_price': float(os.getenv('MAX_PRICE', 50))}

        if keyword not in self.user_subscriptions[chat_id]['keywords']:
            self.user_subscriptions[chat_id]['keywords'].append(keyword)
            await update.message.reply_text(f"✅ Abonnement activé pour '{keyword}'")
        else:
            await update.message.reply_text(f"Vous êtes déjà abonné à '{keyword}'")

    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /unsubscribe <mot-clé>")
            return

        keyword = ' '.join(context.args)
        chat_id = update.effective_chat.id

        if chat_id in self.user_subscriptions and keyword in self.user_subscriptions[chat_id]['keywords']:
            self.user_subscriptions[chat_id]['keywords'].remove(keyword)
            await update.message.reply_text(f"❌ Désabonné de '{keyword}'")
        else:
            await update.message.reply_text(f"Vous n'êtes pas abonné à '{keyword}'")

    async def my_subscriptions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        if chat_id not in self.user_subscriptions or not self.user_subscriptions[chat_id]['keywords']:
            await update.message.reply_text("Vous n'avez aucun abonnement actif.")
            return

        keywords = self.user_subscriptions[chat_id]['keywords']
        max_price = self.user_subscriptions[chat_id]['max_price']

        text = f"📋 Vos abonnements:\n\n"
        for kw in keywords:
            text += f"• {kw}\n"
        text += f"\n💰 Prix maximum: {max_price}€"

        await update.message.reply_text(text)

    async def set_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("Usage: /setprice <montant>\nExemple: /setprice 30")
            return

        max_price = float(context.args[0])
        chat_id = update.effective_chat.id

        if chat_id not in self.user_subscriptions:
            self.user_subscriptions[chat_id] = {'keywords': [], 'max_price': max_price}
        else:
            self.user_subscriptions[chat_id]['max_price'] = max_price

        await update.message.reply_text(f"✅ Prix maximum défini à {max_price}€")

    async def send_item(self, chat_id, item, context):
        discount = item.get('discount_percent', 0)
        profit_potential = item.get('profit_potential', 0)

        text = (
            f"🔥 BONNE AFFAIRE DÉTECTÉE\n\n"
            f"📦 {item['title']}\n"
            f"💰 Prix: {item['price']}€\n"
            f"📉 Réduction estimée: {discount}%\n"
            f"💵 Potentiel de profit: +{profit_potential}€\n"
            f"👤 Vendeur: {item.get('seller', 'N/A')}\n"
            f"📍 Taille: {item.get('size', 'N/A')}\n"
            f"⭐ État: {item.get('condition', 'N/A')}\n\n"
            f"🔗 {item['url']}"
        )

        keyboard = [
            [InlineKeyboardButton("Voir l'annonce", url=item['url'])]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            if item.get('image_url'):
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=item['image_url'],
                    caption=text,
                    reply_markup=reply_markup
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Error sending item: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )

    async def check_subscriptions(self, context: ContextTypes.DEFAULT_TYPE):
        for chat_id, data in self.user_subscriptions.items():
            for keyword in data['keywords']:
                try:
                    items = await self.scraper.search_items(keyword, data['max_price'])

                    for item in items:
                        item_id = item['id']
                        if item_id not in self.sent_items:
                            await self.send_item(chat_id, item, context)
                            self.sent_items.add(item_id)
                            await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Error checking subscription for {chat_id}: {e}")

                await asyncio.sleep(2)

    def run(self):
        app = Application.builder().token(self.token).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("search", self.search))
        app.add_handler(CommandHandler("subscribe", self.subscribe))
        app.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        app.add_handler(CommandHandler("mysubscriptions", self.my_subscriptions))
        app.add_handler(CommandHandler("setprice", self.set_price))

        job_queue = app.job_queue
        check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', 15)) * 60
        job_queue.run_repeating(self.check_subscriptions, interval=check_interval, first=10)

        logger.info("Bot started!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = VintedBot()
    bot.run()
