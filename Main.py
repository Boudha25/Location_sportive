import customtkinter as ctk
from tkinter import ttk
from BaseDonnee import Database
from GestionEmprunt import GestionEmprunts
from GestionEleve import GestionEleve
from GestionMateriel import GestionMateriel

class MainApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Gestion de Location Sportive")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True)

        self.db = Database("location.db")

        self.gestion_emprunts = GestionEmprunts(self.notebook, self.db)
        self.gestion_eleve = GestionEleve(self.notebook, self.db)
        self.gestion_materiel = GestionMateriel(self.notebook, self.db)

        self.notebook.add(self.gestion_emprunts, text="Emprunts")
        self.notebook.add(self.gestion_eleve, text="Élèves")
        self.notebook.add(self.gestion_materiel, text="Matériel")

        # Associer l'événement de changement d'onglet
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.root.mainloop()

    def on_tab_changed(self, event):
        selected_tab = event.widget.tab(event.widget.index("current"))['text']

        # Vérifier quel onglet est sélectionné et appeler la méthode de mise à jour
        if selected_tab == "Emprunts":
            self.gestion_emprunts.lister_emprunts()
        elif selected_tab == "Matériel":
            self.gestion_materiel.lister_materiel()
        elif selected_tab == "Élèves":
            self.gestion_eleve.lister_eleves()

if __name__ == "__main__":
    app = MainApp()
