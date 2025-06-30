import os
import torch
import requests
from bs4 import BeautifulSoup
from dia.models import build_model
from dia.text import text_to_sequence
from dia.vocoder import load_vocoder
from dia.audio import save_wav

# Configuration
URL = "https://tldr.tech/data/2025-06-23" 
OUTPUT_DIR = "audios"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# Fonction de scraping
def scrap_resumes_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", class_="newsletter-html")
    return [div.get_text(strip=True) for div in divs]

# Initialisation du modèle
print("🔧 Chargement du modèle DIA...")
model = build_model("configs/base.yaml").to(DEVICE).eval()
vocoder = load_vocoder("configs/base.yaml").to(DEVICE).eval()

# Conversion texte → audio
def synthesize_text_to_audio(text, output_path):
    tokens = text_to_sequence(text)
    tokens = torch.LongTensor(tokens).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        mel = model.infer(tokens)
        wav = vocoder.infer(mel)

    save_wav(wav.squeeze(0).cpu(), output_path)
    print(f"🎧 Audio enregistré : {output_path}")

# --- Script principal ---
if __name__ == "__main__":
    print("📡 Récupération des résumés...")
    resumes = scrap_resumes_from_url(URL)

    if not resumes:
        print("❌ Aucun résumé trouvé.")
        exit()

    for i, resume in enumerate(resumes):
        filename = os.path.join(OUTPUT_DIR, f"resume_{i+1}.wav")
        synthesize_text_to_audio(resume, filename)

    print("✅ Tous les résumés ont été convertis en audio.")
