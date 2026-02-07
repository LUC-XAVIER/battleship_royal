#from corrige import *
import TP5
import GUI
import os
import json


def Generer_Grille(taille = 10):
    grille = []
    for i in range(taille):
        grille.append([])
        for j in range(taille):
            grille[i].append(1)
    return grille


def gen1bat(nom_bateau, taille):
    bateau = {}
    bateau["nom"] = nom_bateau
    bateau["taille"] = taille
    bateau["touchés"] = 0

    return bateau


def Generer_Bateaux():
    specifications = {"porte-avion" : 5, "croiseur" : 4, "contre-torpilleur 1" : 3, "contre-torpilleur 2" : 3, "sous-marin" : 2}
    liste_bateaux = []
    for name in specifications.keys():
        liste_bateaux.append(gen1bat(name, specifications[name]))
    
    return liste_bateaux
        

def Generer_Joueur(humain, nombre_d_adversaires=1):
    '''
        Génère les informations de jeu d'un joueur
        Entrée : 
            - humain : booléen qui spécifie si l'on crée le joueur humain ou l'ordi
            - nombre_d_adversaires : nombre d'adversaires (grilles de tir)
        Sortie : un dictionnaire avec grille de placement, bateaux, grilles de tir pour chaque adversaire, score
    '''
    batx = Generer_Bateaux()
    # Create list of shooting grids, one for each opponent
    grilles_tirs = [Generer_Grille(10) for _ in range(nombre_d_adversaires)]
    return {
        "grille": TP5.Placer_Bateaux(Generer_Grille(10), batx, humain), 
        "bateaux" : batx, 
        "tirs": grilles_tirs, 
        "score": 0
    }


def Sauvegarde(dico_joueur, dico_ordi):
    chemin = os.getcwd()
    if not os.path.exists(chemin + "/data"):
        os.mkdir(chemin + "/data")
    os.chdir(chemin + "/data")
    data = [dico_joueur, dico_ordi]
    fichier = open("sauvegarde.json", "w")
    json.dump(data, fichier)
    fichier.close()


def Chargement():
    chemin = os.getcwd()
    if os.path.exists(chemin + "/data/sauvegarde.json"):
        os.chdir(chemin + "/data")
        fichier = open("sauvegarde.json", "r")
        data = json.load(fichier)
        fichier.close()
        GUI.Afficher_msg("Une ancienne partie à été téléchargée")
    
    elif not os.path.exists(chemin + "/data/sauvegarde.json"): 
        dico_joueur = Generer_Joueur(True)
        dico_ordi = Generer_Joueur(False)
        data = [dico_joueur, dico_ordi]

    return data
