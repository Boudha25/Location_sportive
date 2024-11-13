import customtkinter as ctk
from tkinter import ttk
from tkcalendar import Calendar
from Utils import trier_colonne


class GestionMateriel(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db  # Conserver une référence à la base de données

        # Instanciation des widgets
        self.num_label = None
        self.num_entry = None
        self.type_label = None
        self.type_entry = None
        self.grandeur_label = None
        self.grandeur_entry = None
        self.cote_label = None
        self.cote_frame = None
        self.cote_radio_gauche = None
        self.cote_radio_droite = None
        self.date_achat_label = None
        self.date_achat_entry = None
        self.calendar_button = None
        self.status_label = None
        self.status_dropdown = None
        self.button_frame = None
        self.add_button = None
        self.update_button = None
        self.delete_button = None
        self.message_label = None
        self.top = None
        self.cal = None
        self.select_button = None

        # Variables pour les champs
        self.status_var = ctk.StringVar(value="Disponible")
        self.cote_var = ctk.StringVar(value="gauche")  # Valeur par défaut pour le champ cote

        # Titre de la page
        self.title_label = ctk.CTkLabel(master=self, text="Gestion du Matériel", font=("Arial", 20))
        self.title_label.pack(pady=10)

        # Cadre pour le tableau Treeview
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Cadre pour les champs d'entrée et boutons
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Configuration du Treeview pour afficher le matériel
        self.columns = ("Id_materiel", "Numéro d'équipement", "Type", "Grandeur", "Côté", "Date d'achat", "Status")
        self.treeview = ttk.Treeview(self.table_frame, columns=self.columns, show="headings")

        # Configuration des colonnes
        for col in self.columns:
            self.treeview.heading(col, text=col.capitalize(), command=lambda _col=col: self.trier_colonne_materiel(_col, False))
            self.treeview.column(col, width=130 if col != "Id_materiel" else 75)

        # Ajouter la barre de défilement verticale
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.treeview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.pack(fill="both", expand=True)

        # Ajout du binding pour sélectionner un matériel sur double-clic
        self.treeview.bind("<Double-1>", self.selectionner_materiel)

        # Configuration des champs d'entrée et des boutons
        self.configurer_champs()
        self.configurer_boutons()

        # Initialisation de la liste du matériel
        self.lister_materiel()

    def configurer_champs(self):
        """Configurer les champs d'entrée pour chaque attribut du matériel"""
        # Champ pour le numéro de matériel
        self.num_label = ctk.CTkLabel(self.form_frame, text="Numéro d'Équipement")
        self.num_label.pack()
        self.num_entry = ctk.CTkEntry(self.form_frame)
        self.num_entry.pack()

        # Champ pour le type de matériel
        self.type_label = ctk.CTkLabel(self.form_frame, text="Type")
        self.type_label.pack()
        self.type_entry = ctk.CTkEntry(self.form_frame)
        self.type_entry.pack()

        # Champ pour la grandeur
        self.grandeur_label = ctk.CTkLabel(self.form_frame, text="Grandeur")
        self.grandeur_label.pack()
        self.grandeur_entry = ctk.CTkEntry(self.form_frame)
        self.grandeur_entry.pack()

        # Cote radio boutons
        self.cote_label = ctk.CTkLabel(self.form_frame, text="Côté")
        self.cote_label.pack()
        self.cote_frame = ctk.CTkFrame(self.form_frame)
        self.cote_frame.pack()
        self.cote_radio_gauche = ctk.CTkRadioButton(self.cote_frame, text="Gauche", variable=self.cote_var, value="gauche")
        self.cote_radio_gauche.pack(side="left", padx=5)
        self.cote_radio_droite = ctk.CTkRadioButton(self.cote_frame, text="Droite", variable=self.cote_var, value="droite")
        self.cote_radio_droite.pack(side="left", padx=5)

        # Date d'achat avec calendrier
        self.date_achat_label = ctk.CTkLabel(self.form_frame, text="Date d'achat")
        self.date_achat_label.pack()
        self.date_achat_entry = ctk.CTkEntry(self.form_frame)
        self.date_achat_entry.pack()
        self.calendar_button = ctk.CTkButton(self.form_frame, text="Choisir la date", command=self.open_calendar)
        self.calendar_button.pack()

        # Statut dropdown
        self.status_label = ctk.CTkLabel(self.form_frame, text="Status")
        self.status_label.pack()
        self.status_dropdown = ctk.CTkOptionMenu(self.form_frame, values=["Disponible", "Prêté"], variable=self.status_var)
        self.status_dropdown.pack()

    def configurer_boutons(self):
        """Configurer les boutons d'ajout, modification et suppression"""
        self.button_frame = ctk.CTkFrame(self.form_frame)
        self.button_frame.pack(pady=10)

        self.add_button = ctk.CTkButton(self.button_frame, text="Ajouter Équipement", command=self.ajouter_materiel)
        self.add_button.pack(pady=5, fill="x")

        self.update_button = ctk.CTkButton(self.button_frame, text="Modifier Équipement", command=self.modifier_materiel)
        self.update_button.pack(pady=5, fill="x")

        self.delete_button = ctk.CTkButton(self.button_frame, text="Supprimer Équipement", command=self.supprimer_materiel)
        self.delete_button.pack(pady=5, fill="x")

        self.message_label = ctk.CTkLabel(self.form_frame, text="")
        self.message_label.pack(pady=10)

    def open_calendar(self):
        """Ouvre le calendrier pour sélectionner la date d'achat"""
        self.top = ctk.CTkToplevel(self)
        self.top.attributes('-topmost', True)
        self.cal = Calendar(self.top, selectmode='day', date_pattern='yyyy-mm-dd')
        self.cal.pack()
        self.select_button = ctk.CTkButton(self.top, text="Sélectionner", command=self.get_date)
        self.select_button.pack()

    def get_date(self):
        self.date_achat_entry.delete(0, ctk.END)
        self.date_achat_entry.insert(0, self.cal.get_date())
        self.top.destroy()

    def selectionner_materiel(self, event):
        """Remplit les champs avec les informations du matériel sélectionné"""
        selected_item = self.treeview.selection()[0]
        materiel = self.treeview.item(selected_item, "values")
        if materiel:
            self.num_entry.delete(0, ctk.END)
            self.num_entry.insert(0, materiel[1])
            self.type_entry.delete(0, ctk.END)
            self.type_entry.insert(0, materiel[2])
            self.grandeur_entry.delete(0, ctk.END)
            self.grandeur_entry.insert(0, materiel[3])
            self.cote_var.set(materiel[4])
            self.date_achat_entry.delete(0, ctk.END)
            self.date_achat_entry.insert(0, materiel[5])
            self.status_var.set(materiel[6])

    def trier_colonne_materiel(self, col, reverse):
        trier_colonne(self.treeview, col, reverse)

    def ajouter_materiel(self):
        """Ajoute un nouveau matériel dans la base de données"""
        num_materiel = self.num_entry.get()
        type_materiel = self.type_entry.get()
        grandeur = self.grandeur_entry.get()
        cote = self.cote_var.get()
        date_achat = self.date_achat_entry.get()
        # Conversion de l'état en entier
        status = 1 if self.status_var.get() == "Disponible" else 0
        self.db.ajouter('materiel', (num_materiel, type_materiel, grandeur, cote, date_achat, status))
        self.message_label.configure(text="Matériel ajouté avec succès.", text_color="green")
        self.efface_champs()
        self.lister_materiel()

    def modifier_materiel(self):
        """Modifie le matériel sélectionné dans la base de données"""
        selected_item = self.treeview.selection()
        if selected_item:
            item_id = self.treeview.item(selected_item[0], "values")[0]

            # Conversion de l'état en entier (1 pour "Disponible", 0 pour "Prêté")
            status = 1 if self.status_var.get() == "Disponible" else 0

            # Mise à jour des autres données
            updated_data = (
                self.num_entry.get(),
                self.type_entry.get(),
                self.grandeur_entry.get(),
                self.cote_var.get(),
                self.date_achat_entry.get(),
                status  # Utilisation de la valeur convertie
            )

            # Appel de la méthode de modification avec les nouvelles données
            self.db.modifier('materiel', item_id, updated_data)

            # Mise à jour du message de succès
            self.message_label.configure(text="Matériel modifié avec succès", text_color="green")

            # Effacement des champs et rafraîchissement de la liste
            self.efface_champs()
            self.lister_materiel()

    def supprimer_materiel(self):
        """Supprime le matériel sélectionné dans la base de données"""
        selected_item = self.treeview.selection()
        if selected_item:
            item_id = self.treeview.item(selected_item[0], "values")[0]
            self.db.supprimer("materiel", item_id)
            self.message_label.configure(text="Équipement supprimé", text_color="green")
            self.efface_champs()
            self.lister_materiel()

    def lister_materiel(self):
        """Liste tout le matériel dans le Treeview"""
        self.treeview.delete(*self.treeview.get_children())
        materiel_data = self.db.lister("materiel")

        for materiel in materiel_data:
            # Supposons que 'materiel' est un tuple comme (id_materiel, num_materiel, type, grandeur, cote, date_achat, status)
            id_materiel, num_materiel, type_materiel, grandeur, cote, date_achat, status = materiel

            # Transformer le statut en texte
            status_text = "Disponible" if status == 1 else "Prêté"

            # Insérer les données avec le statut transformé dans le Treeview
            self.treeview.insert("", ctk.END, values=(
            id_materiel, num_materiel, type_materiel, grandeur, cote, date_achat, status_text))

    def efface_champs(self):
        """Efface les champs d'entrée après une opération"""
        self.num_entry.delete(0, ctk.END)
        self.type_entry.delete(0, ctk.END)
        self.grandeur_entry.delete(0, ctk.END)
        self.cote_var.set("gauche")
        self.date_achat_entry.delete(0, ctk.END)
        self.status_var.set("Disponible")
