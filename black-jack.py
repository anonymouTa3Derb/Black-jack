import tkinter as tk
import random
import sys

# ======================================================
#                 Paramètres et Constantes
# ======================================================

# Enseignes (Coeur, Carreau, Pique, Trèfle) -- arbitraire 'C', 'D', 'P', 'T'
ENSEIGNES = ('C', 'D', 'P', 'T')
# Valeurs
VALEURS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
# Valeurs de points (l'As sera géré plus finement)
DICO_VALEURS = {
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

# Nombre de decks
NB_DECKS = 3

# Seuil de re-mélange : si le shoe est trop bas, on re-mélange
THRESHOLD_REMELANGE = 40  # Moins de 40 cartes => on remélange

# Comptage de cartes (Hi-Lo) : global et persistant
running_count = 0

# Solde par défaut
solde_jetons = 200
# Mise courante
mise = 10  # Par défaut, modifiable via l’UI

# Pour gérer la 2ᵉ main
use_second_hand = False  # Indique si la 2ᵉ main est activée ou non

# ======================================================
#                  Classes
# ======================================================

class Carte:
    def __init__(self, enseigne, valeur):
        self.enseigne = enseigne
        self.valeur = valeur

    def __str__(self):
        """Ex: 'CA' = As de Coeur, 'P10' = 10 de Pique"""
        return f"{self.enseigne}{self.valeur}"

class Main:
    def __init__(self):
        self.cartes = []
        self.total = 0
        self.possede_as = False  # Pour repérer si un As est présent

    def ajouter_carte(self, carte):
        self.cartes.append(carte)
        # Gérer la valeur
        if carte.valeur == 'A':
            self.possede_as = True
        self.total += DICO_VALEURS[carte.valeur]
        # Comptage
        compter_carte(carte.valeur)

    def calculer_valeur(self):
        """
        Ajoute +10 si on a un As et qu'on ne bust pas en le comptant comme 11.
        """
        total_temp = self.total
        if self.possede_as and total_temp <= 11:
            total_temp += 10
        return total_temp

    def est_bust(self):
        """Renvoie True si la main dépasse 21."""
        return self.calculer_valeur() > 21

    def __str__(self):
        return " ".join(str(c) for c in self.cartes)

class Shoe:
    """
    Représente un “sabot” avec NB_DECKS paquets.
    Persiste tant qu’on n’a pas besoin de re-mélanger.
    """
    def __init__(self):
        self.liste_cartes = []
        for _ in range(NB_DECKS):
            for e in ENSEIGNES:
                for v in VALEURS:
                    self.liste_cartes.append(Carte(e, v))
        random.shuffle(self.liste_cartes)

    def distribuer(self):
        """
        Donne la première carte du sabot.
        Si le sabot est trop bas, on fait un re-mélange (dans un vrai casino, on redémarrerait
        aussi le count... ici on montre un exemple de logique "simplifiée").
        """
        if len(self.liste_cartes) < THRESHOLD_REMELANGE:
            # On re-mélange le shoe
            # Dans la vraie vie, on remettrait le count à 0,
            # car c'est un nouveau sabot. Ici, on fera un print indiquant
            # "mélange" et on continue le count pour la démo,
            # mais en pratique, un compteur prudent remettrait le count à 0.
            print(">>>> Le croupier re-mélange le sabot ! (dans un vrai casino, on reset le count)")
            global running_count
            running_count = 0
            self.__init__()  # On recrée un nouveau sabotage et on shuffle
        return self.liste_cartes.pop()

# ======================================================
#         Comptage Hi-Lo et Conseils Avancés
# ======================================================

def compter_carte(valeur):
    """
    Met à jour le running_count selon Hi-Lo.
    2-6 => +1
    10, J, Q, K, A => -1
    7, 8, 9 => 0
    """
    global running_count
    if valeur in ('2', '3', '4', '5', '6'):
        running_count += 1
    elif valeur in ('10','J','Q','K','A'):
        running_count -= 1
    # 7,8,9 => pas de changement

def conseil_count():
    """
    Indique un message sur la mise ou l'attitude générale
    selon le running_count.
    """
    rc = running_count
    if rc >= 8:
        return (f"Compte très élevé ({rc}). Avantage important : misez fort !")
    elif rc >= 4:
        return (f"Compte positif ({rc}). Avantage modéré : soyez agressif.")
    elif rc <= -6:
        return (f"Compte très négatif ({rc}). Le croupier est avantagé : baissez la mise.")
    elif rc <= -2:
        return (f"Compte négatif ({rc}). Prudence conseillée.")
    else:
        return (f"Compte neutre ({rc}). Pas de gros avantage particulier.")

def conseil_strategie(main_joueur, carte_vis_croupier):
    """
    Donne un conseil plus “affûté” qui tient compte :
    - Du total du joueur
    - De la carte visible du croupier
    - Du running_count (pour ajuster un peu le conseil)

    Logique simplifiée (inspirée d'une mini “basic strategy”),
    agrémentée de modifs en fonction du count.
    """
    total_j = main_joueur.calculer_valeur()
    # Valeur visible croupier : On convertit par ex 'A' => 1 ou 11, 'K'=>10, etc.
    # On sait que pour la stratégie, 'A' est comme "carte forte" (10).
    # On va se baser sur la "dangerosité" de la carte croupier.
    danger_croup = carte_dangereuse(carte_vis_croupier)

    # Ajustement si count est élevé
    # => le sabotage contient plus de 10 => on a plus de chance de bust en tirant,
    #   mais plus de prob de black jack. On va rester un peu plus souvent, par ex.
    # Ajustement si count est très négatif => plus de petites cartes => on peut se permettre de tirer plus ?
    global running_count

    # Marge ajustée : si le count est très positif, on surélève le "risque" de tirer.
    # On fait un SHIFT de 1 ou 2 points dans la décision (ex: “stand plus tôt”).
    shift = 0
    if running_count >= 5:
        shift = 1
    elif running_count <= -5:
        shift = -1

    # On applique une “mini table” de décision.
    # Ex: si total <= 11 => HIT
    #     si total 12-16 => stand si croupier 2-6 (carte “faible”), sinon hit
    #     si total >= 17 => stand
    # On y ajoute un shift. S’il est +1, on stand un peu plus tôt, s’il est -1, on hit un peu plus.

    # 1) Si total <= 11 + shift => always Hit
    # 2) Si 12 + shift <= total <= 16 + shift => stand si croupier <7, sinon hit
    # 3) Sinon => stand
    # Danger croupier <7 = croupier a 2-6 => carte “faible”
    # Danger croupier >=7 => carte “dangereuse” (7,8,9,10,A)
    # On fait un bloc plus ou moins flexible.

    # Calcul d’un total ajusté
    total_adj = total_j + shift

    if total_adj <= 11:
        return "Conseil: Tirez (vous êtes assez bas)."
    elif 12 <= total_adj <= 16:
        if danger_croup < 7:
            return "Conseil: Restez (croupier a une carte faible)."
        else:
            return "Conseil: Tirez (croupier a une carte forte)."
    else:
        return "Conseil: Restez (vous avez déjà un bon total)."

def carte_dangereuse(valeur):
    """
    Renvoie un “rang de danger” pour la carte visible du croupier.
    Plus c'est grand, plus c'est “dangereux”.
    """
    if valeur in ('10','J','Q','K','A'):
        return 10
    else:
        # Convertit '2'...'9' en int
        return int(valeur)  # si '2', int('2') = 2, etc.

# ======================================================
#         Fonctions de Jeu - Gérer les tours
# ======================================================

def initialiser_manche():
    """
    Met en place une nouvelle manche (distribution des cartes)
    sans re-créer le shoe, ni reset le running_count,
    sauf si re-mélange auto déjà fait dans shoe.distribuer().
    On gère le fait de jouer 1 ou 2 mains.
    """
    global main_j1, main_j2, main_croupier
    global main1_active, main2_active

    main_j1 = Main()
    main_j2 = Main()
    main_croupier = Main()
    
    main1_active = True
    main2_active = use_second_hand  # active si case cochée

    # Distribue 2 cartes main_j1
    main_j1.ajouter_carte(shoe.distribuer())
    main_j1.ajouter_carte(shoe.distribuer())

    # Si deuxième main activée
    if use_second_hand:
        main_j2.ajouter_carte(shoe.distribuer())
        main_j2.ajouter_carte(shoe.distribuer())

    # Croupier
    main_croupier.ajouter_carte(shoe.distribuer())
    main_croupier.ajouter_carte(shoe.distribuer())

def en_jeu():
    """
    Vrai si au moins une main est encore active et
    que le croupier n'a pas encore joué.
    """
    return (main1_active or main2_active) and not croupier_a_joue

def tirer(main_joueur, numero_main):
    global main1_active, main2_active

    # On distribue une carte
    main_joueur.ajouter_carte(shoe.distribuer())
    
    # Si bust => on “désactive” la main
    if main_joueur.est_bust():
        if numero_main == 1:
            main1_active = False
            perdre_mise()  # On retire la mise si on bust
            afficher_message(f"Main 1 BUST ! -{mise} jetons")
        else:
            main2_active = False
            perdre_mise()
            afficher_message(f"Main 2 BUST ! -{mise} jetons")

    maj_affichage()
    check_fin_joueur()

def rester(numero_main):
    """
    Le joueur reste pour la main numéro_main.
    """
    global main1_active, main2_active

    if numero_main == 1:
        main1_active = False
    else:
        main2_active = False

    afficher_message(f"Main {numero_main} Stand.")
    maj_affichage()
    check_fin_joueur()

def check_fin_joueur():
    """
    Si plus aucune main n’est active (tout le monde a Stand ou Bust),
    le croupier joue automatiquement.
    """
    if not (main1_active or main2_active):
        jouer_croupier()

def jouer_croupier():
    """
    Le croupier tire jusqu'à >=17. Puis compare.
    """
    global croupier_a_joue

    croupier_a_joue = True
    val_c = main_croupier.calculer_valeur()

    # Le croupier tire tant qu’il a < 17
    while val_c < 17:
        main_croupier.ajouter_carte(shoe.distribuer())
        val_c = main_croupier.calculer_valeur()

    # On compare toutes les mains non-bust
    # Gains/pertes
    message_final = ""
    
    if not main_j1.est_bust():
        message_final += comparer_mains(main_j1, 1)
    if use_second_hand and not main_j2.est_bust():
        message_final += comparer_mains(main_j2, 2)

    if message_final == "":
        # ça veut dire que les mains du joueur étaient bust
        message_final = "Toutes vos mains étaient bust avant que le croupier ne joue."

    afficher_message(message_final)
    maj_affichage()

def comparer_mains(main_joueur, numero_main):
    global solde_jetons, mise

    total_j = main_joueur.calculer_valeur()
    total_c = main_croupier.calculer_valeur()

    if total_c > 21:
        solde_jetons += mise
        return f"Main {numero_main} vs Croupier {total_c} => croupier bust : +{mise} jetons\n"
    elif total_j > total_c:
        solde_jetons += mise
        return f"Main {numero_main} => {total_j} vs {total_c} => vous gagnez : +{mise} jetons\n"
    elif total_j == total_c:
        return f"Main {numero_main} => {total_j} vs {total_c} => Égalité (push)\n"
    else:
        solde_jetons -= mise
        return f"Main {numero_main} => {total_j} vs {total_c} => croupier gagne : -{mise} jetons\n"

def perdre_mise():
    global solde_jetons, mise
    solde_jetons -= mise

# ======================================================
#       Interface Tkinter : Fenêtre et Widgets
# ======================================================

root = tk.Tk()
root.title("BlackJack - Shoe 3 decks, 2 mains en option, Comptage Hi-Lo persistant")

# Variables de suivi
shoe = Shoe()  # Sabot global
main_j1 = Main()
main_j2 = Main()
main_croupier = Main()
main1_active = False
main2_active = False
croupier_a_joue = False  # Savoir si le croupier a déjà fini

# Cadre principal
frame_principal = tk.Frame(root, padx=10, pady=10)
frame_principal.pack()

# Label d'info
label_info = tk.Label(frame_principal, text="Bienvenue au Blackjack !", fg="blue")
label_info.grid(row=0, column=0, columnspan=5, sticky="w")

# Labels pour afficher les mains
label_main1 = tk.Label(frame_principal, text="", fg="black")
label_main1.grid(row=1, column=0, columnspan=2, sticky="w")

label_main2 = tk.Label(frame_principal, text="", fg="black")
label_main2.grid(row=2, column=0, columnspan=2, sticky="w")

label_croupier = tk.Label(frame_principal, text="", fg="black")
label_croupier.grid(row=3, column=0, columnspan=2, sticky="w")

# Conseils
label_conseil_m1 = tk.Label(frame_principal, text="", fg="green")
label_conseil_m1.grid(row=1, column=2, columnspan=3, sticky="w")

label_conseil_m2 = tk.Label(frame_principal, text="", fg="green")
label_conseil_m2.grid(row=2, column=2, columnspan=3, sticky="w")

# Comptage
label_count = tk.Label(frame_principal, text="", fg="red")
label_count.grid(row=4, column=0, columnspan=5, sticky="w")

# Solde
label_solde = tk.Label(frame_principal, text=f"Solde : {solde_jetons}")
label_solde.grid(row=5, column=0, sticky="w")

# Mise
label_mise = tk.Label(frame_principal, text=f"Mise : {mise}")
label_mise.grid(row=5, column=1, sticky="e")
entry_mise = tk.Entry(frame_principal, width=5)
entry_mise.grid(row=5, column=2, sticky="w")
entry_mise.insert(0, str(mise))

# Case pour jouer la 2ᵉ main
var_second_hand = tk.BooleanVar(value=False)
check_second_hand = tk.Checkbutton(frame_principal, text="Jouer 2ᵉ main ?", variable=var_second_hand)
check_second_hand.grid(row=6, column=0, sticky="w")

# Boutons d'actions
btn_tirer_m1 = tk.Button(frame_principal, text="Tirer (Main 1)", command=lambda: tirer(main_j1, 1))
btn_tirer_m1.grid(row=7, column=0)

btn_stand_m1 = tk.Button(frame_principal, text="Stand (Main 1)", command=lambda: rester(1))
btn_stand_m1.grid(row=7, column=1)

btn_tirer_m2 = tk.Button(frame_principal, text="Tirer (Main 2)", command=lambda: tirer(main_j2, 2))
btn_tirer_m2.grid(row=8, column=0)

btn_stand_m2 = tk.Button(frame_principal, text="Stand (Main 2)", command=lambda: rester(2))
btn_stand_m2.grid(row=8, column=1)

btn_nouvelle_manche = tk.Button(frame_principal, text="Nouvelle Manche", command=lambda: nouvelle_manche())
btn_nouvelle_manche.grid(row=7, column=2)

btn_quitter = tk.Button(frame_principal, text="Quitter", command=root.quit)
btn_quitter.grid(row=8, column=2)

def afficher_message(texte):
    label_info.config(text=texte)

def maj_affichage():
    """
    Met à jour l'affichage des mains, du croupier,
    du solde, de la mise, etc.
    """
    # Affichage main 1
    txt_m1 = f"Main 1: {main_j1} (Total={main_j1.calculer_valeur()})"
    label_main1.config(text=txt_m1)

    # Affichage main 2 (seulement si use_second_hand)
    if use_second_hand:
        txt_m2 = f"Main 2: {main_j2} (Total={main_j2.calculer_valeur()})"
        label_main2.config(text=txt_m2)
    else:
        label_main2.config(text="(2ᵉ main non jouée)")

    # Affichage croupier
    if not croupier_a_joue and en_jeu():
        # On n'affiche que la 1ère carte
        if len(main_croupier.cartes) > 0:
            c0 = main_croupier.cartes[0]
            label_croupier.config(text=f"Croupier: [{c0}] + [Carte Cachée]")
        else:
            label_croupier.config(text="Croupier: (vide)")
    else:
        # Croupier a joué ou plus de main active => on dévoile tout
        label_croupier.config(
            text=f"Croupier: {main_croupier} (Total={main_croupier.calculer_valeur()})"
        )

    # Solde
    label_solde.config(text=f"Solde : {solde_jetons}")

    # Mise
    label_mise.config(text=f"Mise : {mise}")

    # Comptage
    label_count.config(text=f"Comptage Hi-Lo : {running_count}\n{conseil_count()}")

    # Conseils
    carte_vis_croupier = main_croupier.cartes[0].valeur  # carte visible
    if not main_j1.est_bust() and not croupier_a_joue:
        label_conseil_m1.config(text=conseil_strategie(main_j1, carte_vis_croupier))
    else:
        label_conseil_m1.config(text="")

    if use_second_hand and not main_j2.est_bust() and not croupier_a_joue:
        label_conseil_m2.config(text=conseil_strategie(main_j2, carte_vis_croupier))
    else:
        label_conseil_m2.config(text="")

def nouvelle_manche():
    """
    Prépare la configuration d'une nouvelle manche :
    - Mise à jour de la mise
    - Active/désactive la 2ᵉ main selon la case
    - (Ré)initialise la manche et le croupier
    """
    global mise, use_second_hand, croupier_a_joue

    # Récupérer la nouvelle mise
    try:
        m_temp = int(entry_mise.get())
        if m_temp < 1:
            afficher_message("La mise doit être >= 1.")
            return
        mise = m_temp
    except ValueError:
        afficher_message("La mise doit être un entier.")
        return

    # Vérifie si on veut la 2ᵉ main
    use_second_hand = var_second_hand.get()

    croupier_a_joue = False

    # Distribue les cartes
    initialiser_manche()

    afficher_message("Nouvelle donne !")
    maj_affichage()

# On lance au démarrage
nouvelle_manche()

root.mainloop()
