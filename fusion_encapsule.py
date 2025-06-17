import os 
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

import os 
import re
import pytesseract
import pdfplumber
import xml.etree.ElementTree as ET
import xml.dom.minidom
from docx import Document
from pdf2image import convert_from_path

# Redéfinition du chemin des CV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cv_folder = os.path.join(BASE_DIR, "cv")

# Configuration du chemin vers Tesseract
pytesseract.pytesseract.tesseract_cmd = r'D:/Monprojet_installation/tesseract/tesseract.exe'
os.environ["TESSDATA_PREFIX"] = r"D:/Monprojet_installation/tesseract/tessdata"
# Chemin vers les binaires Poppler (nécessaire à pdf2image)
poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"

# Fonction principale pour traiter les fichiers PDF via OCR
def ma_fonction_principale():
    for filename in os.listdir(cv_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(cv_folder, filename)
            print(f"Traitement du fichier : {filename}")
            try:
                images = convert_from_path(pdf_path, poppler_path=poppler_path)
                text = ""
                for i, img in enumerate(images):
                    page_text = pytesseract.image_to_string(img, lang='fra')
                    print(f"Page {i+1}: {len(page_text)} caractères extraits")
                    text += page_text + "\n"
               
            except Exception as e:
                print(f"Erreur sur {filename} : {e}")

# Point d'entrée principal du script
if __name__ == "__main__":
    ma_fonction_principale()

# OCR à partir d’un PDF en images
def extract_text_from_pdf_ocr(path, dpi=300):
    images = convert_from_path(path, dpi=dpi, poppler_path=poppler_path)
    text = ""
    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img, lang='fra')
        print(f"[OCR] Page {i+1} : {len(page_text.strip())} caractères extraits")
        text += page_text + "\n"
    return text

# Fonction fictive simulant pdfplumber
def extract_text_from_pdf_pdfplumber(path):
    print("[INFO] Extraction texte avec pdfplumber (simulé)...")
    return ""

# Traitement des fichiers PDF du dossier
cv_folder = os.path.join(BASE_DIR, "cv")

for filename in os.listdir(cv_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(cv_folder, filename)
        print(f"🔍 Traitement du fichier : {filename}")
        try:
            texte = extract_text_from_pdf_ocr(pdf_path)
            print(f"[OK] Texte extrait : {len(texte)} caractères")
           
        except Exception as e:
            print(f"❌ Erreur sur {filename} : {e}")



    # Redondance possible : fonctions redéclarées
    def extract_text_from_pdf_pdfplumber(path):
        print("[INFO] Extraction texte avec pdfplumber (simulé)...")
        return ""

    def extract_text_from_pdf_ocr(path, dpi=300):
        images = convert_from_path(path, dpi=dpi, poppler_path=poppler_path)
        text = ""
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img, lang='fra')
            print(f"[OCR] Page {i+1} : {len(page_text.strip())} caractères extraits")
            text += page_text + "\n"
        return text

    # Nettoyage du texte OCR
    def clean_ocr_text(text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        text = "\n".join(line.strip() for line in text.split("\n"))
        return text

    # Extraction du nom et prénom (très simplifiée)
    def extract_name(text):
        lines = text.strip().split("\n")
        for line in lines[:5]:
            if len(line.split()) in [2, 3] and not line.isupper():
                return line.strip()
        return "Nom Prénom Inconnu"

    # Extraction de l'e-mail
    def extract_email(text):
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        return emails[0] if emails else "Email Inconnu"

    # Extraction du téléphone
    def extract_phone(text):
        phones = re.findall(r'(\+?\d[\d\s.-]{7,}\d)', text)
        return phones[0] if phones else "Téléphone Inconnu"

    # Génération du fichier XML à partir d’un dictionnaire
    def create_xml(infos, filename="cv.xml"):
        root = ET.Element("CV")

        identite = ET.SubElement(root, "Identite")
        ET.SubElement(identite, "Prenom").text = infos.get("prenom", "Inconnu")
        ET.SubElement(identite, "Nom").text = infos.get("nom", "Inconnu")
        ET.SubElement(identite, "Email").text = infos.get("email", "Inconnu")
        ET.SubElement(identite, "Telephone").text = infos.get("telephone", "Inconnu")

        tree = ET.ElementTree(root)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        print(f"[XML] Fichier {filename} généré.")

    # Essayez pdfplumber puis OCR si vide
    def extract_text(path):
        text = extract_text_from_pdf_pdfplumber(path)
        if not text.strip():
            print("Texte non trouvé avec pdfplumber, utilisation de l'OCR...")
            text = extract_text_from_pdf_ocr(path)
        return text

    # Pipeline complet de traitement d’un PDF
    def main(pdf_path):
        text = extract_text(pdf_path)
        if not text.strip():
            print("[ERREUR] Aucun texte extrait du PDF, impossible de continuer.")
            return

        text = clean_ocr_text(text)

        infos = {}
        nom_prenom = extract_name(text)
        mots = nom_prenom.split()
        if len(mots) >= 2:
            infos["prenom"] = mots[0]
            infos["nom"] = " ".join(mots[1:])
        else:
            infos["prenom"] = "Inconnu"
            infos["nom"] = "Inconnu"

        infos["email"] = extract_email(text)
        infos["telephone"] = extract_phone(text)

        filename_xml = os.path.splitext(pdf_path)[0] + ".xml"
        create_xml(infos, filename_xml)

    # Traitement de tous les fichiers PDF d’un dossier
    def traiter_dossier_pdf(dossier):
        for fichier in os.listdir(dossier):
            if fichier.lower().endswith(".pdf"):
                chemin_complet = os.path.join(dossier, fichier)
                print(f"\n[INFO] Traitement de : {chemin_complet}")
                main(chemin_complet)

        dossier_pdf = r"D:\cv_parser\cv"
        traiter_dossier_pdf(dossier_pdf)

    # --- Début du fichier parser.py ---
    # Extraction plus détaillée (nom, mail, compétences...)
    def extract_info_detaille(text):
        infos = {
            "nom": "NOM",
            "prenom": "Prénom",
            "email": extract_email(text),
            "telephone": extract_phone(text),
            "adresse": "",
            "date_naissance": "",
            "competences": [],
            "langues": [],
            "experiences": [],
            "formations": []
        }

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



        return infos  # ✅ Ne surtout pas oublier ce return ici


    # Fonctions annexes inchangées :
    # fonction pour extraire l'adresse mail
    def extract_email(text):
        if not text:
            return None
        match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return match.group() if match else None

    # fonction pour extraire le numéro de téléphone
    def extract_phone(text):
        if not text:
            return None
        match = re.search(r"(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}", text)
        return match.group() if match else None

    # fonction pour extraire le prénom 
    def extract_name(text):
        if not text:
            return "Nom Prénom Inconnu"
        lines = text.strip().split("\n")
        for line in lines[:10]:
            line_clean = line.strip()
            if not line_clean:
                continue
            if line_clean.isupper():
                continue
            words = line_clean.split()
            if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words if w.isalpha()):
                return line_clean
        return "Nom Prénom Inconnu"

    def extract_section(text, keywords):
        if not text:
            return ""
        lines = text.splitlines()
        section_text = []
        record = False
        for i, line in enumerate(lines):
            l = line.lower()
            if any(k in l for k in keywords):
                record = True
                continue
            if record:
                if any(kw in l for kw in ["expérience", "formation", "compétence", "loisir", "centre d'intérêt"]):
                    break
                section_text.append(line.strip())
        return "\n".join(section_text).strip()

    def extract_info(text):
        if not text:
            text = ""
        return {
            "nom_prenom": extract_name(text),
            "email": extract_email(text),
            "telephone": extract_phone(text),
            "experience": extract_section(text, ["expérience", "professionnelle"]),
            "formation": extract_section(text, ["formation", "diplôme"]),
            "langues": extract_section(text, ["langue"]),
        }

    # --- Début du fichier exporter.py ---

    def save_info_to_xml(info, output_path):
        if not isinstance(info, dict):
            print("❌ Erreur : 'info' n'est pas un dictionnaire.")
            return
        if not any(info.values()):
            print("❌ Données vides ou mal formées : XML non généré.")
            return

        for key in ["competences", "langues", "experiences", "formations"]:
            if not isinstance(info.get(key), list):
                info[key] = []

        cv = ET.Element("CV")

        identite = ET.SubElement(cv, "Identite")
        ET.SubElement(identite, "Nom").text = info.get("nom", "")
        ET.SubElement(identite, "Prenom").text = info.get("prenom", "")
        ET.SubElement(identite, "Email").text = info.get("email", "")
        ET.SubElement(identite, "Telephone").text = info.get("telephone", "")
        ET.SubElement(identite, "Adresse").text = info.get("adresse", "")

        competences = ET.SubElement(cv, "Competences")
        for comp in info.get("competences", []):
            if comp:
                ET.SubElement(competences, "Competence").text = comp

        langues = ET.SubElement(cv, "Langues")
        for langue in info.get("langues", []):
            lang_elem = ET.SubElement(langues, "Langue")
            lang_elem.text = langue.get("langue", "")
            if "niveau" in langue and langue["niveau"]:
                lang_elem.set("niveau", langue["niveau"])

        experiences = ET.SubElement(cv, "Experiences")
        for exp in info.get("experiences", []):
            exp_elem = ET.SubElement(experiences, "Experience")
            ET.SubElement(exp_elem, "Poste").text = exp.get("poste", "")
            ET.SubElement(exp_elem, "Entreprise").text = exp.get("entreprise", "")
            ET.SubElement(exp_elem, "Debut").text = exp.get("debut", "")
            ET.SubElement(exp_elem, "Fin").text = exp.get("fin", "")
            ET.SubElement(exp_elem, "Description").text = exp.get("description", "")

        formations = ET.SubElement(cv, "Formations")
        for form in info.get("formations", []):
            form_elem = ET.SubElement(formations, "Formation")
            ET.SubElement(form_elem, "Diplome").text = form.get("diplome", "")
            ET.SubElement(form_elem, "Etablissement").text = form.get("etablissement", "")
            ET.SubElement(form_elem, "Annee").text = form.get("annee", "")

        rough_string = ET.tostring(cv, encoding="utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        print(f"[XML] Fichier '{output_path}' généré.")

    # --- Début du fichier save_info_to_xml.py ---

    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                indent(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def save_info_to_xml(infos, output_path):
        if not infos or not isinstance(infos, dict):
            print("❌ Données absentes ou incorrectes. Aucun XML généré.")
            return

        cv = ET.Element("CV")

        identite = ET.SubElement(cv, "Identite")
        ET.SubElement(identite, "Nom").text = infos.get("nom") or ""
        ET.SubElement(identite, "Prenom").text = infos.get("prenom") or ""
        ET.SubElement(identite, "Email").text = infos.get("email") or ""
        ET.SubElement(identite, "Telephone").text = infos.get("telephone") or ""
        ET.SubElement(identite, "Adresse").text = infos.get("adresse") or ""

        competences = ET.SubElement(cv, "Competences")
        for comp in infos.get("competences", []):
            ET.SubElement(competences, "Competence").text = comp or ""

        langues = ET.SubElement(cv, "Langues")
        for langue_info in infos.get("langues", []):
            lang_elem = ET.SubElement(langues, "Langue")
            lang_elem.text = langue_info.get("langue") or ""
            niveau = langue_info.get("niveau") or ""
            if niveau:
                lang_elem.set("niveau", niveau)

        experiences = ET.SubElement(cv, "Experiences")
        for exp in infos.get("experiences", []):
            exp_elem = ET.SubElement(experiences, "Experience")
            ET.SubElement(exp_elem, "Poste").text = exp.get("poste") or ""
            ET.SubElement(exp_elem, "Entreprise").text = exp.get("entreprise") or ""
            ET.SubElement(exp_elem, "Debut").text = exp.get("debut") or ""
            ET.SubElement(exp_elem, "Fin").text = exp.get("fin") or ""
            ET.SubElement(exp_elem, "Description").text = exp.get("description") or ""

        formations = ET.SubElement(cv, "Formations")
        for form in infos.get("formations", []):
            form_elem = ET.SubElement(formations, "Formation")
            ET.SubElement(form_elem, "Diplome").text = form.get("diplome") or ""
            ET.SubElement(form_elem, "Etablissement").text = form.get("etablissement") or ""
            ET.SubElement(form_elem, "Annee").text = form.get("annee") or ""

        indent(cv)

        tree = ET.ElementTree(cv)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"[XML] Fichier '{output_path}' généré.")

    # --- Début du fichier main.py ---
    import os
    import re
    import pdfplumber
    from docx import Document

    CV_FOLDER = "cv"
    OUTPUT_FOLDER = "output"

    def extract_text_from_docx(path):
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])

    def extract_text_from_pdf(path):
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def get_cv_text(file_path):
        if file_path.endswith('.docx'):
            return extract_text_from_docx(file_path)
        elif file_path.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            if not text.strip():
                print("Texte non trouvé avec pdfplumber, utilisation de l'OCR...")
                text = extract_text_from_pdf_ocr(file_path)
            return text
        else:
            return ""

    def main():
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        for filename in os.listdir(CV_FOLDER):
            path = os.path.join(CV_FOLDER, filename)
            if not os.path.isfile(path):
                continue
            print(f"Analyse de : {filename}")
            text = get_cv_text(path)

            print(f"--- Début texte extrait ({len(text)} caractères) ---")
            print(text[:500])
            print("--- Fin extrait ---")

            infos = extract_info_detaille(text)

            print("Infos extraites (détail complet) :")
            for k, v in infos.items():
                print(f"{k.upper()} : {v}")

            if any(infos.values()):
                output_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(filename)[0]}.xml")
                save_info_to_xml(infos, output_path)
                print(f"✅ XML généré : {output_path}")
            else:
                print(f"⚠️ Aucune info extraite de {filename}")
            print("-" * 40)


    if __name__ == "__main__":
        main()




ma_fonction_principale()
