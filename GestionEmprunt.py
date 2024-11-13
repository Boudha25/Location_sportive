from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk
from Utils import trier_colonne, afficher_message
from datetime import datetime

class GestionEmprunts(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.id_materiels_scannes = []  # Liste des items scannés
        self.pack(padx=20, pady=20)

        # Créer un Canvas pour l'arrière-plan
        self.canvas = ctk.CTkCanvas(self, width=1200, height=800)
        self.canvas.pack(fill="both", expand=True)

        # Charger l'image d'arrière-plan
        self.image = Image.open("sport_background.jpg").resize((1200, 600), Image.LANCZOS)
        self.ctk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.ctk_image)

        # Widgets pour l'ajout d'un emprunt
        self.label_id_eleve = ctk.CTkLabel(self.canvas, text="Code Élève:")
        self.label_id_eleve.pack(pady=5)
        self.id_eleve_entry = ctk.CTkEntry(self.canvas, width=300)
        self.id_eleve_entry.pack(pady=5)

        self.label_id_materiel = ctk.CTkLabel(self.canvas, text="Liste de matériel:")
        self.label_id_materiel.pack(pady=5)
        self.id_materiel_entry = ctk.CTkEntry(self.canvas, width=300)
        self.id_materiel_entry.pack(pady=5)

        # Liste des items à emprunter
        self.scanned_items_label= ctk.CTkLabel(self.canvas, text="Aucun item dans la liste")
        self.scanned_items_label.pack(pady=5)

        # Bouton annuler dernier item ajouté
        self.annuler_button = ctk.CTkButton(self.canvas, text="Annuler Dernier Item", command=self.annuler_dernier_item)
        self.annuler_button.pack(pady=5)

        # Date d'emprunt
        self.label_date_emprunt = ctk.CTkLabel(self.canvas, text="Date d'Emprunt:")
        self.label_date_emprunt.pack(pady=5)
        self.date_emprunt_entry = ctk.CTkEntry(self.canvas, width=300)
        self.date_emprunt_entry.insert(0, self.get_today_date())  # Date du jour par défaut
        self.date_emprunt_entry.pack(pady=5)

        # Boutons de confirmation d'emprunt
        self.confirmer_button = ctk.CTkButton(self.canvas, text="Confirmer Emprunt", command=self.confirmer_emprunt)
        self.confirmer_button.pack()

        # Boutons de retour d'équipement
        self.retour_button = ctk.CTkButton(self.canvas, text="Retourner Équipement", command=self.retourner_equipement)
        self.retour_button.pack(pady=5)

        # Bind de la touche <Tab> pour ajouter chaque item scanné
        self.id_materiel_entry.bind("<Tab>", self.ajouter_item_scanne)
        self.id_materiel_entry.focus_set()

        # Message d'état
        self.message_label = ctk.CTkLabel(self.canvas, text="")
        self.message_label.pack(pady=10)

        # Configuration du Treeview pour afficher les emprunts
        self.columns = ("Nom", "Prénom", "Numéro d'équipement", "Type", "Côté", "Date d'emprunt", "Date de retour")
        self.treeview = ttk.Treeview(self.canvas, columns=self.columns, show="headings")

        for col in self.columns:
            self.treeview.heading(col, text=col.replace("_", " ").capitalize(),
                                  command=lambda _col=col: self.trier_colonne_emprunt(_col, False))
            self.treeview.column(col, width=130)

        self.treeview.pack(pady=10, fill="x")
        self.lister_emprunts()  # Charger les emprunts existants au démarrage

    @staticmethod
    def get_today_date():
        return datetime.now().strftime("%Y-%m-%d")

    def lister_emprunts(self):
        self.treeview.delete(*self.treeview.get_children())
        emprunts = self.db.lister_emprunts()
        print("EMPRUNT", emprunts)

        for emprunt in emprunts:
            self.treeview.insert("", "end", values=(
                emprunt[0], emprunt[1], emprunt[2], emprunt[3], emprunt[4], emprunt[5], emprunt[6]
            ))

    # Méthode dans le fichier Utils.py
    def trier_colonne_emprunt(self, col, reverse):
        trier_colonne(self.treeview, col, reverse)

    def ajouter_item_scanne(self, event=None):
        num_materiel = self.id_materiel_entry.get().strip()
        if num_materiel and num_materiel not in self.id_materiels_scannes:
            self.id_materiels_scannes.append(num_materiel)
            self.id_materiel_entry.delete(0, 'end')
            afficher_message(self.message_label, f"Item {num_materiel} ajouté", "green")
        else:
            afficher_message(self.message_label,f"Item {num_materiel} déjà ajouté", "orange")

        self.scanned_items_label.configure(text=", ".join(self.id_materiels_scannes))

        # Rendre le bouton visible s'il y a au moins un item dans la liste
        if self.id_materiels_scannes:
            self.annuler_button.pack()

        return "break"

    def annuler_dernier_item(self):
        if self.id_materiels_scannes:
            dernier_item = self.id_materiels_scannes.pop()
            self.scanned_items_label.configure(text=", ".join(self.id_materiels_scannes))
            afficher_message(self.message_label,f"Item {dernier_item} retiré", "red")

            # Cacher le bouton s'il n'y a plus d'items dans la liste
            if not self.id_materiels_scannes:
                self.annuler_button.pack_forget()
        else:
            afficher_message(self.message_label,"Aucun item à retirer", "orange")

    def confirmer_emprunt(self):
        code_eleve = self.id_eleve_entry.get()
        resultat_eleve = self.db.selectionner("eleve", "code", code_eleve)
        if not resultat_eleve:
            afficher_message(self.message_label,"Élève introuvable", "red")
            return

        id_eleve = resultat_eleve[0][0]
        date_emprunt = self.get_today_date()

        for num_materiel in self.id_materiels_scannes:
            resultat_materiel = self.db.selectionner("materiel", "num_materiel", num_materiel)
            if not resultat_materiel:
                afficher_message(self.message_label,f"Matériel {num_materiel} introuvable", "red")
                continue
            id_materiel = resultat_materiel[0][0]
            self.db.ajouter('emprunts', (id_eleve, id_materiel, date_emprunt))

            nouveau_statut = 0
            self.db.modifier('materiel', id_materiel, (num_materiel, *resultat_materiel[0][2:-1], nouveau_statut))

        afficher_message(self.message_label,"Emprunt(s) ajouté(s) avec succès", "green")
        self.id_materiels_scannes.clear() # Vide la liste après l'ajout d'équipement
        self.id_eleve_entry.delete(0, 'end')
        self.scanned_items_label.configure(text="")  # Efface les items affichés
        self.lister_emprunts()

    def retourner_equipement(self):
        """Gère le retour des équipements scannés et met à jour leur statut à 'disponible'."""
        if not self.id_materiels_scannes:
            afficher_message(self.message_label,"Aucun item scanné pour retour", "orange")
            return

        for num_materiel in self.id_materiels_scannes:
            resultat_materiel = self.db.selectionner("materiel", "num_materiel", num_materiel)
            if not resultat_materiel:
                afficher_message(self.message_label,f"Matériel {num_materiel} introuvable", "red")
                continue

            id_materiel = resultat_materiel[0][0]
            nouveau_statut = 1  # Statut "disponible"

            self.db.modifier('materiel', id_materiel, (num_materiel, *resultat_materiel[0][2:-1], nouveau_statut))

            # Récupération du dernier emprunt actif pour ce matériel
            emprunt_actif = self.db.selectionner_dernier_emprunt_actif(id_materiel)

            if emprunt_actif:
                id_emprunt = emprunt_actif[0]  # ID de l'emprunt actif
                date_retour = datetime.now().strftime('%Y-%m-%d')

                # Mise à jour de la date de retour pour cet emprunt
                self.db.modifier("emprunts", id_emprunt, (date_retour,))

        afficher_message(self.message_label,"Retour(s) effectué(s) avec succès", "green")
        self.id_materiels_scannes.clear()  # Vide la liste après le retour
        self.scanned_items_label.configure(text="")  # Efface les items affichés
        self.lister_emprunts()  # Actualiser l'affichage des emprunts
