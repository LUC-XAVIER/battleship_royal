import random

import BNlib
import Partie
import corrige
import TP5
import GUI
import time
import pickle
import struct
import threading
import socket
from server import log
from shared import *

host = "127.0.0.1"
port = 1234
sckt = None

def Tir(grille_adv, grille_etats_connu, pos, bateaux_adv):
    coords = BNlib.Coords2Nums(pos)
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
    


def Boucle_Jeu():
    data = Partie.Chargement()

    while not BNlib.Gagne(data[0]["bateaux"]):
        tir = tir_ordi = 1
        while (tir == 1 or tir == 2):    #rejouer si jamais vous touchez ou coulez un bateau

            GUI.Afficher_Grille(data[0]["tirs"])
            pos = GUI.Saisie_Coords()
    
            if pos == "Q" or pos == "q":
                Partie.Sauvegarde(data[0], data[1])
                return -1
            
            tir = corrige.Tir(data[1]["grille"], data[0]["tirs"], pos, data[1]["bateaux"])
            #GUI.Afficher_Grille(data[0]["tirs"])
            
            if BNlib.Gagne(data[1]["bateaux"]):
                GUI.Afficher_Grille(data[0]["tirs"])
                return 1
            
        GUI.Afficher_Grille(data[0]["tirs"])

        if BNlib.Gagne(data[1]["bateaux"]):
            return 1
        
        while (tir_ordi == 1 or tir_ordi == 2):
            GUI.Afficher_msg("computer plays...")
            
            if BNlib.Gagne(data[0]["bateaux"]):
                GUI.Afficher_Grille(data[1]["tirs"])
                return 0
            
            pos_ordi = TP5.Ordi_Coords(data[1]["tirs"], data[0]["bateaux"])
            tir_ordi = corrige.Tir(data[0]["grille"], data[1]["tirs"], pos_ordi, data[0]["bateaux"])
            GUI.Afficher_Grille(data[1]["tirs"])     

    return 0

def run_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        s.connect((host, port))
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        s.settimeout(10)
        sckt = s
        log.info('connected ', sckt)

        send(s, PlayerData("Alex"))
        data = receive(s)

        client_id = random.randint(0, 20)
        while True:
            send(s, data)
            log.debug('Sending ', data)
            receive(s)
            log.debug('Received ', data)
            time.sleep(1)

if __name__ == "__main__":
    
    GUIent_thread = threading.Thread(target = run_listener)
    GUIent_thread.start()
    
    verdict = Boucle_Jeu()
    if verdict == 0:
        print("Computer wins!! You loser.")
    elif verdict == 1:
        print("Not bad bro!! You win.")
    else:
        print("Your game's been backed up...")