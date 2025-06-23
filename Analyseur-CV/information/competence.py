from nltk import everygrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def extraire_competences(texte_cv):
    stop_words = set(stopwords.words('french'))
    mots_tokens = word_tokenize(texte_cv)

    # Supprimer les mots vides
    mots_filtres = [mot for mot in mots_tokens if mot not in stop_words]

    # Supprimer la ponctuation
    mots_filtres = [mot for mot in mots_tokens if mot.isalpha()]

    # Générer des bigrammes et des trigrammes (comme intelligence artificielle)
    bigrammes_trigrammes = list(map(' '.join, everygrams(mots_filtres, 2, 3)))

    # Créer un ensemble pour stocker les résultats
    competences_trouvees = set()

    with open('./Data/skills_db.txt', 'r', encoding='utf-8') as fichier:
        donnees_competences = fichier.read().splitlines()

    # Rechercher chaque jeton dans notre base de données de compétences
    for jeton in mots_filtres:
        if jeton.lower() in donnees_competences:
            competences_trouvees.add(jeton)

    # Rechercher chaque bigramme et trigramme dans notre base de données de compétences
    for ngramme in bigrammes_trigrammes:
        if ngramme.lower() in donnees_competences:
            competences_trouvees.add(ngramme)

    return competences_trouvees
