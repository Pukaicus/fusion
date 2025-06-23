import re
 


def extraire_email(texte_cv):
    adresse_email = re.findall(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', texte_cv)
    if adresse_email:
        try:
            return adresse_email[0].split()[0].strip(';')
        except IndexError:
            return None
