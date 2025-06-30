# 🤖 Scraping TLDR + Résumé IA + Envoi Notion

Ce projet permet de :
- Scraper automatiquement les articles de [TLDR.tech](https://tldr.tech),
- Générer un résumé concis avec un LLM local via l'API Ollama,
- Catégoriser automatiquement les articles via l'IA,
- Envoyer les résultats dans une base de données Notion via l'API officielle.

---

## 🔧 Prérequis

### Clone le répo
```bash
git clone https://github.com/yanisgilliard/projet_final
```

### ✅ Logiciels et outils nécessaires

- Python 3.8+
- [Ollama](https://ollama.com) installé et lancé localement avec un modèle (ex : `gemma3:latest`)
- Un token d'intégration Notion et une base de données partagée avec l'intégration

### 📦 Installation des dépendances

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration
### 🔑 Variables à modifier dans le script (main.py)
```bash
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:latest"

NOTION_TOKEN = "votre_token_notion"
DATABASE_ID = "votre_database_id"
```

## 🚀 Lancer le script
```bash
python scrap.py
```