from spacy import load
from spacy.matcher import Matcher



def extraire_nom(texte_cv):
    # Charger le modèle pré-entraîné
    #nlp = spacy.load('fr_core_news_lg')
    nlp = load('en_core_web_sm')

    # Initialiser le Matcher avec un vocabulaire
    matcher = Matcher(nlp.vocab)

    nlp_texte = nlp(texte_cv)

    # Le prénom et le nom de famille sont toujours des noms propres
    #motif = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    motif = [{'POS': 'PROPN', 'IS_TITLE': True}, {'POS': 'PROPN'}]

    matcher.add('NOM', [motif])

    correspondances = matcher(nlp_texte)

    for id_correspondance, debut, fin in correspondances:
        portion_texte = nlp_texte[debut:fin]
        return portion_texte.text
