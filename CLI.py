#from corrige import *
import Partie


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


def Saisie_Car(msg, choix):
    '''
        Restreint la saisie d'un caractère parmis ceux proposé par "choix"
        Le renvoie en majuscule quand ok
    '''
    Afficher_msg(msg + " " + choix)
    saisie = input().upper()
    while len(saisie) != 1 and saisie not in choix:
        Afficher_msg("Erreur, " + msg + " " + choix)
        saisie = input().upper()
    return saisie


if __name__ == "__main__":
    grille = Partie.Generer_Grille(10)
    Afficher_Grille(grille)