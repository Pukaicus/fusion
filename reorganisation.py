import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from docx import Document
import xml.etree.ElementTree as ET
import xml.dom.minidom

# Définition du répertoire contenant les CV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cv_folder = os.path.join(BASE_DIR, "cv")

# Parcours des fichiers PDF pour afficher ceux à traiter
for filename in os.listdir(cv_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(cv_folder, filename) 
        print(f"Traitement du fichier : {pdf_path}")

# Affichage des noms de tous les fichiers dans le dossier CV
for filename in os.listdir(cv_folder):
    print("Fichier :", filename)  
# Redéfinition du chemin des CV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cv_folder = os.path.join(BASE_DIR, "cv")

# Configuration du chemin vers Tesseract
pytesseract.pytesseract.tesseract_cmd = r'D:/Monprojet_installation/tesseract/tesseract.exe'
os.environ["TESSDATA_PREFIX"] = r"D:/Monprojet_installation/tesseract/tessdata"
# Chemin vers les binaires Poppler (nécessaire à pdf2image)
poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"

# 📁 Dossiers d'entrée/sortie
CV_FOLDER = "cv"
OUTPUT_FOLDER = "output"

# ================== 📤 EXTRACTION TEXTE ==================

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_pdf_ocr(path):
    images = convert_from_path(path, poppler_path=poppler_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang='fra') + "\n"
    return text

def get_cv_text(file_path):
    if file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            print("⚠️ PDF vide avec pdfplumber. Utilisation OCR...")
            text = extract_text_from_pdf_ocr(file_path)
        return text
    else:
        return ""

# =================== 🔍 EXTRACTION INFOS ===================

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else ""

def extract_phone(text):
    match = re.search(r"(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}", text)
    return match.group() if match else ""

def extract_name(text):
    lines = text.strip().split("\n")
    for line in lines[:10]:
        line = line.strip()
        if line and not line.isupper():
            words = line.split()
            if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words if w.isalpha()):
                return line
    return "Nom Prénom Inconnu"

# =================== 💾 GÉNÉRATION XML ===================

def save_info_to_xml(info, output_path):
    if not info or not isinstance(info, dict):
        print("❌ Données absentes ou invalides.")
        return

    cv = ET.Element("CV")

    identite = ET.SubElement(cv, "Identite")
    ET.SubElement(identite, "Nom").text = info.get("nom", "")
    ET.SubElement(identite, "Prenom").text = info.get("prenom", "")
    ET.SubElement(identite, "Email").text = info.get("email", "")
    ET.SubElement(identite, "Telephone").text = info.get("telephone", "")

    xml_str = ET.tostring(cv, encoding="utf-8")
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_pretty)

    print(f"[✅] Fichier XML généré : {output_path}")

# =================== 🚀 PROGRAMME PRINCIPAL ===================

def main():
    if not os.path.exists(CV_FOLDER):
        print("❌ Dossier CV introuvable.")
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for filename in os.listdir(CV_FOLDER):
        file_path = os.path.join(CV_FOLDER, filename)
        if not os.path.isfile(file_path):
            continue

        print(f"\n--- Traitement : {filename} ---")
        text = get_cv_text(file_path)

        if not text.strip():
            print("❌ Aucune donnée détectée dans le fichier.")
            continue

        infos = {
            "nom": extract_name(text),
            "prenom": "",  # À déduire si tu veux
            "email": extract_email(text),
            "telephone": extract_phone(text)
        }

        output_filename = os.path.splitext(filename)[0] + ".xml"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        save_info_to_xml(infos, output_path)

        os.remove(file_path)
        print(f"🗑️ Fichier supprimé : {filename}")

# =============== POINT D'ENTRÉE ===============
if __name__ == "__main__":
    main()
