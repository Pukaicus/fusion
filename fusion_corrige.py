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
        "email": "",
        "telephone": "",
        "adresse": "",
        "competences": [],
        "langues": [],
        "experiences": [],
        "formations": []
    }

    # Extraction qui modifie directement infos
    extract_adresse(text)
    extract_competences(text)
    extract_langues(text)
    extract_experiences(text, infos)
    extract_formations(text, infos)

    # Extraction qui retourne une valeur
    prenom, nom = extract_prenom_nom(text)
    infos["prenom"] = prenom or ""
    infos["nom"] = nom or ""
    infos["email"] = extract_email(text) or ""
    infos["telephone"] = extract_phone(text) or ""

    return infos


def extract_email(text):
    if not text:
        return None

    # Nettoyer le texte pour enlever les caractères non valides (sauf ceux utiles pour email)
    # On enlève tout sauf lettres, chiffres, underscore, point, plus, tiret, arobase, espaces
    text = re.sub(r"[^\w\s@.+-]", " ", text)

    # Regex standard d'email (simple)
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group().strip() if match else None



import re

def extract_phone(text):
    if not text:
        return None

    # Garder uniquement chiffres, +, espaces, (), ., -, / (ajouté /)
    cleaned_text = re.sub(r"[^\d+()\s.\-\/]", " ", text)

    # Regex téléphone français classique
    # +33 ou 0, suivi de 9 chiffres regroupés en 4 groupes de 2 chiffres, séparés par espace, point, tiret, slash, parenthèses possibles
    pattern = r"(?:\+33|0)[\s.\-\(\)\/]*(?:[1-9][\s.\-\(\)\/]*\d{2}){4}"

    match = re.search(pattern, cleaned_text)
    if match:
        numero = re.sub(r"[\s.\-\(\)\/]", "", match.group())
        return numero.strip()

    # En dernier recours, chercher 10 chiffres consécutifs (ex: 0612345678)
    match = re.search(r"\b0\d{9}\b", cleaned_text)
    if match:
        return match.group().strip()

    return None


def extract_prenom_nom(text):
    # Liste des mots interdits dans une ligne nom/prénom (mots à exclure)
    blacklist = [
        "expérience", "contact", "compétences", "formation", "adresse", "email", "téléphone",
        "ressources", "humaines", "centre", "intérêt", "intérêts", "loisir", "loisirs",
        "profil", "cv", "à propos", "présentation", "objectif", "références", "informations",
        "personnelles", "dream", "weaver", "ms-dos", "langages", "logiciel", "informatique",
        "programmation", "c++", "java", "python", "sql", "html", "css", "javascript",
        "animation", "power", "point", "développeur", "concepteur", "d'applications",
    ]

    # Ensemble des mots non admissibles comme nom (en majuscule)
    mots_non_nom = set([
        "DREAM", "WEAVER", "MS-DOS", "LANGAGES", "LOGICIEL", "INFORMATIQUE",
        "PROGRAMMATION", "CV", "PROFIL", "OBJECTIF", "CONTACT",
        "ANIMATION", "POWER", "POINT", "DÉVELOPPEUR", "CONCEPTEUR", "D'APPLICATIONS",
    ])

    def is_blacklisted(line):
        line_lower = line.lower()
        return any(mot in line_lower for mot in blacklist)

    def ligne_semble_nom(line):
        if not line:
            return False
        # Si la ligne contient chiffres, caractères spéciaux => non nom
        if re.search(r"[\d@#\$%\^&\*\(\)_=\+\[\]\{\}\\\/<>]", line):
            return False
        mots = line.split()
        # La ligne doit contenir entre 2 et 4 mots
        if not (2 <= len(mots) <= 4):
            return False
        # Chaque mot doit être une chaîne alphabétique (possiblement avec un tiret)
        for m in mots:
            if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ']+(-[A-Za-zÀ-ÖØ-öø-ÿ']+)?$", m):
                return False
        # Le dernier mot ne doit pas être dans la liste mots_non_nom
        if mots[-1].upper() in mots_non_nom:
            return False
        # Au moins un mot commence par une majuscule ou est entièrement en majuscule
        if not any(m[0].isupper() or m.isupper() for m in mots):
            return False
        return True

    lignes = [l.strip() for l in text.strip().splitlines() if l.strip()]
    infos = {"prenom": "", "nom": ""}

    # 1) Recherche dans les premières 10 lignes
    for line in lignes[:10]:
        if is_blacklisted(line):
            continue
        if ligne_semble_nom(line):
            mots = line.split()
            infos["prenom"] = " ".join(m.capitalize() for m in mots[:-1])
            infos["nom"] = mots[-1].capitalize()
            return infos["prenom"], infos["nom"]

    # 2) Recherche "Prénom : ..." et "Nom : ..."
    for line in lignes[:40]:
        line_lower = line.lower()
        if "prénom" in line_lower and ":" in line:
            infos["prenom"] = line.split(":", 1)[1].strip().capitalize()
        if "nom" in line_lower and ":" in line:
            infos["nom"] = line.split(":", 1)[1].strip().capitalize()
        if infos["prenom"] and infos["nom"]:
            return infos["prenom"], infos["nom"]

    # 3) Recherche juste avant "contact"
    for i, line in enumerate(lignes):
        if "contact" in line.lower():
            for j in range(max(0, i - 20), i):
                candidate = lignes[j]
                if not is_blacklisted(candidate) and ligne_semble_nom(candidate):
                    mots = candidate.split()
                    infos["prenom"] = " ".join(m.capitalize() for m in mots[:-1])
                    infos["nom"] = mots[-1].capitalize()
                    return infos["prenom"], infos["nom"]
            break

    # 4) Prénoms courants + nom (ou tout en majuscule)
    prenoms_courants = {"Lucas", "Emma", "Léa", "Louis", "Chloé", "Nathan", "Manon", "Jules", "Camille"}
    for line in lignes[:40]:
        if is_blacklisted(line):
            continue
        mots = line.split()
        if len(mots) >= 2:
            mots_avec_maj = [m for m in mots if m[0].isupper() or m.isupper()]
            if not mots_avec_maj:
                continue
            # Si la ligne est tout en majuscule (ex: NOM)
            if line.isupper():
                infos["nom"] = mots[-1].capitalize()
                infos["prenom"] = " ".join(m.capitalize() for m in mots[:-1])
                return infos["prenom"], infos["nom"]
            for m in mots:
                if m.capitalize() in prenoms_courants:
                    infos["prenom"] = m.capitalize()
                    infos["nom"] = mots[-1].capitalize()
                    return infos["prenom"], infos["nom"]

    # 5) Fallback : première ligne avec au moins 2 mots
    for line in lignes[:40]:
        if not is_blacklisted(line):
            mots = line.split()
            if len(mots) >= 2:
                infos["prenom"] = mots[0].capitalize()
                infos["nom"] = mots[1].capitalize()
                return infos["prenom"], infos["nom"]

    # Si rien trouvé
    return "", ""

import re

def extract_adresse(text):
    lignes = [l.strip() for l in text.strip().splitlines() if l.strip()]
    
    def nettoyer_texte_ligne(ligne):
        # Nettoyer caractères parasites sauf lettres, chiffres, espaces, virgules, points, tirets
        return re.sub(r"[^\w\s,.\-]", "", ligne)
    
    sections_suivantes = [
        "téléphone", "email", "mail", "e-mail", "compétences", "langues",
        "expériences", "formations", "centres", "objectifs", "profil",
        "loisirs", "intérêts", "contact", "adresse", "domicile", "résidence", "habitation"
    ]
    
    adresse_lignes = []
    in_adresse = False
    
    for idx, ligne in enumerate(lignes):
        ligne_nettoyee = nettoyer_texte_ligne(ligne)
        ligne_lower = ligne_nettoyee.lower()
        
        if not in_adresse:
            if "adresse" in ligne_lower or "domicile" in ligne_lower or "résidence" in ligne_lower:
                in_adresse = True
                # Test ligne avant si possible
                if idx > 0:
                    prev_line = nettoyer_texte_ligne(lignes[idx - 1])
                    if len(prev_line) > 10:
                        adresse_lignes.append(prev_line)
                # Si la ligne contient "Adresse: valeur", on récupère la partie après ":"
                apres_adresse = ligne.split(":", 1)
                if len(apres_adresse) > 1 and apres_adresse[1].strip():
                    adresse_lignes.append(apres_adresse[1].strip())
                continue
        else:
            if any(mot in ligne_lower for mot in sections_suivantes if mot != "adresse"):
                # Exception : ligne courte et ressemble à une ville, on continue un peu
                if len(ligne_nettoyee.split()) <= 2 and re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\-]+$", ligne_nettoyee):
                    adresse_lignes.append(ligne_nettoyee)
                    continue
                break
            adresse_lignes.append(ligne_nettoyee)
    
    adresse_complete = " ".join(adresse_lignes).strip()
    if adresse_complete:
        return adresse_complete
    
    # Fallback regex : adresse typique française avec numéro, nom de rue, code postal, ville
    adresse_pattern = re.compile(
        r"(\d{1,4}\s(?:[A-Za-zÀ-ÖØ-öø-ÿ'\-\.]+\s?){1,6},?\s*\d{5}\s+[A-Za-zÀ-ÖØ-öø-ÿ'\-\.]+)",
        re.IGNORECASE
    )
    
    for i, line in enumerate(lignes):
        line_nettoyee = nettoyer_texte_ligne(line)
        match = adresse_pattern.search(line_nettoyee)
        if match:
            return match.group(1).strip()
        # Test sur deux lignes concaténées (cas adresse scindée)
        if i + 1 < len(lignes):
            combined = line_nettoyee + " " + nettoyer_texte_ligne(lignes[i + 1])
            match = adresse_pattern.search(combined)
            if match:
                return match.group(1).strip()
    
    # Fallback simple : détecte ligne contenant mots typiques de rues
    mots_cles = ["rue", "avenue", "boulevard", "impasse", "chemin", "allée", "place", "route"]
    for ligne in lignes:
        ligne_nettoyee = nettoyer_texte_ligne(ligne)
        if any(mot in ligne_nettoyee.lower() for mot in mots_cles):
            return ligne_nettoyee.strip()
    
    # Tentative ville proche de "contact"
    for i, line in enumerate(lignes):
        line_nettoyee = nettoyer_texte_ligne(line)
        if "contact" in line_nettoyee.lower() and i > 0:
            ville = nettoyer_texte_ligne(lignes[i-1])
            if re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\-]+$", ville) and len(ville.split()) <= 2:
                return ville.strip()
    
    return ""  # Rien trouvé


def extract_competences(text):
    """
    Extrait les compétences d'un texte de CV, en ciblant la section 'Compétences' puis en recherchant des listes à puces ou mots-clés pertinents.
    Retourne une liste de compétences uniques, en minuscules.
    """
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
    mots_vides = set(mots_vides)

    mots_reconnus = {
        "python", "java", "html", "css", "javascript", "php", "sql", "bash", "linux",
        "git", "github", "vscode", "docker", "flask", "django", "symfony", "react",
        "node", "json", "xml", "api", "uml", "agile", "scrum", "jira",
        "autonome", "rigoureux", "créatif", "esprit", "communication", "organisé",
        "curieux", "motivé", "adaptabilité", "gestion", "stress", "travail",
        "word", "excel", "powerpoint", "outlook", "teams", "office", "microsoft", "developper",
        "superviser", "représenter", "prendre", "gérer"
    }
    mots_reconnus = set(mots_reconnus)

    competences = []

    pattern_bloc = re.compile(r"(compétences.*?)(langues|expériences|formations|centres|$)", re.IGNORECASE | re.DOTALL)
    match = pattern_bloc.search(text)
    if match:
        bloc = match.group(1)
        lignes = bloc.splitlines()
        for ligne in lignes:
            m = re.match(r"^\s*[-•·]\s*(.+)", ligne)
            if m:
                mot = m.group(1).strip().lower()
                mot = re.sub(r"[^\w\-\+\.]", " ", mot)  # remplacer ponctuation par espace
                # extraire mots et expressions de 2-3 mots
                mots = mot.split()
                # single mots
                for mot_unique in mots:
                    if mot_unique and mot_unique not in mots_vides:
                        competences.append(mot_unique)
                # bigrams et trigrams
                for i in range(len(mots)-1):
                    bigram = mots[i] + " " + mots[i+1]
                    if all(w not in mots_vides for w in bigram.split()):
                        competences.append(bigram)
                for i in range(len(mots)-2):
                    trigram = mots[i] + " " + mots[i+1] + " " + mots[i+2]
                    if all(w not in mots_vides for w in trigram.split()):
                        competences.append(trigram)
            else:
                # extraction mot à mot dans phrase
                mots = re.findall(r"\b\w[\w\-+\.]*\b", ligne.lower())
                for mot in mots:
                    mot_clean = mot.strip()
                    if mot_clean and mot_clean not in mots_vides and (mot_clean in mots_reconnus or len(mot_clean) >= 4):
                        competences.append(mot_clean)

    # fallback pareil...

    # Suppression doublons
    vus = set()
    competences_uniques = []
    for c in competences:
        if c not in vus:
            competences_uniques.append(c)
            vus.add(c)

    return competences_uniques


def normalize_score_to_level(score, test_type):
    if test_type == "toeic":
        if score >= 900:
            return "C1"
        elif score >= 785:
            return "B2"
        else:
            return "B1"
    elif test_type == "toefl":
        if score >= 95:
            return "C1"
        elif score >= 72:
            return "B2"
        else:
            return "B1"
    return ""

def extract_langues(text):
    """
    Extrait les langues et niveaux d'un texte de CV.
    Retourne une liste de dicts : [{"langue": ..., "niveau": ...}, ...]
    """
    langues = []

    # Pattern pour langues + niveaux standards ou scores TOEIC/TOEFL
    langues_pattern = re.compile(
        r"\b(\w+)\b\s*[-:|]*\s*(A1|A2|B1|B2|C1|C2|débutant|intermédiaire|courant|bilingue|TOEIC\s*\d+|TOEFL\s*\d+)",
        re.IGNORECASE
    )

    # Recherche section "Langues" si existante
    match = re.search(r"(langues.*?)(expériences|formations|centres|$)", text, re.IGNORECASE | re.DOTALL)
    if match:
        bloc = match.group(1)
        for ligne in bloc.splitlines():
            for result in langues_pattern.finditer(ligne):
                langue = result.group(1).capitalize()
                niveau_raw = result.group(2).lower().strip()

                if "toeic" in niveau_raw:
                    score = int(re.search(r"\d+", niveau_raw).group())
                    niveau = normalize_score_to_level(score, "toeic")
                elif "toefl" in niveau_raw:
                    score = int(re.search(r"\d+", niveau_raw).group())
                    niveau = normalize_score_to_level(score, "toefl")
                else:
                    correspondances = {
                        "débutant": "A1",
                        "intermédiaire": "B1",
                        "courant": "C1",
                        "bilingue": "C2"
                    }
                    niveau = correspondances.get(niveau_raw, niveau_raw.upper())

                langues.append({"langue": langue, "niveau": niveau})

    # Fallback : rechercher globalement dans le texte
    if not langues:
        fallback_pattern = re.compile(
            r"(anglais|français|espagnol|allemand|italien)[^\n]*?(A1|A2|B1|B2|C1|C2)", re.IGNORECASE
        )
        for ligne in text.strip().splitlines():
            match = fallback_pattern.search(ligne)
            if match:
                langues.append({
                    "langue": match.group(1).capitalize(),
                    "niveau": match.group(2).upper()
                })

    # Suppression des doublons
    vus = set()
    result = []
    for item in langues:
        key = (item["langue"], item["niveau"])
        if key not in vus:
            result.append(item)
            vus.add(key)

    return result

def extract_experiences(text, infos):
    infos["experiences"] = []

    # Recherche de la section "Expériences"
    match = re.search(r"(expériences?.*?)(formations|compétences|langues|centres|parcours|$)", text, re.IGNORECASE | re.DOTALL)
    if not match:
        # Fallback simple : découpage en blocs par double saut de ligne, chercher mots-clés ou années
        blocs = text.split("\n\n")
        for bloc in blocs:
            if re.search(r"(stage|CDD|CDI|freelance|alternance|intérim)", bloc, re.I) or re.search(r"\b\d{4}\b", bloc):
                infos["experiences"].append({"description": bloc.strip()})
        return infos["experiences"]

    bloc = match.group(1).strip()
    lignes = [l.strip() for l in bloc.splitlines() if l.strip()]
    
    mots_metiers = [
        "developpeur", "designer", "assistant", "assistante", "ingénieur", "chef",
        "chargé", "commercial", "technicien", "manager", "consultant", "stagiaire",
        "analyste", "opérateur", "agent", "responsable", "animateur", "formateur",
        "directeur", "architecte", "vendeur", "coordinateur", "secrétaire"
    ]
    villes_secteurs = ["Paris", "Lyon", "Marseille", "Bordeaux", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier"]

    def est_metier(ligne):
        return any(re.search(r"\b" + mot + r"\b", ligne, re.IGNORECASE) for mot in mots_metiers)

    def extraire_dates(ligne):
        # Recherche toutes les dates dans la ligne et retourne min et max
        patterns = [
            r"(\d{4})\s*[-–—]\s*(aujourd’hui|en cours|présent|\d{4})",
            r"(depuis|à partir de|à compter de)\s*(\d{4})",
            r"((?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s*\d{4})\s*[-–—]\s*((?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s*\d{4}|aujourd’hui|en cours|présent)",
            r"\b(\d{4})\b",
        ]
        dates = []
        for pat in patterns:
            for m in re.finditer(pat, ligne, re.IGNORECASE):
                debut = m.group(1).strip()
                fin = m.group(2).strip() if len(m.groups()) > 1 else ""
                if fin.lower() in ["aujourd’hui", "en cours", "présent"]:
                    fin = "aujourd’hui"
                if debut.lower() in ["depuis", "à partir de", "à compter de"]:
                    debut = m.group(2).strip()
                    fin = "aujourd’hui"
                dates.append((debut, fin))
        if dates:
            debuts = [d[0] for d in dates]
            fins = [d[1] for d in dates if d[1]]
            return min(debuts), max(fins) if fins else ""
        return "", ""

    i = 0
    n = len(lignes)

    while i < n:
        ligne = lignes[i]
        poste = ""
        entreprise = ""
        ville = ""
        debut = ""
        fin = ""
        description_lignes = []

        # Trouver le poste
        if est_metier(ligne):
            poste = ligne
            i += 1
        elif i + 1 < n and est_metier(lignes[i + 1]):
            poste = lignes[i + 1]
            i += 2
        else:
            i += 1
            continue

        # Chercher entreprise
        if i < n and not re.search(r"\d{4}|présent|en cours|aujourd’hui", lignes[i], re.IGNORECASE):
            entreprise = lignes[i]
            i += 1

        # Extraire dates dans les lignes proches
        range_dates = lignes[max(0, i-3): min(n, i+3)]
        debut, fin = "", ""
        for ld in range_dates:
            d, f = extraire_dates(ld)
            if d or f:
                debut, fin = d, f
                break

        # Extraire ville dans poste ou entreprise
        for v in villes_secteurs:
            if v.lower() in poste.lower():
                ville = v
                poste = re.sub(v, "", poste, flags=re.IGNORECASE).strip()
            elif v.lower() in entreprise.lower():
                ville = v
                entreprise = re.sub(v, "", entreprise, flags=re.IGNORECASE).strip()

        # Description jusqu’à prochaine expérience ou fin
        while i < n:
            ligne_desc = lignes[i]
            if est_metier(ligne_desc) or re.search(r"formations?", ligne_desc, re.IGNORECASE):
                break
            description_lignes.append(re.sub(r"^[-•·*→‣\s]+", "", ligne_desc))
            i += 1

        infos["experiences"].append({
            "poste": poste,
            "entreprise": entreprise,
            "ville": ville,
            "debut": debut,
            "fin": fin,
            "description": "\n".join(description_lignes).strip()
        })

    return infos["experiences"]



def extract_formations(text, infos):
    infos["formations"] = []

    # Recherche section formations
    match = re.search(r"(formations?.*?)(centres|$)", text, re.IGNORECASE | re.DOTALL)

    diplomes_connus = [
        "BTS", "DUT", "Licence", "Master", "MBA", "Doctorat",
        "CAP", "BEP", "Bac", "Bachelor", "Ingénieur",
        "Titre professionnel", "Diplôme universitaire", "Prépa", "DNA"
    ]

    def is_diplome_line(ligne):
        return any(d.lower() in ligne.lower() for d in diplomes_connus)

    def normaliser_diplome(ligne):
        # Exemple : "BTS SIO" -> "BTS SIO" (on garde toute la ligne)
        # Si seulement "BTS" détecté, on laisse tel quel (pas d'info complémentaire)
        # Sinon on peut appliquer d'autres règles de normalisation ici
        return ligne.strip()

    if not match:
        # Pas de section dédiée, fallback : découper en blocs et détecter diplômes
        blocs = text.split("\n\n")
        for bloc in blocs:
            if is_diplome_line(bloc):
                # Extraire années (4 chiffres ou fourchette)
                annee_match = re.search(r"(\d{4})(?:[-/](\d{4}))?", bloc)
                annee = annee_match.group(0) if annee_match else ""
                lignes = bloc.strip().splitlines()
                diplome = normaliser_diplome(lignes[0]) if lignes else bloc.strip()
                # Pour établissement, concaténer toutes les lignes sauf la 1ère
                etablissement = " ".join(lignes[1:]).strip() if len(lignes) > 1 else ""
                infos["formations"].append({
                    "diplome": diplome,
                    "etablissement": etablissement,
                    "annee": annee
                })
        return infos["formations"]



    bloc = match.group(1).strip()
    lignes = [l.strip() for l in bloc.splitlines() if l.strip()]
    i = 0
    n = len(lignes)

    while i < n:
        ligne = lignes[i]
        if is_diplome_line(ligne):
            diplome = normaliser_diplome(ligne)

            # Chercher année dans la même ligne
            annee_match = re.search(r"(\d{4})(?:[-/](\d{4}))?", ligne)
            annee = annee_match.group(0) if annee_match else ""

            # Chercher établissement sur plusieurs lignes suivantes jusqu'à une autre formation ou fin
            etablissement_lignes = []
            i += 1
            while i < n and not is_diplome_line(lignes[i]):
                # Arrêter si ligne correspond à autre section ou mot clé
                if re.search(r"(centres|compétences|expériences?|langues?|objectifs?|profil|contact)", lignes[i], re.IGNORECASE):
                    break
                etablissement_lignes.append(lignes[i])
                i += 1

            etablissement = " ".join(etablissement_lignes).strip()

            infos["formations"].append({
                "diplome": diplome,
                "etablissement": etablissement,
                "annee": annee
            })
        else:
            i += 1

    return infos["formations"]


import xml.etree.ElementTree as ET
import xml.dom.minidom

def nettoyer_texte(texte):
    if not texte:
        return ""
    return str(texte).strip()

def exporter_vers_xml(infos, chemin_fichier, pretty_print=True):
    racine = ET.Element("CV")

    # Identité
    idf = ET.SubElement(racine, "Identite")
    ET.SubElement(idf, "Prenom").text = nettoyer_texte(infos.get("prenom"))
    ET.SubElement(idf, "Nom").text = nettoyer_texte(infos.get("nom"))
    ET.SubElement(idf, "Email").text = nettoyer_texte(infos.get("email"))
    ET.SubElement(idf, "Telephone").text = nettoyer_texte(infos.get("telephone"))
    ET.SubElement(idf, "Adresse").text = nettoyer_texte(infos.get("adresse"))

    # Compétences
    comps = ET.SubElement(racine, "Competences")
    for mot in infos.get("competences", []):
        if mot and mot.strip():
            ET.SubElement(comps, "MotCle").text = nettoyer_texte(mot)

    # Langues
    langs = ET.SubElement(racine, "Langues")
    for lg in infos.get("langues", []):
        if isinstance(lg, dict):
            l = ET.SubElement(langs, "Langue")
            ET.SubElement(l, "Nom").text = nettoyer_texte(lg.get("langue"))
            ET.SubElement(l, "Niveau").text = nettoyer_texte(lg.get("niveau"))

    # Expériences
    exps = ET.SubElement(racine, "Experiences")
    for exp in infos.get("experiences", []):
        if isinstance(exp, dict):
            e = ET.SubElement(exps, "Experience")
            ET.SubElement(e, "Poste").text = nettoyer_texte(exp.get("poste"))
            ET.SubElement(e, "Entreprise").text = nettoyer_texte(exp.get("entreprise"))
            ET.SubElement(e, "Debut").text = nettoyer_texte(exp.get("debut"))
            ET.SubElement(e, "Fin").text = nettoyer_texte(exp.get("fin"))
            ET.SubElement(e, "Description").text = nettoyer_texte(exp.get("description"))

    # Formations
    forms = ET.SubElement(racine, "Formations")
    for f in infos.get("formations", []):
        if isinstance(f, dict):
            fo = ET.SubElement(forms, "Formation")
            ET.SubElement(fo, "Diplome").text = nettoyer_texte(f.get("diplome"))
            ET.SubElement(fo, "Etablissement").text = nettoyer_texte(f.get("etablissement"))
            ET.SubElement(fo, "Annee").text = nettoyer_texte(f.get("annee"))

    # Ecriture dans le fichier
    tree = ET.ElementTree(racine)

    if pretty_print:
        # XML indenté lisible
        xml_str = ET.tostring(racine, encoding='utf-8')
        reparsed = xml.dom.minidom.parseString(xml_str)
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            f.write(reparsed.toprettyxml(indent="  "))
    else:
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

        # Debugging : afficher les infos extraites
        print("--------- INFOS EXTRACTÉES ---------")
        print(f"📄 Fichier : {fichier}")
        print(f"Prénom détecté : {infos.get('prenom', '')}")
        print(f"Nom détecté : {infos.get('nom', '')}")
        print(f"Email détecté : {infos.get('email', '')}")
        print(f"Téléphone détecté : {infos.get('telephone', '')}")
        print(f"Adresse détectée : {infos.get('adresse', '')}")
        print(f"Compétences : {infos.get('competences', [])}")
        print(f"Langues : {infos.get('langues', [])}")
        print(f"Expériences brutes : {infos.get('experiences', [])}")
        print(f"Formations : {infos.get('formations', [])}")
        print("------------------------------------\n")

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