import os
import sys
import json
from random import randint 
sys.stdout.reconfigure(encoding='utf-8')



#TP 1

def Afficher_msg(msg):
    '''
    Affiche un message (chaine donnée en entrée) à l'utilisateur.
    '''
    print(msg)


def Afficher_Grille(grille = []):
    print()
    rows = [chr(65 + i) for i in range(len(grille))]
    for i in range(len(grille)):
        print("   ", end="")
        if i < len(grille) - 1:
            print("  " + chr(49 + i), end="")
        elif len(grille) == 10:
            print("   " + "10")
        else:
            print("   " + chr(49 + i))
    for j in range(len(grille)):
        print("   +" + len(grille) * "-----+")
        print(rows[j] + "  |", end="")
        for i in range(len(grille[j])):
            state = " "
            if grille[j][i] == 1:
                state = " "
            elif grille[j][i] == -1:
                state = chr(0x2591)
            elif grille[j][i] in [2, 3, 4, 5, 6]:
                state = chr(0x2588)
            elif grille[j][i] in [-2, -3, -4, -5, -6]:
                state = chr(0x2573)
            else:
                state = "@"

            if i < len(grille[j]) - 1:
                print("  " + state + "  |", end="")
            else:
                print("  " + state + "  |")

    print("   +" + len(grille) * "-----+")


def Generer_Grille(taille = 10):
    grille = []
    for i in range(taille):
        grille.append([])
        for j in range(taille):
            grille[i].append(1)
    return grille




#TP 2


def Saisie_Coords():
    Afficher_msg("C'est à vous!\n")
    saisie = input("Entrez les coordonnées (ex: A5) (Si vous souhaitez sauvegarder la partie, appuyer la touche \"q\") : ")
    if saisie.upper() == "Q":
        return "q"
    while True:
        saisie = saisie.upper()
        if len(saisie) == 2 or len(saisie) == 3:
            if saisie[0] in "ABCDEFGHIJ":
                if saisie[1:].isdigit() and int(saisie[1:]) >= 1 and int(saisie[1:]) <= 10:
                    return saisie
        Afficher_msg("Coordonnées invalides. Veuillez réessayer.")
        saisie = input("Entrez les coordonnées (ex: A5) : ")    


def Coords2Nums(pos):
    '''
        Entrée : une chaine représentant des coordonnées : exemple "B6"
        Sortie : deux entiers représentants respectivement les numéros
        de ligne et colonne : 1, 5 (indicé à partir de 0)
    '''
    return ord(pos[0])-65, int(pos[1:])-1


def Tir(grille_adv, grille_etats_connu, pos, bateaux_adv):
    coords = Coords2Nums(pos)
    if grille_adv[coords[0]][coords[1]] > 0:

        grille_etats_connu[coords[0]][coords[1]] = -grille_adv[coords[0]][coords[1]]
        grille_adv[coords[0]][coords[1]] = -grille_adv[coords[0]][coords[1]]

        if grille_adv[coords[0]][coords[1]] == -2:
            bateaux_adv[4]["touchés"] += 1
            if bateaux_adv[4]["touchés"] == bateaux_adv[4]["taille"]:
                return 2
            else:
                return 1
        elif grille_adv[coords[0]][coords[1]] == -3:
            bateaux_adv[2]["touchés"] += 1
            if bateaux_adv[2]["touchés"] == bateaux_adv[2]["taille"]:
                return 2
            else:
                return 1
        elif grille_adv[coords[0]][coords[1]] == -4:
            bateaux_adv[3]["touchés"] += 1
            if bateaux_adv[3]["touchés"] == bateaux_adv[3]["taille"]:
                return 2
            else:
                return 1
        elif grille_adv[coords[0]][coords[1]] == -5:
            bateaux_adv[1]["touchés"] += 1
            if bateaux_adv[1]["touchés"] == bateaux_adv[1]["taille"]:
                return 2
            else:
                return 1
        elif grille_adv[coords[0]][coords[1]] == -6:
            bateaux_adv[0]["touchés"] += 1
            if bateaux_adv[0]["touchés"] == bateaux_adv[0]["taille"]:
                return 2
            else:
                return 1
        else:
            return 0
        
    else:
        return -1
            

def Ordi_Coords(grille):
    '''
        Obtention des coordonnées de tir choisies par l'ordinateur.
        Entrée : la grille à analyser pour faire le choix (grille d'état du joueur)
        Sortie : coordonnées, genre "B6"
    '''
    return chr(randint(65, 74)) + str(randint(1, 10))


def Gagne(bateaux):
    '''
        Détermine si tous les bateaux ont été coulés
        Entrée : une liste de bateaux
        Sortie : un booléen, True s'ils ont tous été coulés, False sinon
    '''
    for bateau in bateaux:
        if bateau["taille"] != bateau["touchés"]: # bateau non coulé ? (taille différent de nb fois touché)
            return False
    return True


def Boucle_Jeu():
    data, exists = Chargement()
    if not exists:
        Placer_Bateaux_Auto(data[0]["grille"], "joueur")   # no function for boat placement by player yet
        Placer_Bateaux_Auto(data[1]["grille"], "ordi")

    while not Gagne(data[0]["bateaux"]):
        Afficher_Grille(data[0]["tirs"])
        pos = Saisie_Coords()

        if pos == "Q" or pos == "q":
            Sauvegarde(data[0], data[1])
            return -1

        Tir(data[1]["grille"], data[0]["tirs"], pos, data[1]["bateaux"])
        Afficher_Grille(data[0]["tirs"])

        if Gagne(data[1]["bateaux"]):
            return 1
        
        pos_ordi = Ordi_Coords(data[1]["tirs"])
        Tir(data[0]["grille"], data[1]["tirs"], pos_ordi, data[0]["bateaux"])
        Afficher_Grille(data[1]["tirs"])
    
    return 0



#TP 3

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
        

def Generer_Joueur(): 
    données_Initiales = {}
    données_Initiales["grille"] = Generer_Grille(10)    
    données_Initiales["tirs"] = Generer_Grille(10)    
    données_Initiales["bateaux"] = Generer_Bateaux()

    return données_Initiales


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
        Afficher_msg("Une ancienne partie à été téléchargée")
        exists = True
    
    else: 
        exists = False
        dico_joueur = Generer_Joueur()
        dico_ordi = Generer_Joueur()
        data = [dico_joueur, dico_ordi]

    return data, exists


def Placer_Bateaux_Auto(grille, joueur):
    if joueur == "ordi":
        grille[:-1] = [
            [1, 1, 1, 5, 5, 5, 5, 1, 1, 1], [3, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
            [3, 1, 1, 1, 1, 1, 1, 1, 1, 1], [3, 1, 1, 1, 1, 1, 2, 1, 1, 1], 
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
            [1, 6, 6, 6, 6, 6, 1, 4, 1, 1], [1, 1, 1, 1, 1, 1, 1, 4, 1, 1], 
            [1, 1, 1, 1, 1, 1, 1, 4, 1, 1]
        ]
    elif joueur == "joueur":
        grille[:-1] = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 6, 1, 1, 1, 1, 1, 1, 1, 1], 
            [1, 6, 1, 5, 5, 5, 5, 1, 1, 1], [1, 6, 1, 1, 1, 1, 1, 1, 1, 1], 
            [1, 6, 1, 1, 1, 1, 1, 1, 1, 1], [1, 6, 1, 1, 1, 2, 2, 1, 1, 1], 
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 4], [1, 1, 1, 1, 3, 3, 3, 1, 1, 4], 
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        ]

    return grille



#testing
# grille_etats_connu = Generer_Grille(10)
# Afficher_Grille(grille_etats_connu)
# print()
# pos = Saisie_Coords()
# verdict = Tir(grille_ordi, grille_etats_connu, pos, bateaux_ordi)
# print(verdict)

Verdict = Boucle_Jeu()
if Verdict == 0:
    print("Ordinateur Vainqueur")
elif Verdict == 1:
    print("joueur vainqueur")
else:
    print("Votre partie à bien été sauvegardé")