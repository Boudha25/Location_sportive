import customtkinter as ctk
from tkinter import ttk
from Utils import trier_colonne, afficher_message

class GestionEleve(ctk.CTkFrame):
    def __init__(self, master, db):
        """Initialise le cadre de gestion des élèves."""
        super().__init__(master)
        self.db = db  # Instance de la base de données
        self.code_entry = None
        self.prenom_entry = None
        self.nom_entry = None
        self.eleve_selectionne_id = None
        self._setup_widgets()  # Initialise les widgets de l'interface

    def _setup_widgets(self):
        """Configure les widgets pour l'interface de gestion des élèves."""
        self.title_label = ctk.CTkLabel(self, text="Gestion des Élèves", font=("Arial", 20))
        self.title_label.pack(pady=10)

        self._create_table_frame()
        self._create_entry_fields()
        self._create_buttons()
        self._create_message_label()
        self.lister_eleves()  # Affiche les élèves existants

    def _create_table_frame(self):
        """Création du cadre pour la table d'affichage des élèves."""
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.columns = ("Id élève", "Nom", "Prenom", "Code d'élève")
        self.treeview = ttk.Treeview(self.table_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.treeview.heading(col, text=col.capitalize(), command=lambda _col=col: self.trier_colonne_eleve(_col, False))
            self.treeview.column(col, width=120 if col != "Id élève" else 50)

        self.scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.treeview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.pack(fill="both", expand=True)

        self.treeview.bind("<Double-1>", self.selectionner_eleve)  # Double-clic pour sélectionner un élève

    def _create_entry_fields(self):
        """Création des champs de saisie pour les informations de l'élève."""
        for field, label_text in [("nom", "Nom"), ("prenom", "Prénom"), ("code", "Code")]:
            label = ctk.CTkLabel(self, text=label_text)
            label.pack()
            setattr(self, f"{field}_label", label)
            entry = ctk.CTkEntry(self)
            entry.pack()
            setattr(self, f"{field}_entry", entry)

    def _create_buttons(self):
        """Création des boutons pour les actions CRUD et de recherche."""
        self.add_button = ctk.CTkButton(self, text="Ajouter Élève", command=self.ajouter_eleve)
        self.add_button.pack(pady=10)

        self.search_label = ctk.CTkLabel(self, text="Rechercher (Nom, Prénom ou Code)")
        self.search_label.pack()
        self.search_entry = ctk.CTkEntry(self)
        self.search_entry.pack()
        self.search_button = ctk.CTkButton(self, text="Rechercher Élève", command=self.rechercher_eleve)
        self.search_button.pack(pady=10)

        self.update_button = ctk.CTkButton(self, text="Modifier Élève", command=self.modifier_eleve)
        self.update_button.pack(pady=10)

        self.delete_button = ctk.CTkButton(self, text="Supprimer Élève", command=self.supprimer_eleve)
        self.delete_button.pack(pady=10)

    def _create_message_label(self):
        """Création d'un label pour afficher les messages d'erreur et de confirmation."""
        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack()

    # --- Fonctions de gestion des élèves --- #
    def lister_eleves(self):
        """Affiche tous les élèves dans le Treeview."""
        self.treeview.delete(*self.treeview.get_children())
        eleves = self.db.lister('eleve')
        for eleve in eleves:
            self.treeview.insert("", "end", values=eleve)

    def ajouter_eleve(self):
        """Ajoute un élève après vérification des champs et des doublons."""
        nom, prenom, code = self.nom_entry.get(), self.prenom_entry.get(), self.code_entry.get()

        if nom and prenom and code:
            if self.db.rechercher_eleve_par_code(code):
                afficher_message(self.message_label, "Doublon détecté : L'élève existe déjà!", "red")
            else:
                self.db.ajouter('eleve', (nom, prenom, code))
                afficher_message(self.message_label, "Élève ajouté avec succès.")
                self._clear_entries()
                self.lister_eleves()
        else:
            afficher_message(self.message_label, "Veuillez remplir tous les champs.", "red")

    def selectionner_eleve(self, event):
        """Charge les informations de l'élève sélectionné dans les champs d'entrée."""
        selected_item = self.treeview.selection()[0]
        eleve = self.treeview.item(selected_item, "values")
        self.eleve_selectionne_id = eleve[0]
        for i, field in enumerate(["nom", "prenom", "code"], 1):
            getattr(self, f"{field}_entry").delete(0, ctk.END)
            getattr(self, f"{field}_entry").insert(0, eleve[i])

    def modifier_eleve(self):
        """Modifie les informations d'un élève sélectionné."""
        if self.eleve_selectionne_id:
            nom, prenom, code = self.nom_entry.get(), self.prenom_entry.get(), self.code_entry.get()
            if nom and prenom and code:
                self.db.modifier('eleve', self.eleve_selectionne_id, (nom, prenom, code))
                afficher_message(self.message_label, "Élève modifié avec succès.")
                self._clear_entries()
                self.lister_eleves()

    def supprimer_eleve(self):
        """Supprime l'élève sélectionné de la base de données."""
        if self.eleve_selectionne_id:
            self.db.supprimer('eleve', self.eleve_selectionne_id)
            afficher_message(self.message_label, "Élève supprimé avec succès.")
            self._clear_entries()
            self.lister_eleves()

    def rechercher_eleve(self):
        """Recherche un élève dans la base de données."""
        recherche = self.search_entry.get().strip().lower()
        self.treeview.delete(*self.treeview.get_children())
        eleves = self.db.lister('eleve')
        for eleve in eleves:
            if any(recherche in str(eleve[i]).lower() for i in range(1, 4)):
                self.treeview.insert("", "end", values=eleve)

    def trier_colonne_eleve(self, col, reverse):
        trier_colonne(self.treeview, col, reverse)

    def _clear_entries(self):
        """Efface les champs d'entrée et réinitialise l'ID de l'élève sélectionné."""
        for field in ["nom", "prenom", "code"]:
            getattr(self, f"{field}_entry").delete(0, ctk.END)
        self.eleve_selectionne_id = None
