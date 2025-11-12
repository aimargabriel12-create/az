# Bot Telegram Vinted - Détecteur de Bonnes Affaires

Un bot Telegram intelligent qui recherche automatiquement les meilleures annonces Vinted à bas prix avec un potentiel de revente élevé.

## Fonctionnalités

- 🔍 **Recherche intelligente** - Recherche d'articles par mots-clés
- 💰 **Analyse de prix** - Calcule le potentiel de profit et les réductions
- 🔔 **Alertes automatiques** - Abonnez-vous pour recevoir des notifications
- 📊 **Filtrage avancé** - Filtre par prix, marque et potentiel de revente
- 🎯 **Multi-critères** - Support de plusieurs abonnements simultanés

## Installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd vinted-telegram-bot
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Créer un bot Telegram**
   - Ouvrez Telegram et cherchez [@BotFather](https://t.me/botfather)
   - Envoyez `/newbot` et suivez les instructions
   - Copiez le token fourni

4. **Configuration**
   - Copiez `.env.example` vers `.env`
   ```bash
   cp .env.example .env
   ```
   - Éditez `.env` et ajoutez votre token:
   ```
   TELEGRAM_BOT_TOKEN=votre_token_ici
   MAX_PRICE=50
   MIN_DISCOUNT_PERCENT=30
   CHECK_INTERVAL_MINUTES=15
   ```

## Utilisation

### Démarrer le bot

```bash
python vinted_bot.py
```

### Commandes disponibles

- `/start` - Démarrer le bot et voir le menu
- `/search <mot-clé>` - Rechercher des articles (ex: `/search nike air max`)
- `/subscribe <mot-clé>` - S'abonner aux alertes (ex: `/subscribe jordan`)
- `/unsubscribe <mot-clé>` - Se désabonner
- `/mysubscriptions` - Voir vos abonnements actifs
- `/setprice <montant>` - Définir le prix maximum en € (ex: `/setprice 30`)
- `/help` - Afficher l'aide

## Comment ça marche ?

1. **Recherche** - Le bot interroge l'API Vinted selon vos critères
2. **Analyse** - Estime le prix du marché basé sur la marque et l'état
3. **Filtrage** - Ne garde que les bonnes affaires (réduction ≥30%, profit ≥5€)
4. **Notification** - Vous envoie les meilleures offres avec photo et détails

## Calcul du potentiel de profit

Le bot calcule automatiquement:
- **Prix du marché estimé** - Basé sur la marque, l'état et le type d'article
- **Réduction** - Pourcentage d'économie par rapport au prix estimé
- **Profit potentiel** - Après déduction des frais Vinted (15%) et frais d'expédition (~5€)

## Configuration avancée

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `TELEGRAM_BOT_TOKEN` | Token du bot Telegram | - |
| `MAX_PRICE` | Prix maximum en euros | 50 |
| `MIN_DISCOUNT_PERCENT` | Réduction minimale pour considérer une bonne affaire | 30 |
| `CHECK_INTERVAL_MINUTES` | Intervalle de vérification des abonnements | 15 |
| `VINTED_SEARCH_KEYWORDS` | Mots-clés par défaut (séparés par virgules) | nike,adidas,jordan |

### Marques reconnues

**Premium** (multiplicateur x3.0):
- Nike, Adidas, Jordan, Supreme, Gucci, Louis Vuitton, Dior, Chanel, etc.

**Mid-tier** (multiplicateur x2.0):
- Zara, H&M, Pull&Bear, Bershka, Mango, ASOS, Uniqlo

## Exemples d'utilisation

### Recherche simple
```
/search nike
```

### Recherche avec plusieurs mots
```
/search air jordan 1
```

### S'abonner à plusieurs recherches
```
/subscribe nike
/subscribe adidas yeezy
/subscribe supreme
```

### Définir un budget
```
/setprice 25
```

## Limitations

- L'API Vinted peut avoir des limitations de débit
- Les estimations de prix sont basées sur des heuristiques simples
- Le bot ne peut pas acheter automatiquement les articles
- Nécessite une connexion internet stable

## Avertissements

⚠️ **Important**:
- Ce bot est à usage éducatif et personnel
- Respectez les conditions d'utilisation de Vinted
- Ne spammez pas les recherches
- Les prix estimés sont indicatifs

## Support

Pour toute question ou problème:
1. Vérifiez que votre token Telegram est correct
2. Vérifiez votre connexion internet
3. Consultez les logs pour les erreurs

## Licence

MIT
