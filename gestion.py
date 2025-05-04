import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pickle
import os
from datetime import datetime

class Client:
    def __init__(self, code, etablissement, nom, localisation, contact, 
                 mensualite, montant_paye, periode, agent, observation):
        self.code = code
        self.etablissement = etablissement
        self.nom = nom
        self.localisation = localisation
        self.contact = contact
        self.mensualite = mensualite
        self.montant_paye = montant_paye
        self.periode = periode
        self.agent = agent
        self.observation = observation
        self.date_ajout = datetime.now().strftime("%Y-%m-%d")

class BuridaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BURIDA - Gestion de Clients")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        self.clients = []
        self.current_selection = None
        self.filename = "burida_clients.pkl"
        
        # Charger les données si le fichier existe
        self.charger_donnees()
        
        # Créer les onglets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet principal - Liste des clients
        self.tab_liste = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_liste, text="Liste des Clients")
        
        # Onglet statistiques
        self.tab_stats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text="Statistiques")
        
        # Configuration des widgets dans l'onglet liste
        self.configurer_onglet_liste()
        
        # Configuration des widgets dans l'onglet statistiques
        self.configurer_onglet_stats()
        
        # Remplir le tableau
        self.rafraichir_tableau()
    
    def configurer_onglet_liste(self):
        # Frame pour les boutons
        frame_boutons = tk.Frame(self.tab_liste, bg="#f0f0f0")
        frame_boutons.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Boutons CRUD
        boutons = [
            ("Ajouter", self.ajouter_client, "#4CAF50"),
            ("Modifier", self.modifier_client, "#2196F3"),
            ("Supprimer", self.supprimer_client, "#F44336"),
            ("Rafraîchir", self.rafraichir_tableau, "#FF9800")
        ]
        
        for i, (texte, commande, couleur) in enumerate(boutons):
            btn = tk.Button(frame_boutons, text=texte, command=commande, 
                           bg=couleur, fg="white", font=("Arial", 10, "bold"),
                           width=10, height=1)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Frame pour la recherche
        frame_recherche = tk.Frame(frame_boutons, bg="#f0f0f0")
        frame_recherche.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(frame_recherche, text="Rechercher:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.recherche_var = tk.StringVar()
        self.recherche_var.trace("w", lambda name, index, mode: self.rechercher())
        entry_recherche = tk.Entry(frame_recherche, textvariable=self.recherche_var, width=20)
        entry_recherche.pack(side=tk.LEFT, padx=5)
        
        # Frame pour le tableau
        frame_tableau = tk.Frame(self.tab_liste)
        frame_tableau.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tableau (Treeview)
        colonnes = [
            "code", "etablissement", "nom", "localisation", "contact", 
            "mensualite", "montant_paye", "periode", "agent", "observation", "date_ajout"
        ]
        
        self.tableau = ttk.Treeview(frame_tableau, columns=colonnes, show="headings")
        
        # Configurer les en-têtes de colonnes
        largeurs = {
            "code": 80, "etablissement": 150, "nom": 150, "localisation": 120, 
            "contact": 100, "mensualite": 100, "montant_paye": 100, "periode": 100, 
            "agent": 100, "observation": 150, "date_ajout": 100
        }
        
        titres = {
            "code": "Code", "etablissement": "Établissement", "nom": "Nom", 
            "localisation": "Localisation", "contact": "Contact", "mensualite": "Mensualité", 
            "montant_paye": "Montant Payé", "periode": "Période", "agent": "Agent", 
            "observation": "Observation", "date_ajout": "Date d'ajout"
        }
        
        for col in colonnes:
            self.tableau.heading(col, text=titres[col])
            self.tableau.column(col, width=largeurs[col], anchor=tk.W)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tableau, orient=tk.VERTICAL, command=self.tableau.yview)
        scrollbar_x = ttk.Scrollbar(frame_tableau, orient=tk.HORIZONTAL, command=self.tableau.xview)
        self.tableau.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Placement des éléments
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tableau.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Événement de sélection
        self.tableau.bind("<<TreeviewSelect>>", self.selection_item)
    
    def configurer_onglet_stats(self):
        # Frame principale pour les statistiques
        main_frame = tk.Frame(self.tab_stats, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        tk.Label(main_frame, text="Statistiques et Résumé", 
               font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        
        # Frame pour les cartes de statistiques
        cards_frame = tk.Frame(main_frame, bg="#f0f0f0")
        cards_frame.pack(fill=tk.X, pady=10)
        
        # Créer 4 cartes de statistiques
        stats_cards = [
            ("Nombre total de clients", "total_clients", "#3498db"),
            ("Montant total perçu", "total_montant", "#2ecc71"),
            ("Clients à jour", "clients_a_jour", "#27ae60"),
            ("Clients en retard", "clients_retard", "#e74c3c")
        ]
        
        for i, (titre, tag, couleur) in enumerate(stats_cards):
            card = tk.Frame(cards_frame, bg=couleur, bd=1, relief=tk.RAISED)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
            
            tk.Label(card, text=titre, font=("Arial", 12), 
                   bg=couleur, fg="white").pack(pady=5)
            
            valeur = tk.Label(card, text="0", font=("Arial", 20, "bold"), 
                            bg=couleur, fg="white")
            valeur.pack(pady=10)
            setattr(self, f"lbl_{tag}", valeur)
        
        # Frame pour les statistiques par période
        periode_frame = tk.Frame(main_frame, bg="white", bd=1, relief=tk.RAISED)
        periode_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(periode_frame, text="Répartition par Agent", 
               font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Tableau de statistiques par agent
        colonnes_agent = ["agent", "nb_clients", "montant_total"]
        self.tableau_agents = ttk.Treeview(periode_frame, columns=colonnes_agent, show="headings", height=5)
        
        for col, largeur, titre in zip(colonnes_agent, [150, 100, 150], 
                                     ["Agent", "Nombre de clients", "Montant total"]):
            self.tableau_agents.heading(col, text=titre)
            self.tableau_agents.column(col, width=largeur, anchor=tk.CENTER)
        
        self.tableau_agents.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton pour rafraîchir les statistiques
        tk.Button(main_frame, text="Rafraîchir les statistiques", 
                command=self.calculer_statistiques, bg="#3498db", fg="white", 
                font=("Arial", 10, "bold")).pack(pady=10)
    
    def calculer_statistiques(self):
        """Calcule et affiche les statistiques"""
        if not self.clients:
            return
        
        # Statistiques générales
        total_clients = len(self.clients)
        total_montant = sum(float(client.montant_paye) for client in self.clients)
        
        # On suppose qu'un client est à jour si montant_paye >= mensualite
        clients_a_jour = sum(1 for client in self.clients 
                             if float(client.montant_paye) >= float(client.mensualite))
        clients_retard = total_clients - clients_a_jour
        
        # Mettre à jour les labels
        self.lbl_total_clients.config(text=str(total_clients))
        self.lbl_total_montant.config(text=f"{total_montant:,.2f}")
        self.lbl_clients_a_jour.config(text=str(clients_a_jour))
        self.lbl_clients_retard.config(text=str(clients_retard))
        
        # Statistiques par agent
        stats_agents = {}
        for client in self.clients:
            agent = client.agent
            if agent not in stats_agents:
                stats_agents[agent] = {"nb_clients": 0, "montant_total": 0}
            
            stats_agents[agent]["nb_clients"] += 1
            stats_agents[agent]["montant_total"] += float(client.montant_paye)
        
        # Vider le tableau des agents
        for item in self.tableau_agents.get_children():
            self.tableau_agents.delete(item)
        
        # Remplir le tableau des agents
        for agent, stats in stats_agents.items():
            self.tableau_agents.insert("", tk.END, values=(
                agent, 
                stats["nb_clients"],
                f"{stats['montant_total']:,.2f}"
            ))
    
    def selection_item(self, event):
        """Gère la sélection d'un élément dans le tableau"""
        selected_items = self.tableau.selection()
        if selected_items:
            item_id = selected_items[0]
            item_index = self.tableau.index(item_id)
            self.current_selection = item_index
        else:
            self.current_selection = None
    
    def rafraichir_tableau(self):
        """Rafraîchit l'affichage du tableau"""
        # Effacer toutes les lignes actuelles
        for item in self.tableau.get_children():
            self.tableau.delete(item)
        
        # Ajouter les clients à la liste
        for client in self.clients:
            self.tableau.insert("", tk.END, values=(
                client.code,
                client.etablissement,
                client.nom,
                client.localisation,
                client.contact,
                client.mensualite,
                client.montant_paye,
                client.periode,
                client.agent,
                client.observation,
                client.date_ajout
            ))
        
        # Mettre à jour les statistiques
        self.calculer_statistiques()
    
    def rechercher(self):
        """Recherche dans le tableau"""
        recherche = self.recherche_var.get().lower()
        
        # Effacer toutes les lignes actuelles
        for item in self.tableau.get_children():
            self.tableau.delete(item)
        
        # Filtrer et ajouter les clients correspondants
        for client in self.clients:
            if (recherche in client.code.lower() or 
                recherche in client.etablissement.lower() or 
                recherche in client.nom.lower() or
                recherche in client.localisation.lower() or
                recherche in client.contact.lower() or
                recherche in client.agent.lower()):
                
                self.tableau.insert("", tk.END, values=(
                    client.code,
                    client.etablissement,
                    client.nom,
                    client.localisation,
                    client.contact,
                    client.mensualite,
                    client.montant_paye,
                    client.periode,
                    client.agent,
                    client.observation,
                    client.date_ajout
                ))
    
    def ajouter_client(self):
        """Ouvre une fenêtre pour ajouter un nouveau client"""
        self.fenetre_client("Ajouter un client")
    
    def modifier_client(self):
        """Modifie le client sélectionné"""
        if self.current_selection is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un client à modifier.")
            return
        
        client = self.clients[self.current_selection]
        self.fenetre_client("Modifier un client", client)
    
    def supprimer_client(self):
        """Supprime le client sélectionné"""
        if self.current_selection is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un client à supprimer.")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce client ?"):
            del self.clients[self.current_selection]
            self.sauvegarder_donnees()
            self.rafraichir_tableau()
            self.current_selection = None
    
    def fenetre_client(self, titre, client=None):
        """Fenêtre pour ajouter ou modifier un client"""
        # Créer une nouvelle fenêtre
        fenetre = tk.Toplevel(self.root)
        fenetre.title(titre)
        fenetre.geometry("600x600")
        fenetre.configure(bg="#f0f0f0")
        fenetre.transient(self.root)
        fenetre.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(fenetre, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        tk.Label(main_frame, text=titre, font=("Arial", 16, "bold"), 
               bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=10)
        
        # Champs de formulaire
        champs = [
            ("Code:", "code"),
            ("Établissement:", "etablissement"),
            ("Nom:", "nom"),
            ("Localisation:", "localisation"),
            ("Contact:", "contact"),
            ("Mensualité:", "mensualite"),
            ("Montant payé:", "montant_paye"),
            ("Période:", "periode"),
            ("Agent:", "agent"),
            ("Observation:", "observation")
        ]
        
        # Variables pour stocker les valeurs
        variables = {}
        
        # Créer les champs de formulaire
        for i, (label_text, field_name) in enumerate(champs):
            tk.Label(main_frame, text=label_text, bg="#f0f0f0", 
                   anchor=tk.E).grid(row=i+1, column=0, padx=10, pady=5, sticky=tk.E)
            
            var = tk.StringVar()
            variables[field_name] = var
            
            # Définir la valeur initiale si on modifie un client existant
            if client:
                var.set(getattr(client, field_name))
            
            # Pour l'observation, utiliser un Text au lieu d'un Entry
            if field_name == "observation":
                entry = tk.Text(main_frame, width=30, height=4)
                entry.grid(row=i+1, column=1, padx=10, pady=5, sticky=tk.W)
                if client:
                    entry.insert("1.0", client.observation)
                variables[field_name] = entry  # Remplacer la variable StringVar par le widget Text
            else:
                entry = tk.Entry(main_frame, textvariable=var, width=30)
                entry.grid(row=i+1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Boutons
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.grid(row=len(champs)+1, column=0, columnspan=2, pady=20)
        
        # Fonction pour sauvegarder les données du formulaire
        def sauvegarder():
            # Vérifier que les champs obligatoires sont remplis
            for field_name in ["code", "etablissement", "nom"]:
                if not variables[field_name].get().strip():
                    messagebox.showwarning("Attention", f"Le champ {field_name} est obligatoire.")
                    return
            
            # Récupérer les valeurs du formulaire
            values = {}
            for field_name, var in variables.items():
                if field_name == "observation":
                    values[field_name] = var.get("1.0", tk.END).strip()
                else:
                    values[field_name] = var.get()
            
            # Créer ou modifier le client
            if client:
                for field_name, value in values.items():
                    setattr(client, field_name, value)
            else:
                nouveau_client = Client(**values)
                self.clients.append(nouveau_client)
            
            # Sauvegarder les données et rafraîchir l'affichage
            self.sauvegarder_donnees()
            self.rafraichir_tableau()
            fenetre.destroy()
        
        # Boutons d'action
        tk.Button(buttons_frame, text="Annuler", command=fenetre.destroy, 
                bg="#f44336", fg="white", width=10).pack(side=tk.LEFT, padx=10)
        
        tk.Button(buttons_frame, text="Enregistrer", command=sauvegarder, 
                bg="#4caf50", fg="white", width=10).pack(side=tk.LEFT, padx=10)

    def sauvegarder_donnees(self):
        """Sauvegarde les données dans un fichier"""
        with open(self.filename, 'wb') as fichier:
            pickle.dump(self.clients, fichier)
        messagebox.showinfo("Succès", "Les données ont été enregistrées avec succès.")
    
    def charger_donnees(self):
        """Charge les données depuis un fichier"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as fichier:
                    self.clients = pickle.load(fichier)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger les données: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BuridaApp(root)
    root.mainloop()
       
        
      .LEFT, padx=5)
        
        # Frame pour la liste des tâches
        tasks_frame = tk.Frame(main_frame, bg=self.bg_color)
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Créer un cadre avec scrollbar
        task_scroll = tk.Scrollbar(tasks_frame)
        task_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Liste des tâches
        self.task_listbox = tk.Listbox(
            tasks_frame,
            font=("Helvetica", 12),
            selectbackground=self.accent_color,
            selectmode=tk.SINGLE,
            height=15,
            width=50
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurer la scrollbar
        task_scroll.config(command=self.task_listbox.yview)
        self.task_listbox.config(yscrollcommand=task_scroll.set)
        
        # Mettre à jour la liste des tâches
        self.update_task_list()
        
        # Frame pour les boutons d'action
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Boutons d'action
        complete_button = tk.Button(
            button_frame,
            text="Marquer comme Terminé",
            font=("Helvetica", 10),
            bg="#5cb85c",
            fg="white",
            padx=10,
            command=self.complete_task
        )
        complete_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(
            button_frame,
            text="Supprimer Tâche",
            font=("Helvetica", 10),
            bg="#d9534f",
            fg="white",
            padx=10,
            command=self.delete_task
        )
        delete_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(
            button_frame,
            text="Effacer Tout",
            font=("Helvetica", 10),
            bg="#f0ad4e",
            fg="white",
            padx=10,
            command=self.clear_all_tasks
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append({"text": task, "completed": False})
            self.update_task_list()
            self.save_tasks()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Attention", "Veuillez entrer une tâche.")
    
    def delete_task(self):
        try:
            index = self.task_listbox.curselection()[0]
            self.tasks.pop(index)
            self.update_task_list()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à supprimer.")
    
    def complete_task(self):
        try:
            index = self.task_listbox.curselection()[0]
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.update_task_list()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à marquer comme terminée.")
    
    def clear_all_tasks(self):
        confirm = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer toutes les tâches?")
        if confirm:
            self.tasks = []
            self.update_task_list()
            self.save_tasks()
    
    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            task_text = task["text"]
            if task["completed"]:
                task_text = "✓ " + task_text
            else:
                task_text = "○ " + task_text
            self.task_listbox.insert(tk.END, task_text)
    
    def save_tasks(self):
        with open("tasks.pickle", "wb") as file:
            pickle.dump(self.tasks, file)
    
    def load_tasks(self):
        try:
            with open("tasks.pickle", "rb") as file:
                self.tasks = pickle.load(file)
        except (FileNotFoundError, EOFError):
            # Si le fichier n'existe pas ou est vide, on initialise une liste vide
            self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
