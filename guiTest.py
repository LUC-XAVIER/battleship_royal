# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 13:09:15 2026

@author: FONING
"""

import PySimpleGUI as sg


# Déclaration du 'layout' (mise en page de la fenêtre)
layout=[[sg.Button('Cliquez ici')]]

# Création de la fenêtre
window=sg.Window('Ma première fenêtre', layout=layout)

# Boucle de gestion des évènements
while True:
    event, values = window.read() # lecture du dernier évènement
    if event == sg.WIN_CLOSED: # si l'évènement est "quitter", on casse la boucle
        break
window.close() # Destruction de la fenêtre