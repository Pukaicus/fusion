from nltk import sent_tokenize
import spacy



def extraire_education(texte_cv):
    organizations = []

    # Chargement du modèle spaCy pour le français
    nlp = spacy.load('fr_core_news_lg')

    # Obtenir tous les noms d'organisations en utilisant spaCy
    for sent in sent_tokenize(texte_cv):
        doc = nlp(sent)
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                organizations.append(ent.text)

    # Recherche des mots réservés pour l'éducation
    education = set()

    with open('./Data/education.txt', 'r', encoding='utf-8') as file:
        reserved_words = file.read().splitlines()

    for org in organizations:
        for word in reserved_words:
            if org.lower().find(word) >= 0:
                education.add(org)


    return education
