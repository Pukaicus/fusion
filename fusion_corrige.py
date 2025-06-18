import os
import re
import pytesseract
from pdf2image import convert_from_path
from xml.etree.ElementTree import Element, SubElement, ElementTree

# Configuration Tesseract & Poppler
pytesseract.pytesseract.tesseract_cmd = r'D:/Monprojet_installation/tesseract/tesseract.exe'
os.environ["TESSDATA_PREFIX"] = r"D:/Monprojet_installation/tesseract/tessdata"
poppler_path = r"D:/Monprojet_installation/poppler-24.08.0/Library/bin"


def ocr_cv(chemin_pdf):
    images = convert_from_path(chemin_pdf, poppler_path=poppler_path)
    texte = ""
    for img in images:
        texte += pytesseract.image_to_string(img, lang="fra") + "\n"
    return texte

def extract_info_detaille(text):
    infos = {
        "nom": "", 
        "prenom": "",   
        "email": extract_email(text) or "",
        "telephone": extract_phone(text) or "",
        "adresse": extract_adresse(text) or "",
        "competences": extract_competences(text) or [],
        "langues": extract_langues(text) or [],
        "experiences": extract_experiences(text) or [],
        "formations": extract_formations(text) or []
    }

    print("infos =", infos)  # Ici OK, infos bien défini
    
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
                
def extract_email(text):
    if not text:
        return None
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_phone(text):
    if not text:
        return None
    match = re.search(r"(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}", text)
    return match.group() if match else None

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
        # Vérifie que chaque mot commence par une majuscule
        if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words if w.isalpha()):
            return line_clean
    return "Nom Prénom Inconnu"

def extract_prenom_nom(text):
    lignes = text.strip().splitlines()
    for ligne in lignes:
        mots = ligne.strip().split()
        if len(mots) >= 2 and mots[0][0].isupper() and mots[1][0].isupper():
            return mots[0], mots[1]
    return "", ""

import re

def extract_email_tel(text):
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    tel_match = re.search(r"(0|\+33)[1-9](\s?\d{2}){4}", text)
    email = email_match.group() if email_match else ""
    tel = tel_match.group() if tel_match else ""
    return email, tel

def extract_adresse(text):
    lignes = text.strip().splitlines()
    for ligne in lignes:
        if any(mot in ligne.lower() for mot in ["rue", "avenue", "boulevard", "impasse", "chemin", "allée"]):
            return ligne.strip()
    return ""

def extract_competences(text):
    competences = []
    lignes = text.strip().splitlines()
    for ligne in lignes:
        if "-" in ligne or "•" in ligne:
            ligne = ligne.replace("•", "-")
            mots = ligne.split("-")
            for mot in mots:
                mot_clean = mot.strip()
                if 2 < len(mot_clean) < 50:
                    competences.append(mot_clean)
    return list(set(competences))  # supprime les doublons

def extract_langues(text):
    langues = []
    lignes = text.strip().splitlines()
    for ligne in lignes:
        match = re.search(r"(anglais|français|espagnol|allemand|italien)[^\n]*(A1|A2|B1|B2|C1|C2)", ligne, re.I)
        if match:
            langues.append({"langue": match.group(1).capitalize(), "niveau": match.group(2)})
    return langues

def extract_experiences(text):
    experiences = []
    blocs = text.split("\n\n")
    for bloc in blocs:
        if re.search(r"(stage|CDD|CDI|freelance|alternance|intérim)", bloc, re.I) or re.search(r"\b\d{4}\b", bloc):
            experiences.append(bloc.strip())
    return experiences

def extract_formations(text):
    formations = []
    blocs = text.split("\n\n")
    for bloc in blocs:
        if re.search(r"(BAC|BTS|DUT|Licence|Master|Doctorat)", bloc, re.I):
            formations.append(bloc.strip())
    return formations

def exporter_vers_xml(infos, chemin_fichier):
    from xml.etree.ElementTree import Element, SubElement, ElementTree

    racine = Element("CV")

    # Identité
    idf = SubElement(racine, "Identite")
    SubElement(idf, "Prenom").text = infos["prenom"]
    SubElement(idf, "Nom").text = infos["nom"]
    SubElement(idf, "Email").text = infos["email"]
    SubElement(idf, "Telephone").text = infos["telephone"]
    SubElement(idf, "Adresse").text = infos["adresse"]

    # Compétences
    comps = SubElement(racine, "Competences")
    for mot in infos["competences"]:
        SubElement(comps, "MotCle").text = mot

    # Langues
    langs = SubElement(racine, "Langues")
    for lg in infos["langues"]:
        l = SubElement(langs, "Langue")
        SubElement(l, "Nom").text = lg.get("langue", "")
        SubElement(l, "Niveau").text = lg.get("niveau", "")

    # Expériences
    exps = SubElement(racine, "Experiences")
    for exp in infos["experiences"]:
        e = SubElement(exps, "Experience")
        SubElement(e, "Poste").text = exp["poste"]
        SubElement(e, "Entreprise").text = exp["entreprise"]
        SubElement(e, "Debut").text = exp["debut"]
        SubElement(e, "Fin").text = exp["fin"]
        SubElement(e, "Description").text = exp["description"]

    # Formations
    forms = SubElement(racine, "Formations")
    for f in infos["formations"]:
        fo = SubElement(forms, "Formation")
        SubElement(fo, "Diplome").text = f["diplome"]
        SubElement(fo, "Etablissement").text = f["etablissement"]
        SubElement(fo, "Annee").text = f["annee"]

    tree = ElementTree(racine)
    tree.write(chemin_fichier, encoding="utf-8", xml_declaration=True)


import os

def main():
    dossier_cv = "D:/Monprojet_installation/cv"
    dossier_output = "D:/Monprojet_installation/output"
    os.makedirs(dossier_output, exist_ok=True)

    for fichier in os.listdir(dossier_cv):
        if not fichier.lower().endswith(".pdf"):
            continue

        chemin_pdf = os.path.join(dossier_cv, fichier)
        texte = ocr_cv(chemin_pdf)
        infos = extract_info_detaille(texte)

        nom_xml = os.path.splitext(fichier)[0] + ".xml"
        chemin_xml = os.path.join(dossier_output, nom_xml)
        exporter_vers_xml(infos, chemin_xml)
        
        print(f"✅ {fichier} → {nom_xml}")

    print("🎉 Tous les CV ont été traités.")

if __name__ == "__main__":
    main()
