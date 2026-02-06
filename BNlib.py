#from corrige import *

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

def Coords2Nums(pos):
    '''
        Entrée : une chaine représentant des coordonnées : exemple "B6"
        Sortie : deux entiers représentants respectivement les numéros
        de ligne et colonne : 1, 5 (indicé à partir de 0)
    '''
    return ord(pos[0])-65, int(pos[1:])-1
