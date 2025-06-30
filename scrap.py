import requests
from bs4 import BeautifulSoup
import re
import json
from notion_client import Client

# ===================== CONFIGURATION =====================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:latest"

NOTION_TOKEN = "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"  
DATABASE_ID = "21ecc6c075048007b34fd9f9b22a173d"
notion = Client(auth=NOTION_TOKEN)


# ===================== FONCTIONS =====================

def classify_categories_with_ollama(title, summary):
    prompt = f"""Tu es un assistant qui classe les articles dans des catégories claires, compréhensibles et concises.

Voici le titre : "{title}"
Voici le résumé : "{summary}"

Donne entre 1 et 4 catégories pertinentes séparées par des virgules. Pas d’explication. Exemples de catégories possibles : IA, Cloud, Dev, Marketing, Startup, Sécurité, Mobile, Blockchain, Data, Produit, etc. Créez des catégories si nécessaire, mais restez concis.

Catégories :"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": 60
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                data = json.loads(line)
                full_response += data.get("response", "")
                if data.get("done", False):
                    break

        # Nettoyage du texte retourné
        categories = [c.strip().capitalize() for c in full_response.strip().split(",") if c.strip()]
        return categories[:4]
    except Exception as e:
        print(f"Erreur classification Ollama : {e}")
        return ["Non catégorisé"]


def add_article_to_notion(article):
    try:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Titre": {"title": [{"text": {"content": article['title']}}]},
                "URL": {"url": article['url']},
                "Durée": {"rich_text": [{"text": {"content": article['duration']}}]},
                "Résumé": {"rich_text": [{"text": {"content": article['summary']}}]},
                "Catégorie": {"multi_select": [{"name": c} for c in article['categories']]}
            }
        )
        print(f"✅ Article ajouté à Notion : {article['title']}")
    except Exception as e:
        print(f"❌ Erreur Notion : {e}")

def generate_summary_with_ollama(text):
    prompt = (
        "Tu es un assistant concis. Résume ce texte en français avec un maximum de 8 mots. "
        "N’écris que les mots du résumé, sans phrase d’introduction, sans ponctuation, sans retour à la ligne. "
        "Le résumé doit rester pertinent et compréhensible.\n\n"
        f"{text}\n\n"
        "Résumé :"
    )

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": 40
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                data = json.loads(line)
                full_response += data.get("response", "")
                if data.get("done", False):
                    break

        # Nettoyage
        cleaned = re.sub(r'[^\w\sÀ-ÿ]', '', full_response)  # Garde les caractères accentués
        words = cleaned.strip().split()

        # Tronque si plus de 8 mots
        if len(words) > 8:
            words = words[:8]

        return " ".join(words)

    except Exception as e:
        print(f"Erreur API Ollama : {e}")
        return "Résumé IA indisponible"


# ===================== SCRAPING =====================

url = "https://tldr.tech/data/2025-06-23"
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')
articles = soup.find_all('article')

results = []
duration_pattern = re.compile(r'\(([^)]+)\)$')

for article in articles:
    link_tag = article.find("a", class_="font-bold")
    article_url = link_tag["href"] if link_tag and "href" in link_tag.attrs else url
    title_tag = link_tag.find(['h2', 'h3']) if link_tag else article.find(['h2', 'h3'])
    raw_title = title_tag.get_text(strip=True) if title_tag else "Titre non trouvé"
    duration_match = duration_pattern.search(raw_title)

    if duration_match:
        duration = duration_match.group(1)
        title = duration_pattern.sub('', raw_title).strip()
    else:
        duration = "Durée non trouvée"
        title = raw_title

    newsletter_div = article.find("div", class_="newsletter-html")
    raw_text = newsletter_div.get_text(strip=True) if newsletter_div else ""
    summary = generate_summary_with_ollama(raw_text) if raw_text else "Pas de texte pour résumé"
    categories = classify_categories_with_ollama(title, summary)

    article_data = {
        "title": title,
        "url": article_url,
        "duration": duration,
        "summary": summary,
        "categories": categories
    }

    results.append(article_data)
    add_article_to_notion(article_data)
