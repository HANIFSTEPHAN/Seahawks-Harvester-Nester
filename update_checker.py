import requests
import tkinter.messagebox as messagebox
from packaging import version  # pip install packaging

class UpdateChecker:
    def __init__(self, current_version="1.2.0"):  # ← Mettez votre version actuelle
        self.current_version = current_version
        self.repo_api = "https://api.github.com/repos/HANIFSTEPHAN/Seahawks-Harvester-Nester/releases/latest"

    def check_for_updates(self):
        try:
            response = requests.get(self.repo_api)
            latest = response.json()
            latest_version = latest["tag_name"].lstrip("v")
            
            if version.parse(latest_version) > version.parse(self.current_version):
                messagebox.showinfo(
                    "Mise à jour disponible",
                    f"Version {latest_version} disponible !\n\n"
                    f"Téléchargez-la depuis :\n{latest['html_url']}",
                    parent=self.parent_window  # Garde votre fenêtre comme parent
                )
                return True
            return False
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de vérifier : {str(e)}")
            return False