# Analyseur de CV

Bienvenue dans l'Analyseur de CV, un projet développé en Python utilisant Tkinter, spaCy, nltk, et d'autres bibliothèques pour extraire des informations pertinentes à partir de CV au format PDF.

## Installation

1. Clonez le dépôt GitHub :

    ```bash
    git clone https://github.com/OussamaLay/Analyseur-CV.git
    ```

2. Accédez au répertoire du projet :

    ```bash
    cd Analyseur-de-CV
    ```

3. Installez les dépendances à l'aide de pip et du fichier requirements.txt :

    ```bash
    pip install -r requirements.txt
    ```

    Ceci installera toutes les librairies nécessaires.

4. Téléchargez les modèles spaCy pré-entraînés pour le français :

    ```bash
    python -m spacy download fr_core_news_lg
    python -m spacy download en_core_web_sm
    ```

    Assurez-vous d'avoir nltk installé et télécharger ces données avec la commande suivante :

    ```bash
    python nltk_data.py
    ```

## Utilisation

1. Exécutez le script principal :

    ```bash
    python index.py
    ```

2. Une fenêtre s'ouvrira, vous permettant de parcourir et analyser un fichier PDF de CV.

3. Suivez les instructions pour afficher les informations extraites telles que le nom, l'éducation, le numéro de téléphone, l'email et les compétences.

## Remarques

Assurez-vous d'avoir correctement configuré votre environnement Python et les modèles nécessaires avant d'exécuter le script.

L'affichage des informations peut prendre quelques secondes en raison du traitement.

---

