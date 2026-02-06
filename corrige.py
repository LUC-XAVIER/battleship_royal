
def Coords2Nums(pos):
    '''
    Entr ́ee : une chaine repr ́esentant des coordonn ́ees : exemple "B6"
    Sortie : deux entiers repr ́esentants respectivement les num ́eros
    de ligne et colonne : 1, 5 (indic ́e `a partir de 0)
    '''
    return ord(pos[0])-65, int(pos[1:])-1

def Gagne(bateaux):
    """
    D ́etermine si tous les bateaux ont  ́et ́e coul ́es
    Entr ́ee : dictionnaire
    Sortie : un bool ́een, True s'ils ont tous  ́et ́e coul ́es, False sinon
    """
    for bateau in bateaux:
        #if bateau[1]!=bateau[2]: # bateau non coul ́e ? (taille diff ́erent de nb fois touch ́e)
        if bateau['taille']!=bateau['touchés']:
            return False
    return True
    
def Saisie_Car(msg, choix):
    '''
    Restreint la saisie d'un caractère parmis ceux proposé par "choix"
    Le renvoie en majuscule quand ok
    '''
    Afficher_msg(msg+" "+choix)
    saisie = input().upper()
    while len(saisie)!=1 and saisie not in choix:
        Afficher_msg("Erreur, "+msg+" "+choix)
        saisie = input().upper()
    return saisie

def Afficher_Grille(grille):
   

    s = "   │"
    for i in range(len(grille)):
        #s += str(i+1)+" " 
        s += "{:^3}│".format(i+1)
    print(s)
    
    line = len(grille)*(3*"─"+"┼") + 3*"─"+"┤"
 
    
    nligne = 65 # "A", en-tête 1° ligne
    for ligne in grille:
        print(line)
        #s = chr(nligne)+" "
        s= "{:^3}│".format(chr(nligne))
        for case in ligne:
            if case==1:
                #s += " " #eau
                s += "{:3}│".format(3*" ")
            elif case == -1:
                #s += "\u2591" # raté (eau)
                s += "{:3}│".format(3*"\u2591")
            elif case >= 2 and case <= 6:
                #s += "\u2588" # bateau
                s += "{:3}│".format(3*"\u2588")
            elif case >= -6 and case <= -2:
                #s += "\u2573" # touchés (bateau)
                s += "{:3}│".format(3*"\u2573")
            else:
                #s += "@" # ne doit jamais s'afficher si l'entrée est OK
                s += "{:3}│".format(3*"@")
            #s += s[-1] # doublage du dernier caractère
        print(s)
        
        nligne += 1
    
    lastline = len(grille)*(3*"─"+"┴") + 3*"─"+"┘"
    print(lastline)

def Afficher_msg(msg):
    print(msg)


def Tir(grille_ordi,grille2jeu_joueur,tir,bateaux_joueur):
    """
    retourne  
    0 pour rate, 
    1 pour touche
    2 pour coule, 
    et -1 pour touchés mais deja  touche a cet endroit
    
    2 (porte-avion) à 6 (sous-marin)

    Parameters
    ----------
    grille_ordi : TYPE
        DESCRIPTION.
    grille2jeu_joueur : TYPE
        DESCRIPTION.
    tir : TYPE
        DESCRIPTION.
    bateaux_joueur : dict
        DESCRIPTION.

    Returns
    -------
    res : TYPE
        DESCRIPTION.

    """
    nline,ncol = Coords2Nums(tir)
    
    valcase = grille_ordi[nline][ncol]
    #Changement état grille ordi
    if valcase > 0: 
        grille_ordi[nline][ncol] = -valcase
    
    #case de la grille d'état prend même valeur que grille de placement
    grille2jeu_joueur[nline][ncol]  = grille_ordi[nline][ncol]
    
    
    if abs(valcase) == 1: 
        res = 0
    elif valcase < 0: #déjà touchés
        res = -1
    else:
        #incrémenter le bon bateau
        #bateaux_joueur[abs(valcase)-2][2] += 1
        bateaux_joueur[abs(valcase)-2]["touchés"] += 1
        #if bateaux_joueur[abs(valcase)-2][2] == bateaux_joueur[abs(valcase)-2][1]:
        if bateaux_joueur[abs(valcase)-2]["touchés"] == bateaux_joueur[abs(valcase)-2]["taille"]:
            res = 2 # coulé
        else:
            res = 1 #touche
        
    
    return res



        
def Generer_Grille(n):
    #eau valeur 1
    grille = [[1 for i in range(n)] for j in range(n)]
    return grille

def gen1bat(nom,taille):
    dicbateau ={"nom":nom,"taille":taille,"touchés":0}
    return dicbateau

def Generer_Bateaux():
    tab = [0 for i in range(5)]
    tab[0] = gen1bat("porte-avion",5)
    tab[1] = gen1bat("croiseur",4)
    tab[2] = gen1bat("contre-torpilleur 1",3)
    tab[3] = gen1bat("contre-torpilleur 2",3)
    tab[4] = gen1bat("sous-marin",2)
    return tab
 



def Saisie_Coords():
    Afficher_msg("Entrer vos coordonnees:")
    saisie = input()
    while True:
        saisie = saisie.upper()
        if len(saisie) >=2 and len(saisie) <=3:
            if saisie[0] in 'ABCDEFGHIJ':
                if saisie[1:].isdigit() and int(saisie[1:])>=1 and int(saisie[1:])<=10:
                    return saisie
        Afficher_msg("Entrer vos coordonnees:")
        saisie = input()