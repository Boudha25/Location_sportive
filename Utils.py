
def trier_colonne(treeview, col, reverse):
    """Trie le Treeview par une colonne spécifiée, avec un tri numérique ou alphabétique selon le contenu."""
    l = [(treeview.set(k, col), k) for k in treeview.get_children('')]

    # Fonction de tri pour différencier les valeurs numériques des valeurs textuelles
    def sort_key(value):
        val = value[0]
        try:
            return 0, float(val)  # Trie numériquement
        except ValueError:
            return 1, val  # Trie alphabétiquement si ce n'est pas un nombre

    # Trie la liste avec la clé de tri
    l.sort(key=sort_key, reverse=reverse)

    # Réorganise les éléments dans Treeview
    for index, (_, k) in enumerate(l):
        treeview.move(k, '', index)

    # Met à jour la commande de tri sur l'en-tête
    treeview.heading(col, command=lambda: trier_colonne(treeview, col, not reverse))

def afficher_message(label, message, couleur="green", duree=3000):
    """Affiche un message temporaire sur un label donné, avec une couleur et une durée spécifiées."""
    label.configure(text=message, text_color=couleur)
    label.after(duree, lambda: label.configure(text=""))

