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

# 1. Chemin du CV
chemin_cv = "D:\Monprojet_installation\cv"

# 2. Extraire le texte avec OCR
text = ocr_cv(chemin_cv)

# 3. Extraire les infos du texte
infos = extraire_infos(text)

# 4. Exporter en XML
exporter_vers_xml(infos)

lignes = text.strip().splitlines()

blacklist = ["expériences", "professionnelles", "formations", "contact", "langues", "adresse", "compétences", "parcours", "curriculum", "vitae"]

        # 1. Chercher 2 mots dont 1 est tout en maj et l'autre capitalisé
for line in lignes[:20]:
        ligne_clean = line.strip()
            mots = ligne_clean.split()
            if len(mots) == 2:
                mot1, mot2 = mots[0], mots[1]
                ligne_basse = ligne_clean.lower()
                if any(b in ligne_basse for b in blacklist):
                    continue  # ignore si ligne genre "Expériences Professionnelles"

                # Cas Nom en maj, prénom en capitalisé
                if mot1[0].isupper() and mot2.isupper():
                    infos["prenom"] = mot1.capitalize()
                    infos["nom"] = mot2.upper()
                    break
                # Cas Prénom en maj, nom en capitalisé
                elif mot1.isupper() and mot2[0].isupper():
                    infos["prenom"] = mot1.capitalize()
                    infos["nom"] = mot2.upper()
                    break
                # Cas deux mots majuscules (ex : JEAN DUPONT)
                elif mot1.isupper() and mot2.isupper():
                    infos["prenom"] = mot1.capitalize()
                    infos["nom"] = mot2.upper()
                    break

        # 2. Fallback : ligne avec "Nom :" ou "Prénom :"
        if infos["prenom"] == "Prénom" or infos["nom"] == "NOM":
            for line in lignes[:40]:
                line_clean = line.strip()
                if "prénom" in line.lower() and ":" in line:
                    prenom = line_clean.split(":")[1].strip()
                    if prenom:
                        infos["prenom"] = prenom.capitalize()
                elif "nom" in line.lower() and ":" in line:
                    nom = line_clean.split(":")[1].strip()
                    if nom:
                        infos["nom"] = nom.upper()
                if infos["prenom"] != "Prénom" and infos["nom"] != "NOM":
                    break

        # 3. Fallback : détecter ligne au-dessus de "Contact"
        if infos["prenom"] == "Prénom" or infos["nom"] == "NOM":
            for i, line in enumerate(lignes):
                if "contact" in line.lower():
                    for j in range(max(0, i - 3), i):
                        mots = lignes[j].strip().split()
                        if len(mots) == 2 and not any(b in lignes[j].lower() for b in blacklist):
                            if mots[0].isupper() and mots[1][0].isupper():
                                infos["prenom"] = mots[0].capitalize()
                                infos["nom"] = mots[1].upper()
                                break
                    break




        # 🔍 Recherche d’adresse postale (version robuste)
        adresse_pattern = re.compile(
            r"(\d{1,4}\s(?:[A-Za-zÀ-ÖØ-öø-ÿ'\-\.]+\s?){1,6}(?:,\s*)?\d{5}\s+[A-Za-zÀ-ÖØ-öø-ÿ'\-\.]+)",
            re.IGNORECASE
        )

        for i, line in enumerate(lignes):
            line = line.strip()
            # Vérifie sur une ligne
            match = adresse_pattern.search(line)
            if match:
                infos["adresse"] = match.group(1).strip()
                break
            # Vérifie sur deux lignes consécutives (cas fragmenté)
            elif i + 1 < len(lignes):
                combined = line + " " + lignes[i + 1].strip()
                match = adresse_pattern.search(combined)
                if match:
                    infos["adresse"] = match.group(1).strip()
                    break



        # Recherche de compétences par motifs
        match = re.search(r"(compétences.*?)(langues|expériences|formations|centres|$)", text, re.IGNORECASE | re.DOTALL)
        if match:
            bloc = match.group(1)
            lignes_bloc = bloc.splitlines()
            mots_vides = {
                "de", "et", "à", "le", "la", "les", "un", "une", "des", "du",
                "en", "pour", "avec", "niveau", "notions", "bonne", "maîtrise",
                "compétences", "maitrise", "utilisation", "langage", "logiciel", "logiciels",
                "actuel", "actuelle", "depuis", "responsable", "professionnel", "professionnelle",
                "terrain", "nice", "lyon", "paris", "clientèle", "clients", "entreprise", "entreprises",
                "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024",
                "2010", "2011", "2012", "actuel", "actuelle", "stage", "contrat", "cdd", "alternance",
                "boiron", "isodent", "dermagyne", "institut", "administration", "part", "rendez-vous",
                "permettant", "maintenir", "contribuer", "parcours", "professionnel", "formation"
            }
            mots_reconnus = {
                "python", "java", "html", "css", "javascript", "php", "sql", "bash", "linux",
                "git", "github", "vscode", "docker", "flask", "django", "symfony", "react",
                "node", "json", "xml", "api", "uml", "agile", "scrum", "jira",
                "autonome", "rigoureux", "créatif", "esprit d’équipe", "communication", "organisé",
                "curieux", "motivé", "adaptabilité", "gestion", "stress", "travail",
                "word", "excel", "powerpoint", "outlook", "teams", "office", "microsoft", "developper", 
                "superviser", "représenter", "prendre", "gérer"
            }
            for ligne in lignes_bloc:
                if re.match(r"^\s*[-•·]\s*(.+)", ligne):
                    mot = re.sub(r"^\s*[-•·]\s*", "", ligne).strip().lower()
                    if mot and mot not in mots_vides:
                        infos["competences"].append(mot)
                else:
                    mots = re.findall(r"\b\w[\w\-+\.]*\b", ligne.lower())
                    for mot in mots:
                        if mot not in mots_vides and (mot in mots_reconnus or len(mot) >= 4):
                            infos["competences"].append(mot)


        # Détection des langues + niveaux
        langues_pattern = re.compile(
            r"\b(\w+)\b\s*[-:|]*\s*(A1|A2|B1|B2|C1|C2|débutant|intermédiaire|courant|bilingue|TOEIC\s*\d+|TOEFL\s*\d+)",
            re.IGNORECASE
        )

        match = re.search(r"(langues.*?)(expériences|formations|centres|$)", text, re.IGNORECASE | re.DOTALL)
        if match:
            bloc = match.group(1)
            lignes_bloc = bloc.splitlines()
            for ligne in lignes_bloc:
                for result in langues_pattern.finditer(ligne):
                    langue = result.group(1).strip()
                    niveau_raw = result.group(2).strip()
                    niveau = niveau_raw.upper()

                    if "toeic" in niveau_raw.lower():
                        score = int(re.search(r"\d+", niveau_raw).group())
                        niveau = "C1" if score >= 900 else "B2" if score >= 785 else "B1"
                    elif "toefl" in niveau_raw.lower():
                        score = int(re.search(r"\d+", niveau_raw).group())
                        niveau = "C1" if score >= 95 else "B2" if score >= 72 else "B1"

                    infos["langues"].append({"langue": langue, "niveau": niveau})


        # Extraction des expériences professionnelles
        match = re.search(r"(expériences?.*?)(formations|compétences|langues|centres|parcours|$)", text, re.IGNORECASE | re.DOTALL)
        if match:
            bloc = match.group(1).strip()
            lignes = bloc.splitlines()
            buffer = []
            
            for ligne in lignes:
                ligne = ligne.strip()
                if ligne == "" or ligne.lower().startswith("formation"):
                    continue
                buffer.append(ligne)

            i = 0
            while i < len(buffer):
                poste = ""
                entreprise = ""
                debut = ""
                fin = ""
                description_lignes = []

                # Poste
                while i < len(buffer):
                    ligne = buffer[i]
                    if re.search(r"\b(developpeur|designer|assistant|assistante|ingénieur|chef|chargé|commercial|technicien|manager|consultant|stagiaire|analyste|opérateur|agent)\b", ligne, re.IGNORECASE):
                        poste = ligne
                        i += 1
                        break
                    i += 1

                # Entreprise
                if i < len(buffer):
                    ligne = buffer[i]
                    if not re.search(r"\d{4}|\d{2}/\d{4}|présent|en cours", ligne.lower()):
                        entreprise = ligne
                        i += 1

                # Dates
                date_block = " ".join(buffer[max(0, i - 3):i + 3])
                date_match = re.search(
                    r"(?:(\d{2}/\d{4}|\w+\s+\d{4}|\d{4}))\s*[-à–>]*\s*(\d{2}/\d{4}|\w+\s+\d{4}|présent|en cours)?",
                    date_block,
                    re.IGNORECASE
                )
                if date_match:
                    debut = date_match.group(1).strip() if date_match.group(1) else ""
                    fin = date_match.group(2).strip() if date_match.group(2) else ""

                # Description
                while i < len(buffer):
                    ligne = buffer[i]
                    if ligne.lower().startswith("formation") or re.search(r"\b(developpeur|designer|assistant|assistante|ingénieur|chef|chargé|commercial|technicien|manager|consultant|stagiaire|analyste|opérateur|agent)\b", ligne, re.IGNORECASE):
                        break
                    description_lignes.append(re.sub(r"^[-•·*→‣\s]+", "", ligne))
                    i += 1

                # Ajout uniquement si un poste a été détecté
                if poste:
                    infos["experiences"].append({
                        "poste": poste,
                        "entreprise": entreprise,
                        "debut": debut,
                        "fin": fin,
                        "description": " ".join(description_lignes).strip()
                    })



        # Analyse des formations
        match = re.search(r"(formations?.*?)(centres|$)", text, re.IGNORECASE | re.DOTALL)
        if match:
            bloc = match.group(1).strip()
            lignes = bloc.splitlines()

            diplomes_connus = [
                "BTS", "DUT", "Licence", "Master", "MBA", "Doctorat",
                "CAP", "BEP", "Bac", "Bachelor", "Ingénieur",
                "Titre professionnel", "Diplôme universitaire", "Prépa", "DNA"
            ]

            for i, ligne in enumerate(lignes):
                ligne = ligne.strip()
                if any(d.lower() in ligne.lower() for d in diplomes_connus):
                    # On essaie de trouver une année (ex: 2022 ou 2021-2023)
                    annee_match = re.search(r"\d{4}(?:[-/]\d{4})?", ligne)
                    annee = annee_match.group() if annee_match else ""

                    # Etablissement : ligne suivante si elle existe
                    etablissement = lignes[i+1].strip() if i + 1 < len(lignes) else ""

                    infos["formations"].append({
                        "diplome": ligne,
                        "etablissement": etablissement,
                        "annee": annee
                    })

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
