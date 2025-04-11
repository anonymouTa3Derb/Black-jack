import random
import sys

# =========================================
# Variables globales
# =========================================

# Indique si la partie est en cours (True) ou terminée (False)
en_jeu = False

# Montant initial de jetons (buy-in)
solde_jetons = 100
print("Votre montant de départ est :", solde_jetons)

# Mise par défaut
mise = 1

# Texte de relance
message_relance = "Appuyez sur (d) pour redistribuer ou (q) pour quitter."

# Enseignes : Cœurs (C), Carreaux (D), Piques (P), Trèfles (T)
enseigne_possibles = ('C', 'D', 'P', 'T')

# Valeurs possibles des cartes
valeurs_possibles = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')

# Dictionnaire des valeurs en points (l'As sera géré plus finement dans la classe Main)
dico_valeurs = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10
}

# =========================================
# Comptage de cartes (Hi-Lo)
# =========================================
running_count = 0  # Compteur de cartes global

def compter_carte(valeur_carte):
    """
    Met à jour le compteur (running_count) selon le système Hi-Lo.
    Valeur_carte est la valeur type 'A', '2', ..., '10', 'J', 'Q', 'K'.
    """
    global running_count

    if valeur_carte in ('2', '3', '4', '5', '6'):
        running_count += 1
    elif valeur_carte in ('10', 'J', 'Q', 'K', 'A'):
        running_count -= 1
    # Cartes 7, 8, 9 ne changent pas le count (0)

# Fonction pour donner un conseil (très simplifié) en fonction du count
def conseil_count():
    """
    Retourne un conseil basé sur la valeur du running_count.
    Ceci est très basique, juste pour l’exemple.
    """
    global running_count
    if running_count > 2:
        return f"Le compte est positif (+{running_count}) : Le jeu est en votre faveur, vous pouvez miser plus !"
    elif running_count < -2:
        return f"Le compte est négatif ({running_count}) : Attention, le croupier est avantagé. Baissez la mise ou soyez prudent."
    else:
        return f"Le compte est proche de l’équilibre ({running_count}). Jouez normalement."

# =========================================
# Classe Carte
# =========================================

class Carte:
    def __init__(self, enseigne, valeur):
        self.enseigne = enseigne  # 'C', 'D', 'P', 'T'
        self.valeur = valeur      # 'A', '2', '3', ..., 'J', 'Q', 'K'

    def __str__(self):
        return f"{self.enseigne}{self.valeur}"

    def afficher_carte(self):
        print(str(self))

# =========================================
# Classe Main (Hand)
# =========================================

class Main:
    """
    Représente la main d'un joueur ou du croupier.
    L’As peut valoir 1 ou 11 (géré dans la méthode calculer_valeur).
    """

    def __init__(self):
        self.cartes = []
        self.total = 0
        self.possede_as = False

    def __str__(self):
        composition = " ".join(str(carte) for carte in self.cartes)
        return f"La main contient : {composition}"

    def ajouter_carte(self, carte):
        """
        Ajoute une carte à la main et met à jour la valeur ET
        met à jour le compteur Hi-Lo.
        """
        self.cartes.append(carte)
        # Mise à jour de la valeur
        if carte.valeur == 'A':
            self.possede_as = True
        self.total += dico_valeurs[carte.valeur]
        # Mise à jour du count
        compter_carte(carte.valeur)

    def calculer_valeur(self):
        """
        Calcule la valeur de la main en considérant l’As comme 1 ou 11.
        """
        if self.possede_as and self.total <= 11:
            return self.total + 10
        else:
            return self.total

    def afficher_main(self, cacher_premiere=False):
        if cacher_premiere and en_jeu:
            print("Carte cachée")
            for carte in self.cartes[1:]:
                carte.afficher_carte()
        else:
            for carte in self.cartes:
                carte.afficher_carte()

# =========================================
# Classe Paquet (Deck)
# =========================================

class Paquet:
    def __init__(self):
        self.paquet = []
        for enseigne in enseigne_possibles:
            for valeur in valeurs_possibles:
                self.paquet.append(Carte(enseigne, valeur))

    def melanger(self):
        random.shuffle(self.paquet)

    def distribuer(self):
        return self.paquet.pop()

    def __str__(self):
        return " ".join(str(carte) for carte in self.paquet)

# =========================================
# Fonctions du jeu
# =========================================

def demander_mise():
    global mise, solde_jetons

    mise = 0
    print("\nQuel montant souhaitez-vous miser ? (Entrez un entier) :")

    while True:
        try:
            saisie = input(">> ")
            montant = int(saisie)
            if 1 <= montant <= solde_jetons:
                mise = montant
                break
            else:
                print(f"Mise invalide. Vous avez {solde_jetons} jetons disponibles.")
        except ValueError:
            print("Veuillez entrer un nombre entier.")

def distribuer_cartes():
    """
    Distribue les cartes pour commencer un nouveau tour.
    """
    global en_jeu, paquet, main_joueur, main_croupier
    global solde_jetons, mise, resultat
    global running_count  # On veut afficher l'état du compteur

    # Avant de créer un nouveau paquet, on peut décider
    # si l’on veut remettre le count à 0 quand on recharge un deck :
    # Pour simplifier, on va considérer qu’on reprend un deck neuf à chaque manche,
    # donc on réinitialise le running_count. À vous d’adapter selon vos règles.
    running_count = 0

    paquet = Paquet()
    paquet.melanger()

    demander_mise()

    main_joueur = Main()
    main_croupier = Main()

    # Distribue deux cartes au joueur
    main_joueur.ajouter_carte(paquet.distribuer())
    main_joueur.ajouter_carte(paquet.distribuer())

    # Distribue deux cartes au croupier
    main_croupier.ajouter_carte(paquet.distribuer())
    main_croupier.ajouter_carte(paquet.distribuer())

    resultat = "Voulez-vous tirer (h) ou rester (s) ?"
    en_jeu = True

    etat_partie()

def tirer_carte():
    global en_jeu, solde_jetons, paquet, main_joueur, resultat, mise

    if en_jeu:
        if main_joueur.calculer_valeur() <= 21:
            main_joueur.ajouter_carte(paquet.distribuer())

        if main_joueur.calculer_valeur() > 21:
            print(f"Votre main est de {main_joueur.calculer_valeur()}. Vous brûlez !")
            solde_jetons -= mise
            resultat = f"Vous avez perdu cette manche. {message_relance}"
            en_jeu = False
        else:
            resultat = "Voulez-vous tirer (h) ou rester (s) ?"
    else:
        resultat = f"Désolé, vous ne pouvez plus tirer de carte. {message_relance}"

    etat_partie()

def rester():
    global en_jeu, solde_jetons, paquet, main_croupier, main_joueur, resultat, mise

    if not en_jeu:
        resultat = "La manche est déjà terminée."
        etat_partie()
        return

    # Le croupier tire tant qu'il a moins de 17
    while main_croupier.calculer_valeur() < 17:
        main_croupier.ajouter_carte(paquet.distribuer())

    total_croupier = main_croupier.calculer_valeur()
    total_joueur = main_joueur.calculer_valeur()

    if total_croupier > 21:
        resultat = f"Le croupier dépasse 21 ({total_croupier}). Vous gagnez ! {message_relance}"
        solde_jetons += mise
    elif total_croupier < total_joueur:
        resultat = f"Vous avez {total_joueur} contre {total_croupier} pour le croupier. Vous gagnez ! {message_relance}"
        solde_jetons += mise
    elif total_croupier == total_joueur:
        resultat = f"Égalité ! (push) {message_relance}"
    else:
        resultat = f"Le croupier a {total_croupier} et vous {total_joueur}. Le croupier gagne. {message_relance}"
        solde_jetons -= mise

    en_jeu = False
    etat_partie()

def quitter_jeu():
    print("Merci d'avoir joué !")
    sys.exit(0)

def etat_partie():
    """
    Affiche l'état actuel de la partie (mains, compte) et
    donne un conseil basé sur le compte.
    """
    print("\n==== État de la partie ====")

    # Afficher la main du joueur
    print("Main du joueur :")
    main_joueur.afficher_main(cacher_premiere=False)
    print(f"Total joueur = {main_joueur.calculer_valeur()}")

    # Afficher la main du croupier
    print("\nMain du croupier :")
    main_croupier.afficher_main(cacher_premiere=en_jeu)
    if not en_jeu:
        # Partie terminée, on affiche le total croupier
        print(f"Total croupier = {main_croupier.calculer_valeur()}")

    # Afficher le solde
    print(f"\nVous avez maintenant {solde_jetons} jetons.")

    # Afficher le running_count et un conseil
    print(f"Running count (Hi-Lo) = {running_count}")
    print("Conseil basé sur le compte :", conseil_count())

    # Afficher le résultat ou la question en cours
    print("\n" + str(resultat))

    # Lire la commande
    commande_joueur()

def commande_joueur():
    """
    Lit la commande du joueur et exécute l’action correspondante.
    """
    choix = input(">> ").lower()

    if choix == 'h':
        tirer_carte()
    elif choix == 's':
        rester()
    elif choix == 'd':
        distribuer_cartes()
    elif choix == 'q':
        quitter_jeu()
    else:
        print("Choix invalide. Veuillez entrer : (h) tirer, (s) rester, (d) distribuer, (q) quitter.")
        commande_joueur()

def intro():
    regles = """
Bienvenue au BlackJack (avec comptage de cartes Hi-Lo) !
Le but est de vous approcher le plus possible de 21 sans dépasser.
Le croupier tire jusqu’à avoir au moins 17.
Les As valent 1 ou 11, selon ce qui vous avantage.
Comptage Hi-Lo :
  - 2 à 6 = +1
  - 7 à 9 =  0
  - 10, J, Q, K, A = -1
Plus le compte est élevé, plus le deck vous avantage.
Appuyez sur (h) pour tirer, (s) pour rester, (d) pour distribuer, ou (q) pour quitter.
"""
    print(regles)

# =========================================
# Lancement du jeu
# =========================================

if __name__ == "__main__":
    intro()
    distribuer_cartes()
