# 🚀 Guide Complet d'Installation & Utilisation - Bot Vinted Luxury Hunter v2.0

## Table des matières
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Utilisation](#utilisation)
4. [Synchronisation des Prix](#synchronisation-des-prix)
5. [Troubleshooting](#troubleshooting)

---

## Installation

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)
- Un compte Telegram
- Un compte Supabase (fourni)

### Étape 1: Télécharger le projet
```bash
cd vinted-bot
```

### Étape 2: Installer les dépendances
```bash
pip install -r requirements.txt
```

Dépendances requises:
- `python-telegram-bot==20.7` - Bot Telegram
- `requests==2.31.0` - Requêtes HTTP
- `beautifulsoup4==4.12.2` - Web scraping
- `aiohttp==3.9.1` - Requêtes asynchrones
- `python-dotenv==1.0.0` - Gestion des variables d'env
- `supabase==2.1.0` - Base de données

### Étape 3: Créer un bot Telegram

1. Ouvrir Telegram et chercher **@BotFather**
2. Envoyer `/newbot`
3. Suivre les instructions:
   - Nom du bot (ex: `VintedLuxuryHunter`)
   - Username du bot (ex: `vinted_luxury_bot`) - doit être unique
4. Copier le **token API** fourni (ex: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Étape 4: Configurer le fichier .env

1. Copier `.env.example` vers `.env`:
```bash
cp .env.example .env
```

2. Éditer `.env` et compléter:

```env
# Token du bot Telegram (obligatoire)
TELEGRAM_BOT_TOKEN=votre_token_bot_ici

# Supabase (fourni automatiquement)
VITE_SUPABASE_URL=https://solwtszgtgqlngaakeso.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Canal Telegram pour diffusion (optionnel)
TELEGRAM_CHANNEL_ID=-1001234567890

# Configuration de recherche
MAX_PRICE=150
MIN_PROFIT=10
SEARCH_INTERVAL_MINUTES=5
```

### Étape 5: Créer un canal Telegram (optionnel mais recommandé)

1. Créer un nouveau canal Telegram
2. Ajouter le bot au canal en tant qu'administrateur
3. Obtenir l'ID du canal:
   - Envoyer un message au canal
   - Envoyer la commande `/getid` (si vous avez un bot pour ça)
   - Ou utiliser le format: `-100` + les 10 derniers chiffres de l'URL du canal

---

## Configuration

### Fichier de configuration principal (.env)

| Variable | Description | Exemple |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token du bot (obligatoire) | `123456:ABC-DEF...` |
| `VITE_SUPABASE_URL` | URL Supabase | `https://...supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Clé Supabase | `eyJ...` |
| `TELEGRAM_CHANNEL_ID` | ID du canal de diffusion | `-1001234567890` |
| `MAX_PRICE` | Prix max de recherche (€) | `150` |
| `MIN_PROFIT` | Profit minimum requis (€) | `10` |
| `SEARCH_INTERVAL_MINUTES` | Intervalle de recherche | `5` |

### Marques de luxe recherchées par défaut

**Ultra-luxe (multiplicateur x4.0):**
- Gucci, Louis Vuitton, Prada, Chanel, Dior, Fendi

**Luxe (multiplicateur x3.5):**
- Yves Saint Laurent, Valentino, Givenchy, Balenciaga

**Premium (multiplicateur x3.0):**
- Nike, Adidas, Jordan, Supreme, Off-White

---

## Utilisation

### Démarrage du bot

```bash
python telegram_bot_advanced.py
```

Vous devriez voir:
```
INFO - Advanced Bot started!
```

### Commandes principales

#### 🔍 Recherches

**`/search_luxury`** - Recherche articles de marques ultra-luxe
```
Cherche: Gucci, Louis Vuitton, Prada, Chanel, Dior, etc.
Prix max: 150€
Réduction min: 25%
Profit min: 10€
```

**`/search_mispriced`** - Trouve articles sous-évalués
```
Cherche: Articles avec "original", "authentic", "rare", "vintage"
Détecte les items mal tarifés
Idéal pour flippers avisés
```

**`/search <mot-clé>,<mot-clé>`** - Recherche personnalisée
```
Usage: /search nike,jordan,adidas
Cherche plusieurs mots-clés simultanément
Accélérateur: ~50 articles/recherche
```

#### 📡 Canal de diffusion

**`/set_channel`** - Définir le canal de diffusion
```
Utiliser cette commande DANS le canal
Le bot enverra tous les articles trouvés dans ce canal
Permet suivi en temps réel
```

#### 📊 Analyse

**`/stats`** - Afficher les statistiques
```
Articles trouvés: nombre total
Articles en base: nombre sauvegardé
Profit moyen: moyenne des marges
```

**`/recent`** - Voir les 10 dernières affaires
```
Tri par date découverte
Clics rapides pour voir l'annonce
```

**`/top_brands`** - Marques les plus trouvées
```
Classement des marques en opportunités
Pourcentage de chaque marque
Tendances du marché
```

#### ⚙️ Gestion

**`/stop`** - Arrêter les recherches
**`/help`** - Afficher l'aide complète
**`/start`** - Redémarrer le bot

---

## Synchronisation des Prix

### Comment ça fonctionne?

Le bot analyse les prix à travers plusieurs plateformes:

1. **Vinted** - Plateforme d'achat (frais: 12.5%)
2. **Depop** - Revente chère (frais: 10.5%, markup: 1.3x)
3. **Vestiaire Collective** - Luxe (frais: 15%, markup: 1.4x)
4. **Grailed** - Streetwear/Sneakers (frais: 8%, markup: 1.5x)

### Calcul du profit

```
Profit = (Prix de revente × (1 - Frais plateforme)) - Prix d'achat - Frais expédition

Exemple:
- Article Gucci acheté 60€ sur Vinted
- Prix marché estimé: 200€
- Sur Depop: 260€ × (1 - 10.5%) = 232.70€
- Profit: 232.70€ - 60€ - 5€ = 167.70€
```

### Facteurs pris en compte

**Par marque:**
- Ultra-luxe (Gucci, Chanel): +30-40%
- Luxe standard (Valentino, Saint Laurent): +20-30%
- Premium (Nike, Jordan): +10-15%

**Par état:**
- Neuf: +0%
- Excellent: -15%
- Très bon: -25%
- Bon: -35%

**Par catégorie:**
- Accessoires/Montres: +10-20%
- Chaussures: +10%
- Sacs: +20%
- Vêtements: -10 à -20%

### Recommandations de prix

Le bot recommande automatiquement:
1. La meilleure plateforme de revente
2. Le prix optimal pour chaque plateforme
3. Le profit estimé
4. Le ROI en pourcentage

Exemple de message de recommandation:
```
💼 ANALYSE DE PRIX

📦 Sac Gucci Original

💰 Prix d'achat (Vinted): 65€
📈 Prix marché: 220€

🎯 MEILLEURES PLATEFORMES:

🥇 GRAILED
   Prix de revente: 330€
   Profit net: +260€
   (Frais: 8%)

• DEPOP
   Prix de revente: 280€
   Profit net: +210€
   (Frais: 10.5%)

• VESTIAIRE COLLECTIVE
   Prix de revente: 308€
   Profit net: +235€
   (Frais: 15%)

✅ RECOMMANDATION: GRAILED
💵 Profit maximal: +260€
📊 ROI: 400%
```

---

## Flux de travail complet

### Exemple: Trouver une affaire

```
1. Lancer: python telegram_bot_advanced.py

2. Chercher: /search_luxury
   Bot: "🔍 Recherche marques de luxe en cours..."
   Bot: "✅ 42 articles de luxe détectés!"
   Bot affiche: [12 meilleures affaires]

3. Analyser: Cliquer sur les articles intéressants
   Voir: Prix, marque, réduction, profit estimé
   Vérifier: Note du vendeur, condition

4. Décider:
   - Profit > 50€? ✅ Acheter
   - Marque ultra-luxe? ✅ Priorité
   - Vendeur < 80% avis? ⚠️ Prudence

5. Acheter: Cliquer "Voir l'annonce"

6. Revendre:
   Suivre la recommandation du bot
   Lister sur la plateforme suggérée
   Attendre acheteur
```

---

## Stratégies de revente

### Stratégie 1: Volume
- Chercher articles 30-50€
- Profit minimum 15€
- Volume: 30+ articles/mois
- Revente: Depop/Vinted

### Stratégie 2: Marques
- Focus ultra-luxe (Gucci, Chanel)
- Profit minimum 50€
- Volume: 5-10 articles/mois
- Revente: Vestiaire/Grailed

### Stratégie 3: Articles mal tarifés
- Chercher `/search_mispriced`
- Profit minimum 30€
- Curation manuelle
- Revente sélective

---

## Troubleshooting

### Le bot ne démarre pas

**Erreur: "TELEGRAM_BOT_TOKEN not set"**
```
❌ Solution:
1. Vérifier .env existe
2. Vérifier TELEGRAM_BOT_TOKEN est rempli
3. Copier-coller le token exactement
```

**Erreur: "Connection refused"**
```
❌ Raison: Pas de connexion internet
✅ Solution:
1. Vérifier WiFi/Connexion
2. Vérifier VPN (si utilisé)
3. Redémarrer le routeur
```

### Les recherches ne retournent rien

**Problème: 0 articles trouvés**
```
❌ Causes possibles:
1. Prix max trop bas
2. Vinted bloque les requêtes (rate limit)
3. Pas d'articles correspondants

✅ Solutions:
1. Augmenter MAX_PRICE dans .env
2. Attendre 30 minutes
3. Essayer autre mot-clé
4. Vérifier connexion
```

### Canal ne reçoit pas les messages

**Problème: Bot ne poste rien au canal**
```
✅ Vérifier:
1. Bot est admin du canal
2. TELEGRAM_CHANNEL_ID est correct
3. Format: -100 + 10 derniers chiffres
4. Relancer le bot après changement
```

### Base de données pleine

**Problème: "Database quota exceeded"**
```
✅ Solution:
1. Supprimer articles > 30 jours
2. Garder seulement articles pertinents
3. Archiver les données
4. Contact support Supabase
```

### Erreur "Supabase credentials"

**Problème: "Missing Supabase credentials"**
```
✅ Solution:
1. Vérifier VITE_SUPABASE_URL
2. Vérifier VITE_SUPABASE_ANON_KEY
3. Copier depuis .env.example
4. Redémarrer le bot
```

---

## Performance et limites

### Vitesse de recherche
- **1 mot-clé:** ~3-5 secondes
- **5 mot-clés:** ~15-20 secondes
- **Batch automatique:** 30 secondes

### Limitation Vinted
- Max 50 requêtes/minute
- User-agent rotation automatique
- Délai entre requêtes: 0.5-2s

### Stockage
- Articles gardés: 90 jours
- Base limite: 10GB Supabase gratuit
- ~100 articles = 1-2MB

---

## Tips & Astuces

### 🎯 Maximiser les profits

1. **Chercher tôt le matin**
   - Plus d'articles frais
   - Moins de concurrence

2. **Focus ultra-luxe**
   - Gucci, Chanel, Louis Vuitton
   - Profit moyenne: 100€+

3. **Vérifier les vendeurs**
   - Avis < 80%: risqué
   - Comptes neufs: attention

4. **Négocier sur Vinted**
   - Proposer -10% souvent accepté
   - Économie: -5-10€

5. **Revendre stratégiquement**
   - Grailed: Sneakers/Streetwear
   - Vestiaire: Luxe/Vintage
   - Depop: Tendance/Jeune

---

## Support & Problèmes

Pour plus d'aide:
1. Vérifier les logs du bot
2. Tester les commandes manuellement
3. Consulter la section Troubleshooting
4. Redémarrer le bot complètement

---

**Bonne chance dans vos trouvailles! 🍀**
