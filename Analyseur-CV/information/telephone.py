import re


def extraire_numero_telephone(texte_cv):
    mob_num_regex = r"((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}|\d{1}\s*\d{2}[-\.\s]??\d{2}[-\.\s]??\d{2}[-\.\s]??\d{2}))"
    num = re.findall(re.compile(mob_num_regex), texte_cv)

    if num:
        numero = ''.join(num[0])
        return numero