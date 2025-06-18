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
        "telephone": extract_phone(text) or ""
    }

    # Maintenant que `infos` existe, on peut l'utiliser dans les fonctions suivantes :
    infos["adresse"] = extract_adresse(text, infos) or ""
    infos["competences"] = extract_competences(text, infos) or []
    infos["langues"] = extract_langues(text, infos) or []
    infos["experiences"] = extract_experiences(text, infos) or []
    infos["formations"] = extract_formations(text, infos) or []

    print("infos =", infos)
    return infos
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
    blacklist = ["expérience", "contact", "compétences", "formation", "adresse", "email", "téléphone"]
    infos = {"prenom": "", "nom": ""}

    lignes = [l.strip() for l in text.strip().splitlines() if l.strip()]
    # 1. Chercher dans les 20 premières lignes une ligne avec 2 ou 3 mots plausibles (pas blacklistés)
    for line in lignes[:20]:
        line_lower = line.lower()
        if any(b in line_lower for b in blacklist):
            continue
        mots = line.split()
        # Cas 2 ou 3 mots (ex: Jean Dupont, Jean Paul Dupont)
        if 2 <= len(mots) <= 3:
            # Vérifier que les mots commencent par majuscule (lettre capitale)
            if all(m[0].isupper() for m in mots):
                # Si 2 mots : prénom nom
                if len(mots) == 2:
                    infos["prenom"] = mots[0]
                    infos["nom"] = mots[1]
                    return infos["prenom"], infos["nom"]
                # Si 3 mots : prénom + nom composé
                elif len(mots) == 3:
                    infos["prenom"] = mots[0]
                    infos["nom"] = mots[1] + " " + mots[2]
                    return infos["prenom"], infos["nom"]

    # 2. Chercher "Prénom :" et "Nom :" dans les 40 premières lignes
    for line in lignes[:40]:
        line_lower = line.lower()
        if "prénom" in line_lower and ":" in line_lower:
            prenom = line.split(":", 1)[1].strip()
            if prenom:
                infos["prenom"] = prenom
        if "nom" in line_lower and ":" in line_lower:
            nom = line.split(":", 1)[1].strip()
            if nom:
                infos["nom"] = nom
        if infos["prenom"] and infos["nom"]:
            return infos["prenom"], infos["nom"]

    # 3. Chercher juste avant la section "contact"
    for i, line in enumerate(lignes):
        if "contact" in line.lower():
            # Regarder les 3 lignes avant
            for j in range(max(0, i - 3), i):
                mots = lignes[j].split()
                if 2 <= len(mots) <= 3 and not any(b in lignes[j].lower() for b in blacklist):
                    if all(m[0].isupper() for m in mots):
                        if len(mots) == 2:
                            infos["prenom"] = mots[0]
                            infos["nom"] = mots[1]
                            return infos["prenom"], infos["nom"]
                        elif len(mots) == 3:
                            infos["prenom"] = mots[0]
                            infos["nom"] = mots[1] + " " + mots[2]
                            return infos["prenom"], infos["nom"]
            break

    # 4. En dernier recours, retourner vide
    return "", ""

def extract_email_tel(text):
    # Email
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    email_match = re.search(email_regex, text)
    email = email_match.group() if email_match else ""

    # Téléphone français (formats variés)
    tel_regex = r"(0|\+33)[\s.-]?([1-9][\s.-]?){4}[0-9]"
    tel_match = re.search(tel_regex, text)
    tel = tel_match.group() if tel_match else ""

    # Nettoyer le téléphone (supprimer espaces et caractères inutiles)
    if tel:
        tel = re.sub(r"[\s.-]", "", tel)

    return email, tel

def extract_adresse(text, infos):
    lignes = text.strip().splitlines()

    # Regex adresse postale complète (numéro + rue + code postal + ville)
    adresse_pattern = re.compile(
        r"(\d{1,4}\s(?:[A-Za-zÀ-ÖØ-öø-ÿ'\-\.]+\s?){1,6}(?:,\s*)?\d{5}\s+[A-Za-zÀ-ÖØ-öø-ÿ'\-\.]+)",
        re.IGNORECASE
    )

    for i, line in enumerate(lignes):
        line = line.strip()

        # 1) Cherche adresse complète sur une ligne
        match = adresse_pattern.search(line)
        if match:
            infos["adresse"] = match.group(1).strip()
            return  # On sort dès qu'on a trouvé

        # 2) Cherche adresse fragmentée sur 2 lignes consécutives
        if i + 1 < len(lignes):
            combined = line + " " + lignes[i + 1].strip()
            match = adresse_pattern.search(combined)
            if match:
                infos["adresse"] = match.group(1).strip()
                return

    # 3) Si pas trouvé avec regex, fallback simple par mots clés
    mots_cles = ["rue", "avenue", "boulevard", "impasse", "chemin", "allée", "place", "route"]
    for ligne in lignes:
        if any(mot in ligne.lower() for mot in mots_cles):
            infos["adresse"] = ligne.strip()
            return

    # 4) Pas d'adresse trouvée
    infos["adresse"] = ""


def extract_competences(text, infos):
    infos["competences"] = []

    # 1. Recherche de la section "Compétences" jusqu'à la prochaine section ou fin de texte
    match = re.search(r"(compétences.*?)(langues|expériences|formations|centres|$)", text, re.IGNORECASE | re.DOTALL)
    mots_vides = {
        "de", "et", "à", "le", "la", "les", "un", "une", "des", "du",
        "en", "pour", "avec", "niveau", "notions", "bonne", "maîtrise",
        "compétences", "maitrise", "utilisation", "langage", "logiciel", "logiciels",
        "actuel", "actuelle", "depuis", "responsable", "professionnel", "professionnelle",
        "terrain", "nice", "lyon", "paris", "clientèle", "clients", "entreprise", "entreprises",
        "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024",
        "2010", "2011", "2012", "stage", "contrat", "cdd", "alternance",
        "boiron", "isodent", "dermagyne", "institut", "administration", "part", "rendez-vous",
        "permettant", "maintenir", "contribuer", "parcours", "formation"
    }
    mots_reconnus = {
        "python", "java", "html", "css", "javascript", "php", "sql", "bash", "linux",
        "git", "github", "vscode", "docker", "flask", "django", "symfony", "react",
        "node", "json", "xml", "api", "uml", "agile", "scrum", "jira",
        "autonome", "rigoureux", "créatif", "esprit", "communication", "organisé",
        "curieux", "motivé", "adaptabilité", "gestion", "stress", "travail",
        "word", "excel", "powerpoint", "outlook", "teams", "office", "microsoft", "developper",
        "superviser", "représenter", "prendre", "gérer"
    }

    if match:
        bloc = match.group(1)
        lignes_bloc = bloc.splitlines()
        for ligne in lignes_bloc:
            # Extraction dans les listes à puces
            m = re.match(r"^\s*[-•·]\s*(.+)", ligne)
            if m:
                mot = m.group(1).strip().lower()
                if mot and mot not in mots_vides:
                    infos["competences"].append(mot)
            else:
                # Extraction dans les phrases, mot par mot
                mots = re.findall(r"\b\w[\w\-+\.]*\b", ligne.lower())
                for mot in mots:
                    if mot not in mots_vides and (mot in mots_reconnus or len(mot) >= 4):
                        infos["competences"].append(mot)

    # 2. Fallback : rechercher partout dans le texte des lignes contenant des tirets ou puces
    if not infos["competences"]:
        lignes = text.strip().splitlines()
        for ligne in lignes:
            if "-" in ligne or "•" in ligne or "·" in ligne:
                ligne_nettoyee = ligne.replace("•", "-").replace("·", "-")
                mots = [m.strip().lower() for m in ligne_nettoyee.split("-")]
                for mot in mots:
                    if 2 < len(mot) < 50 and mot not in mots_vides:
                        infos["competences"].append(mot)

    # Supprimer doublons tout en conservant l’ordre
    seen = set()
    competences_uniques = []
    for c in infos["competences"]:
        if c not in seen:
            competences_uniques.append(c)
            seen.add(c)
    infos["competences"] = competences_uniques

def extract_langues(text, infos):
    infos["langues"] = []

    # Pattern général pour langues + niveaux
    langues_pattern = re.compile(
        r"\b(\w+)\b\s*[-:|]*\s*(A1|A2|B1|B2|C1|C2|débutant|intermédiaire|courant|bilingue|TOEIC\s*\d+|TOEFL\s*\d+)",
        re.IGNORECASE
    )

    # 1. Recherche de la section "Langues"
    match = re.search(r"(langues.*?)(expériences|formations|centres|$)", text, re.IGNORECASE | re.DOTALL)
    if match:
        bloc = match.group(1)
        lignes_bloc = bloc.splitlines()
        for ligne in lignes_bloc:
            for result in langues_pattern.finditer(ligne):
                langue = result.group(1).capitalize()
                niveau_raw = result.group(2).lower().strip()

                # Conversion des scores TOEIC/TOEFL en niveaux européens
                if "toeic" in niveau_raw:
                    score = int(re.search(r"\d+", niveau_raw).group())
                    if score >= 900:
                        niveau = "C1"
                    elif score >= 785:
                        niveau = "B2"
                    else:
                        niveau = "B1"
                elif "toefl" in niveau_raw:
                    score = int(re.search(r"\d+", niveau_raw).group())
                    if score >= 95:
                        niveau = "C1"
                    elif score >= 72:
                        niveau = "B2"
                    else:
                        niveau = "B1"
                else:
                    # Normalisation des niveaux textuels
                    correspondances = {
                        "débutant": "A1",
                        "intermédiaire": "B1",
                        "courant": "C1",
                        "bilingue": "C2"
                    }
                    niveau = correspondances.get(niveau_raw, niveau_raw.upper())

                infos["langues"].append({"langue": langue, "niveau": niveau})

    # 2. Fallback : recherche simple sur tout le texte (langue + niveau A1-C2)
    if not infos["langues"]:
        lignes = text.strip().splitlines()
        for ligne in lignes:
            match = re.search(r"(anglais|français|espagnol|allemand|italien)[^\n]*(A1|A2|B1|B2|C1|C2)", ligne, re.IGNORECASE)
            if match:
                infos["langues"].append({
                    "langue": match.group(1).capitalize(),
                    "niveau": match.group(2).upper()
                })

    # Supprimer doublons (au cas où)
    seen = set()
    langues_uniques = []
    for item in infos["langues"]:
        key = (item["langue"], item["niveau"])
        if key not in seen:
            langues_uniques.append(item)
            seen.add(key)
    infos["langues"] = langues_uniques

def extract_experiences(text, infos):
    infos["experiences"] = []

    # 1. Recherche de la section "Expériences"
    match = re.search(r"(expériences?.*?)(formations|compétences|langues|centres|parcours|$)", text, re.IGNORECASE | re.DOTALL)
    if not match:
        # Fallback simple : découpage en blocs par double saut de ligne, chercher mots-clés ou années
        blocs = text.split("\n\n")
        for bloc in blocs:
            if re.search(r"(stage|CDD|CDI|freelance|alternance|intérim)", bloc, re.I) or re.search(r"\b\d{4}\b", bloc):
                infos["experiences"].append({"description": bloc.strip()})
        return infos["experiences"]

    bloc = match.group(1).strip()
    lignes = bloc.splitlines()
    buffer = [ligne.strip() for ligne in lignes if ligne.strip() and not ligne.lower().startswith("formation")]

    i = 0
    while i < len(buffer):
        poste = ""
        entreprise = ""
        debut = ""
        fin = ""
        description_lignes = []

        # 2. Poste (mot-clé métier)
        while i < len(buffer):
            ligne = buffer[i]
            if re.search(r"\b(developpeur|designer|assistant|assistante|ingénieur|chef|chargé|commercial|technicien|manager|consultant|stagiaire|analyste|opérateur|agent)\b", ligne, re.IGNORECASE):
                poste = ligne
                i += 1
                break
            i += 1

        # 3. Entreprise (ligne suivante si pas date)
        if i < len(buffer):
            ligne = buffer[i]
            if not re.search(r"\d{4}|\d{2}/\d{4}|présent|en cours", ligne.lower()):
                entreprise = ligne
                i += 1

        # 4. Dates (recherche dans les lignes proches)
        date_block = " ".join(buffer[max(0, i - 3):min(len(buffer), i + 3)])
        date_match = re.search(
            r"(?:(\d{2}/\d{4}|\w+\s+\d{4}|\d{4}))\s*[-à–>]*\s*(\d{2}/\d{4}|\w+\s+\d{4}|présent|en cours)?",
            date_block,
            re.IGNORECASE
        )
        if date_match:
            debut = date_match.group(1).strip() if date_match.group(1) else ""
            fin = date_match.group(2).strip() if date_match.group(2) else ""

        # 5. Description (jusqu’au prochain poste ou fin)
        while i < len(buffer):
            ligne = buffer[i]
            if ligne.lower().startswith("formation") or re.search(r"\b(developpeur|designer|assistant|assistante|ingénieur|chef|chargé|commercial|technicien|manager|consultant|stagiaire|analyste|opérateur|agent)\b", ligne, re.IGNORECASE):
                break
            description_lignes.append(re.sub(r"^[-•·*→‣\s]+", "", ligne))
            i += 1

        if poste:
            infos["experiences"].append({
                "poste": poste,
                "entreprise": entreprise,
                "debut": debut,
                "fin": fin,
                "description": " ".join(description_lignes).strip()
            })

    return infos["experiences"]

def extract_formations(text, infos):
    infos["formations"] = []

    # Recherche de la section formations
    match = re.search(r"(formations?.*?)(centres|$)", text, re.IGNORECASE | re.DOTALL)
    if not match:
        # fallback simple : découpe en blocs par double saut de ligne et cherche mots clés diplômes
        blocs = text.split("\n\n")
        for bloc in blocs:
            if re.search(r"(BAC|BTS|DUT|Licence|Master|Doctorat|MBA|CAP|BEP|Bachelor|Ingénieur)", bloc, re.I):
                infos["formations"].append({"texte": bloc.strip()})
        return infos["formations"]

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
            # Cherche une année (ex: 2022 ou 2021-2023)
            annee_match = re.search(r"\d{4}(?:[-/]\d{4})?", ligne)
            annee = annee_match.group() if annee_match else ""

            # Etablissement : ligne suivante si existe
            etablissement = lignes[i+1].strip() if i + 1 < len(lignes) else ""

            infos["formations"].append({
                "diplome": ligne,
                "etablissement": etablissement,
                "annee": annee
            })

    return infos["formations"]

def exporter_vers_xml(infos, chemin_fichier):
    from xml.etree.ElementTree import Element, SubElement, ElementTree

    racine = Element("CV")

    # Identité
    idf = SubElement(racine, "Identite")
    SubElement(idf, "Prenom").text = infos.get("prenom", "")
    SubElement(idf, "Nom").text = infos.get("nom", "")
    SubElement(idf, "Email").text = infos.get("email", "")
    SubElement(idf, "Telephone").text = infos.get("telephone", "")
    SubElement(idf, "Adresse").text = infos.get("adresse", "")

    # Compétences
    comps = SubElement(racine, "Competences")
    for mot in infos.get("competences", []):
        SubElement(comps, "MotCle").text = mot

    # Langues
    langs = SubElement(racine, "Langues")
    for lg in infos.get("langues", []):
        l = SubElement(langs, "Langue")
        SubElement(l, "Nom").text = lg.get("langue", "")
        SubElement(l, "Niveau").text = lg.get("niveau", "")

    # Expériences
    exps = SubElement(racine, "Experiences")
    for exp in infos.get("experiences", []):
        e = SubElement(exps, "Experience")
        SubElement(e, "Poste").text = exp.get("poste", "")
        SubElement(e, "Entreprise").text = exp.get("entreprise", "")
        SubElement(e, "Debut").text = exp.get("debut", "")
        SubElement(e, "Fin").text = exp.get("fin", "")
        SubElement(e, "Description").text = exp.get("description", "")

    # Formations
    forms = SubElement(racine, "Formations")
    for f in infos.get("formations", []):
        fo = SubElement(forms, "Formation")
        SubElement(fo, "Diplome").text = f.get("diplome", "")
        SubElement(fo, "Etablissement").text = f.get("etablissement", "")
        SubElement(fo, "Annee").text = f.get("annee", "")

    tree = ElementTree(racine)
    tree.write(chemin_fichier, encoding="utf-8", xml_declaration=True)


def parser_experiences(experiences_brutes):
    result = []
    for exp in experiences_brutes:
        # Si c'est déjà un dict, on l'ajoute tel quel
        if isinstance(exp, dict):
            result.append(exp)
            continue
        
        # Sinon on traite comme une string brute
        lignes = exp.split("\n")
        dates = lignes[0] if len(lignes) > 0 else ""
        poste_entreprise = lignes[1] if len(lignes) > 1 else ""
        description = "\n".join(lignes[2:]) if len(lignes) > 2 else ""

        debut, fin = "", ""
        if "-" in dates:
            debut, fin = map(str.strip, dates.split("-", 1))
        else:
            debut = dates.strip()

        poste, entreprise = "", ""
        if "," in poste_entreprise:
            poste, entreprise = map(str.strip, poste_entreprise.split(",", 1))
        else:
            poste = poste_entreprise.strip()

        result.append({
            "poste": poste,
            "entreprise": entreprise,
            "debut": debut,
            "fin": fin,
            "description": description
        })
    return result


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

        if "experiences" in infos and infos["experiences"]:
            infos["experiences"] = parser_experiences(infos["experiences"])
        else:
            infos["experiences"] = []

        nom_xml = os.path.splitext(fichier)[0] + ".xml"
        chemin_xml = os.path.join(dossier_output, nom_xml)
        exporter_vers_xml(infos, chemin_xml)

        print(f"✅ {fichier} → {nom_xml}")

    print("🎉 Tous les CV ont été traités.")

if __name__ == "__main__":
    main()