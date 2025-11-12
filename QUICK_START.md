# ⚡ Quick Start - 5 minutes

## 1️⃣ Créer le bot Telegram (2 min)

Ouvrir Telegram → Chercher **@BotFather**

```
/newbot
→ Nom: VintedBot
→ Username: vinted_bot_12345
✅ Copier le TOKEN
```

## 2️⃣ Configurer le projet (2 min)

```bash
# Télécharger
git clone <repo>
cd vinted-bot

# Installer
pip install -r requirements.txt

# Configurer
cp .env.example .env
# Éditer .env et ajouter le TOKEN
```

`.env`:
```env
TELEGRAM_BOT_TOKEN=VOTRE_TOKEN_ICI
VITE_SUPABASE_URL=https://solwtszgtgqlngaakeso.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 3️⃣ Lancer le bot (1 min)

```bash
python telegram_bot_advanced.py
```

Aller sur Telegram et taper `/start`

## 4️⃣ Utiliser le bot

```
/search_luxury      → Cherche Gucci, Chanel, etc.
/search_mispriced   → Trouve articles mal tarifés
/search nike,adidas → Multi-recherche
/stats              → Voir les trouvailles
/help               → Aide complète
```

---

## Commandes essentielles

| Commande | Résultat |
|----------|----------|
| `/search_luxury` | 🔥 10-50 articles de luxe |
| `/search_mispriced` | 💰 Articles sous-évalués |
| `/search nike` | 🎯 Recherche Nike |
| `/stats` | 📊 Total articles trouvés |
| `/stop` | ⏹️ Arrête les recherches |

---

## Configuration optionnelle: Canal de diffusion

1. Créer un canal Telegram
2. Ajouter le bot en admin
3. Envoyer `/set_channel` DANS le canal
4. Tous les articles iront automatiquement au canal!

---

## Exemple d'utilisation

```
Vous: /search_luxury
Bot: 🔍 Recherche marques de luxe en cours...
Bot: ✅ 28 articles de luxe détectés!

[Bot envoie les 10 meilleures affaires]

Vous: [Clique sur une affaire]
Bot affiche:
   📦 Sac Gucci Authentique
   💰 60€ (Vinted)
   💵 +180€ profit (Depop)
   🎯 Recommandé: GRAILED

Vous: [Clique "Voir l'annonce"]
[Achète l'article sur Vinted]
[Revend sur plateforme suggérée]
[Profit: +180€!]
```

---

## En cas de problème

**"Token invalide"**
```
→ Vérifier le token dans @BotFather
→ Copier exactement (sans espaces)
```

**"Pas de résultats"**
```
→ Augmenter MAX_PRICE dans .env
→ Attendre 5 minutes (rate limit Vinted)
```

**"Bot ne démarre pas"**
```
→ pip install -r requirements.txt
→ python -m pip install --upgrade pip
→ Relancer
```

---

## Prochaines étapes

Voir **SETUP_GUIDE.md** pour:
- Configuration avancée
- Stratégies de revente
- Synchronisation des prix
- Troubleshooting complet

---

**C'est parti! 🚀**
