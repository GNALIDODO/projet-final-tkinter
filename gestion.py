import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire de Tâches")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Définir les couleurs et le style
        self.bg_color = "#f0f0f0"
        self.title_color = "#333333"
        self.accent_color = "#4a7abc"
        
        self.root.config(bg=self.bg_color)
        
        # Initialiser les tâches
        self.tasks = []
        self.load_tasks()
        
        # Créer les widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principale
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = tk.Label(
            main_frame, 
            text="Gestionnaire de Tâches",
            font=("Helvetica", 18, "bold"),
            fg=self.title_color,
            bg=self.bg_color,
            pady=10
        )
        title_label.pack()
        
        # Frame pour l'ajout de tâches
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Entrée de texte pour la nouvelle tâche
        self.task_entry = tk.Entry(
            input_frame, 
            font=("Helvetica", 12),
            width=40
        )
        self.task_entry.pack(side=tk.LEFT, padx=5)
        self.task_entry.bind("<Return>", lambda event: self.add_task())
        
        # Bouton pour ajouter une tâche
        add_button = tk.Button(
            input_frame,
            text="Ajouter Tâche",
            font=("Helvetica", 10),
            bg=self.accent_color,
            fg="white",
            padx=10,
            command=self.add_task
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
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