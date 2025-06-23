# Executer avant :
# pip install -r requirements.txt
# python nltk_data.py
# python -m spacy download fr_core_news_lg
# python -m spacy download fr_core_news_sm

# import tkinter
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

from tkinter import ttk
from tkinter import filedialog
from tkinter import X 

# import field extractor
from information.nom import * 
from information.education import * 
from information.telephone import * 
from information.email import * 
from information.competence import * 
import lecteurfichiers.pdf2text as pdf2text



from tkinter import filedialog as fd
import os
from tkinter import messagebox

def process(chemin_dossier, root):
    if not chemin_dossier:
        # Par sécurité
        from tkinter import messagebox
        messagebox.showinfo("Info", "Aucun dossier sélectionné.")
        return

    # Parcourir tous les fichiers PDF du dossier
    for fichier in os.listdir(chemin_dossier):
        if fichier.lower().endswith(".pdf"):
            chemin_pdf = os.path.join(chemin_dossier, fichier)
            print(f"\n📄 Traitement de : {fichier}")

            # Extraire le texte
            texte = pdf2text.get_Text(chemin_pdf)

            # Pour l'instant, on affiche juste le texte
            print(texte)

            # Extraire infos depuis texte (tu peux adapter selon ta fonction)
            nom              = extraire_nom(texte)
            numero_telephone = extraire_numero_telephone(texte)
            email            = extraire_email(texte)
            education        = extraire_education(texte)
            competences      = extraire_competences(texte)

            # Affichage dans une fenêtre (tu peux aussi adapter pour traiter plusieurs fichiers)
            fenetre_resultat = tk.Toplevel(root)
            fenetre_resultat.title(f"Infos extraites : {fichier}")
            fenetre_resultat.geometry("800x300")

            tk.Label(fenetre_resultat, text="Informations extraites", font=("Arial", 20)).grid(row=0, column=1, pady=10)

            tk.Label(fenetre_resultat, text="Nom \t: ").grid(row=1, column=0, sticky="w", padx=10)
            tk.Label(fenetre_resultat, text=f"{nom}").grid(row=1, column=1, sticky="w", padx=10)

            tk.Label(fenetre_resultat, text="Éducation\t: ").grid(row=2, column=0, sticky="w", padx=10)
            tk.Label(fenetre_resultat, text=f"{education}").grid(row=2, column=1, sticky="w", padx=10)

            tk.Label(fenetre_resultat, text="Téléphone\t: ").grid(row=3, column=0, sticky="w", padx=10)
            tk.Label(fenetre_resultat, text=f"{numero_telephone}").grid(row=3, column=1, sticky="w", padx=10)

            tk.Label(fenetre_resultat, text="Email\t: ").grid(row=4, column=0, sticky="w", padx=10)
            tk.Label(fenetre_resultat, text=f"{email}").grid(row=4, column=1, sticky="w", padx=10)

            tk.Label(fenetre_resultat, text="Compétences\t: ", anchor="w", justify=LEFT).grid(row=5, column=0, sticky="w", padx=10)
            tk.Label(fenetre_resultat, text="\n".join(competences), anchor="w", justify=LEFT, wraplength=200).grid(row=5, column=1, sticky="w", padx=10)



 
if __name__ == '__main__':
    from tkinter import filedialog as fd
    
    # Créer une fenêtre de 600x300 et centrer cela sur l'écran.
 # Taille et centrage de la fenêtre
    largeur = 600
    hauteur = 300

    root = tk.Tk()
    root.title("Analyseur de CV")

    largeur_ecran = root.winfo_screenwidth()
    hauteur_ecran = root.winfo_screenheight()
    x = int((largeur_ecran / 2) - (largeur / 2))
    y = int((hauteur_ecran / 2) - (hauteur / 2))

    root.geometry(f'{largeur}x{hauteur}+{x}+{y}')

    def ouvrir_dossier():
        # Ouvre la boîte de dialogue pour choisir un dossier
        chemin_dossier = filedialog.askdirectory(title="Sélectionner un dossier")
        if chemin_dossier:
            process(chemin_dossier, root)

    # Bouton pour parcourir un dossier
    bouton = ttk.Button(root, text='Parcourir un dossier', command=ouvrir_dossier)
    bouton.pack(fill=X)

    root.mainloop()
