# -*- coding: utf-8 -*-
import sqlite3

class Database:
    def __init__(self, db_name="location.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Création des tables dans la base de données"""
        try:
            conn = self.conn
            conn.execute('''
                CREATE TABLE IF NOT EXISTS materiel (
                    id_materiel INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    num_materiel TEXT NOT NULL,
                    type TEXT,
                    grandeur TEXT,
                    cote TEXT,
                    date_achat INTEGER,
                    status INTEGER DEFAULT 1  -- 0 pour "prêté", 1 pour "disponible"
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS eleve (
                    id_eleve INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    nom TEXT,
                    prenom TEXT,
                    code TEXT
                )
            ''')

 #           conn.execute('DROP TABLE IF EXISTS emprunts')
 #           conn.commit()  # Sauvegarde les changements

            conn.execute('''
                CREATE TABLE IF NOT EXISTS emprunts (
                    id_emprunt INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_eleve INTEGER NOT NULL,
                    id_materiel INTEGER NOT NULL,
                    date_emprunt INTEGER,
                    date_retour INTEGER,
                    FOREIGN KEY (id_materiel) REFERENCES materiel(id_materiel),
                    FOREIGN KEY (id_eleve) REFERENCES eleve(id_eleve)
                )
            ''')
        except sqlite3.Error as e:
            print(f"Erreur lors de la création des tables : {e}")

    def ajouter(self, table, values):
        try:
            conn = self.conn  # Utilisation de la connexion sans 'with'
            if table == 'materiel':
                conn.execute('''
                    INSERT INTO materiel (num_materiel, type, grandeur, cote, date_achat, status) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', values)
            elif table == 'eleve':
                conn.execute('''
                    INSERT INTO eleve (nom, prenom, code) 
                    VALUES (?, ?, ?)
                ''', values)
            elif table == 'emprunts':
                conn.execute('''
                    INSERT INTO emprunts (id_eleve, id_materiel, date_emprunt, date_retour) 
                    VALUES (?, ?, ?, NULL)
                ''', values)
            conn.commit()  # Sauvegarde les changements
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout dans la table {table} : {e}")

    def supprimer(self, table, item_id):
        try:
            conn = self.conn  # Utilisation de la connexion sans 'with'
            if table == 'materiel':
                conn.execute('DELETE FROM materiel WHERE id_materiel = ?', (item_id,))
            elif table == 'eleve':
                conn.execute('DELETE FROM eleve WHERE id_eleve = ?', (item_id,))
            elif table == 'emprunts':
                conn.execute('DELETE FROM emprunts WHERE id_emprunt = ?', (item_id,))
            conn.commit()  # Sauvegarde les changements
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression dans la table {table} : {e}")

    def modifier(self, table, item_id, values):
        try:
            conn = self.conn  # Utilisation de la connexion sans 'with'
            if table == 'materiel':
                conn.execute('''
                    UPDATE materiel 
                    SET num_materiel = ?, type = ?, grandeur = ?, cote = ?, date_achat = ?, status = ? 
                    WHERE id_materiel = ?
                ''', (*values, item_id))
            elif table == 'eleve':
                conn.execute('''
                    UPDATE eleve SET nom = ?, prenom = ?, code = ? 
                    WHERE id_eleve = ?
                ''', (*values, item_id))
            elif table == 'emprunts':
                conn.execute('''
                    UPDATE emprunts SET date_retour = ? 
                    WHERE id_emprunt = ?
                ''', (*values, item_id))
            conn.commit()  # Sauvegarde les changements
        except sqlite3.Error as e:
            print(f"Erreur lors de la modification dans la table {table} : {e}")

    def lister(self, table):
        try:
            cur = self.conn.cursor()  # Création d'un curseur sans 'with'
            cur.execute(f'SELECT * FROM {table}')
            rows = cur.fetchall()
            cur.close()  # Fermer le curseur
            return rows
        except sqlite3.Error as e:
            print(f"Erreur lors du listing dans la table {table} : {e}")
            return []

    def rechercher(self, table, item_id):
        try:
            cur = self.conn.cursor()
            if table == 'materiel':
                cur.execute('SELECT * FROM materiel WHERE id_materiel = ?', (item_id,))
            elif table == 'eleve':
                cur.execute('SELECT * FROM eleve WHERE id_eleve = ?', (item_id,))
            elif table == 'emprunts':
                cur.execute('SELECT * FROM emprunts WHERE id_emprunt = ?', (item_id,))
            result = cur.fetchone()
            cur.close()  # Fermer le curseur
            return result
        except sqlite3.Error as e:
            print(f"Erreur lors de la recherche dans la table {table} : {e}")
            return None

    def selectionner(self, table, column, value):
        try:
            cur = self.conn.cursor()
            cur.execute(f'SELECT * FROM {table} WHERE {column} = ?', (value,))
            rows = cur.fetchall()
            cur.close()  # Fermer le curseur
            return rows
        except sqlite3.Error as e:
            print(f"Erreur lors de la sélection dans la table {table} : {e}")
            return []

    def rechercher_eleve_par_code(self, code):
        """Recherche un élève par son code pour éviter les doublons"""
        try:
            cur = self.conn.cursor()  # Création d'un curseur sans 'with'
            cur.execute('SELECT * FROM eleve WHERE code = ?', (code,))
            result = cur.fetchone()  # Retourne None si l'élève n'est pas trouvé
            cur.close()  # Fermer le curseur
            return result
        except sqlite3.Error as e:
            print(f"Erreur lors de la recherche d'élève par code : {e}")
            return None

    def close(self):
        """Fermer la connexion à la base de données"""
        self.conn.close()

    def lister_emprunts(self):
        # Requête SQL avec jointures pour récupérer les informations complètes
        try:
            emprunts = self.conn.execute('''
                SELECT eleve.nom, eleve.prenom, materiel.num_materiel, materiel.type, materiel.cote, emprunts.date_emprunt, emprunts.date_retour
                FROM emprunts
                JOIN eleve ON emprunts.id_eleve = eleve.id_eleve
                JOIN materiel ON emprunts.id_materiel = materiel.id_materiel
                WHERE materiel.status = 0 AND emprunts.date_retour IS NULL
            ''').fetchall()
            return emprunts
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des emprunts : {e}")
            return []

    def selectionner_dernier_emprunt_actif(self, id_materiel):
        """Sélectionne le dernier emprunt actif pour un matériel spécifique."""
        try:
            cur = self.conn.cursor()
            cur.execute('''
                SELECT * FROM emprunts 
                WHERE id_materiel = ? AND date_retour IS NULL
                ORDER BY date_emprunt DESC LIMIT 1
            ''', (id_materiel,))
            emprunt = cur.fetchone()  # Retourne le dernier emprunt actif
            cur.close()  # Fermer le curseur
            return emprunt
        except sqlite3.Error as e:
            print(f"Erreur lors de la sélection du dernier emprunt actif pour le matériel {id_materiel} : {e}")
            return None
