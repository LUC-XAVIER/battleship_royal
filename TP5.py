import corrige
import CLI
import BNlib
import Partie
from random import randint


# ---------------------
# Placement des bateaux
# ---------------------

def Placer_Bateau(grille, num, position, direction, taille):
    '''
        Place un bateau sur une grille.
        num : index du bateau (dans la liste des bateaux)
        position : coords "B6"
        direction : un caractère parmi "NSEO"
        taille : taille du bateau
    '''
    yo, xo = corrige.Coords2Nums(position)
    yd, xd = yo, xo
    horiz = 0
    sens = +1
    if direction=='N':
        yd -= taille
        sens = -1
    elif direction=='E':
        xd += taille
        horiz = 1
    elif direction=='S':
        yd += taille
    else: # Ouest
        xd -= taille
        horiz = 1
        sens = -1
    vert = 1-horiz
    for i in range(taille):
        grille[yo+(i*sens)*vert][xo+(i*sens)*horiz] = num+2
    return grille

def Verif_Placement(grille, position, taille):
    '''
    Vérifie les orientations possibles à partir d'une case, dans les quatres directions.
    Sachant qu'un bateau ne doit jamais en toucher un autre (par les coins également)
    Renvoie une chaine avec les directions possibles parmi NSOE (chaine vide si aucune possible)
    '''
    yo, xo = corrige.Coords2Nums(position) # origine
    if grille[yo][xo] != 1:
        return ""
    res = ""
    #  0     N
    # 1 3   O E
    #  2     S
    dirs = "NOSE"
    for orient in range(4): # 4 points cardinaux
        horiz = orient%2 # Orientation H ou V (0 ou 1)
        vert = 1-horiz
        sens = (orient//2)*2-1 # Sens positif ou négatif (sur l'axe de l'orientation)
        xd = xo+horiz*sens*(taille-1) # destination (= bout du bateau)
        yd = yo+vert*sens*(taille-1)
        if xd<0 or xd>=len(grille) or yd<0 or yd>=len(grille): # dest hors grille
            continue
        xmin = min(xo, xd)-1 # Coins du "cadre" formé autour du bateau
        xmax = max(xo, xd)+1
        ymin = min(yo, yd)-1
        ymax = max(yo, yd)+1
        xmin = max(xmin, 0) # On tronque les zones hors grille
        xmax = min(xmax, len(grille)-1)
        ymin = max(ymin, 0)
        ymax = min(ymax, len(grille)-1)
        stop = False
        for y in range(ymin, ymax+1): # Vérification de chaque case de ce cadre
            for x in range(xmin, xmax+1):
                if grille[y][x]!=1:
                    stop = True
                    break
            if stop:
                break
        if stop:
            continue
        res += dirs[orient] # Ajout de l'orientation dans les possibilités
    return res


def Placer_Bateaux(grille, bateaux, humain):
    '''
    Positionne l'ensemble des bateaux sur une grille (de façon auto si ce n'est pas l'humain)
    '''
    if humain:
        corrige.Afficher_Grille(grille)
    for num in range(len(bateaux)):
        if humain:
            CLI.Afficher_msg("Placement de : "+bateaux[num]['nom'])
        directions = ""
        while len(directions)==0: # Tant qu'il n'est pas possible de placer un bateau sur la case choisie :
            coords = CLI.Saisie_Coords() if humain else chr(randint(65, 74))+str(randint(1, 10))
            if coords.upper() == 'Q':
                quit()
            directions = Verif_Placement(grille, coords, bateaux[num]['taille'])
            if humain and len(directions)==0:
                CLI.Afficher_msg("Impossible de placer le "+bateaux[num]['nom']+" ici.")
        orientation = CLI.Saisie_Car("Saisir une orientation", directions) if humain else directions[randint(1, len(directions))-1]
        grille = Placer_Bateau(grille, num, coords, orientation, bateaux[num]['taille'])
        if humain:
            corrige.Afficher_Grille(grille)
    return grille

# --------------------------
# Stratégie de tir de l'ordi
# --------------------------

def Case_pertinente(grille, x, y):
    '''
    Détermine s'il est pertinent de tirer sur cette case, en regardant tout autour.
     grille: la grille des tirs déjà tentés
     x, y : les indices de la case à tester dans la liste 2D

     ? ? ?
     ? X ?
     ? ? ?
    '''
    n = len(grille)
    # Bateau à proximité, si oui ce n'est pas pertinent ?
    for y2 in range(y-1,y+2):
        if (y2==-1) or (y2==n): # hors grille
            continue
        for x2 in range(x-1,x+2):
            if (x2==-1) or (x2==n): # hors grille
                continue
            if abs(grille[y2][x2]) >= 2: # bateau à proximité immédiate
                return False

    # Pas de bateau autour, ai-je déjà testé deux cases autour (ortogonalement) ?
    # (dans ce cas inutile de tester celle-ci)
    #   -
    #   X   ou   - X -    ?
    #   -

    # Verticalement ?
    adj = 0
    for y2 in range(y-1,y+2):
        if (y2==y) or (y2==-1) or (y2==n): # cette case ou hors grille, on ignore
            continue
        if grille[y2][x]==-1:
            adj += 1
    if adj==2:
        return False
    # Horizontalement ?
    adj = 0
    for x2 in range(x-1,x+2):
        if (x2==x) or (x2==-1) or (x2==n): # cette case ou hors grille, on ignore
            continue
        if grille[y][x2]==-1:
            adj += 1
    return not (adj==2)

def Case_Possible(grille, x, y):
    '''
    Détermine si c'est une case existante, et si oui si on a pas déjà raté
    '''
    n = len(grille)
    if (x==-1) or (y==-1) or (x==n) or (y==n): # hors grille
        return False
    if grille[y][x]==-1: # On avait déjà testé cette case
        return False
    return True


def Ordi_Coords(grille, bateaux):
    '''
        Recherche un bateau déjà touché mais non coulé, et tente de le couler.
        Si aucun bateau candidat, tir aléatoire en évitant d'etre adjacent à un bateau déjà trouvé.
    '''
    n = len(grille)
    ncase = 0
    cases_candidates = []
    while (ncase < n**2): # Recherche d'un bateau partiellement touché, linéarisation de la grille
        y = ncase//n
        x = ncase%n
        vcase = grille[y][x]
        if (vcase <= -2) and (bateaux[abs(vcase)-2]['touchés'] < bateaux[abs(vcase)-2]['taille']):
            # Partiel trouvé, recherche de son orientation
            for direction in range(4): # 4 orientations possibles
                x2 = x
                y2 = y
                vert = direction%2
                horiz = 1-vert
                sens = (direction//2)*2-1 #positif ou négatif
                x2 += horiz*sens
                y2 += vert*sens
                if not Case_Possible(grille, x2, y2):
                    continue
                if grille[y2][x2] < -1: # Orientation trouvée !
                    while True: # recherche du sens
                        x3, y3 = x2, y2
                        while True: # On va jusqu'au bout du bateau
                            x3 += horiz*sens
                            y3 += vert*sens
                            if not Case_Possible(grille, x3, y3):
                                break
                            if grille[y3][x3]==1: # On veux tirer ici !
                                return chr(y3+65)+str(x3+1)
                        sens *= -1 # On reteste dans l'autre sens
                if grille[y2][x2]==1: # sens non trouvée (un seul tir sur ce bateau), mais c'est intéressant de tenter ici
                    cases_candidates += [(y2,x2)]
                    
        ncase += 1         
                    
    # Si on arrive ici, c'est qu'on a un bateau partiel dont on ne connait pas le sens
    if len(cases_candidates)>0: # J'ai des cases à intéressantes à tester autour
        y, x = cases_candidates[randint(1, len(cases_candidates)-1)]
        return chr(y+65)+str(x+1)
    # Si on arrive ici, c'est qu'aucun bateau partiel n'a été trouvé
    perti = False
    while not perti:
        y = randint(1, n)-1
        x = (randint(1, n//2+(n%2))-1)*2+(y%2) # 1 case sur 2, en quinconce
        if grille[y][x] != 1: # case déjà tirée
            continue
        perti = Case_pertinente(grille, x, y)
    return chr(y+65)+str(x+1)


# Permet de tester le module indépendamment du programme principal
# Sentez-vous libre d'apporter des modifications si cela peut vous aider à trouver les bugs.
if (__name__ == "__main__"):
    # Test du placement des bateaux par l'ordinateur
    #corrige.Afficher_Grille(Placer_Bateaux(Partie.Generer_Grille(10), Partie.Generer_Bateaux(), False))
    #input("Tapez sur Entrée pour continuer.")

    # Test du placement des bateaux par le joueur humain
    corrige.Afficher_Grille(Placer_Bateaux(Partie.Generer_Grille(10), Partie.Generer_Bateaux(), False))
    corrige.Afficher_Grille(Placer_Bateaux(Partie.Generer_Grille(10), Partie.Generer_Bateaux(), True))
    # Test de la stratégie de tir de l'ordi
    # Un seul joueur qui s'auto cible
    #joueur = Partie.Generer_Joueur(False)
    # Pour tester, il est plus simple d'avoir une grille non aléatoire
    #joueur['grille'] = grille_joueur = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 2, 1, 1, 1, 1, 1, 1, 1, 1], [1, 2, 1, 5, 5, 5, 1, 1, 1, 1], [1, 2, 1, 1, 1, 1, 1, 1, 1, 1], [1, 2, 1, 1, 1, 1, 1, 1, 1, 1], [1, 2, 1, 1, 1, 6, 6, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 4], [1, 1, 1, 1, 3, 3, 3, 3, 1, 4], [1, 1, 1, 1, 1, 1, 1, 1, 1, 4], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    #while not BNlib.Gagne(joueur['bateaux']):
        #tir = Ordi_Coords(joueur['tirs'], joueur['bateaux'])
        #print(tir)
        #corrige.Tir(joueur['grille'], joueur['tirs'], tir, joueur['bateaux'])
        #corrige.Afficher_Grille(joueur['tirs'])
        #input("Tapez sur Entrée pour continuer.") # Pour faire une pause entre les tirs
