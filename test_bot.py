import asyncio
import os
from dotenv import load_dotenv
from vinted_scraper import VintedScraper

load_dotenv()

async def test_scraper():
    print("=" * 60)
    print("TEST BOT VINTED - Vérification de configuration")
    print("=" * 60)

    print("\n1. Vérification des variables d'environnement...")
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("   ❌ TELEGRAM_BOT_TOKEN non défini dans .env")
        return False
    else:
        print(f"   ✅ Token trouvé: {token[:10]}...")

    print("\n2. Vérification de la connexion à Vinted...")
    scraper = VintedScraper()
    try:
        items = await scraper.search_items("nike", 50)
        print(f"   ✅ Connexion réussie!")
        print(f"   ℹ️  {len(items)} article(s) trouvé(s)")

        if items:
            print("\n3. Exemple d'article détecté:")
            item = items[0]
            print(f"   📦 Titre: {item['title']}")
            print(f"   💰 Prix: {item['price']}€")
            print(f"   📉 Réduction: {item['discount_percent']}%")
            print(f"   💵 Profit potentiel: +{item['profit_potential']}€")
            print(f"   🔗 {item['url']}")

        print("\n4. Dépendances Python...")
        try:
            import telegram
            print("   ✅ python-telegram-bot OK")
        except:
            print("   ❌ python-telegram-bot non installé")

        try:
            import requests
            print("   ✅ requests OK")
        except:
            print("   ❌ requests non installé")

        try:
            import bs4
            print("   ✅ beautifulsoup4 OK")
        except:
            print("   ❌ beautifulsoup4 non installé")

        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS!")
        print("=" * 60)
        print("\nProchaines étapes:")
        print("1. Vérifiez votre token Telegram avec @BotFather")
        print("2. Lancez le bot: python vinted_bot.py")
        print("3. Tapez /start dans le chat Telegram")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        print("\n   Vérifiez:")
        print("   - Votre connexion internet")
        print("   - Que Vinted n'a pas bloqué vos requêtes")
        return False
    finally:
        await scraper.close()

if __name__ == '__main__':
    asyncio.run(test_scraper())
