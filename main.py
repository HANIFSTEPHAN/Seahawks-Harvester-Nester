import tkinter as tk
from tkinter import scrolledtext, ttk
from system_info import SystemInfo
from network_scanner import NetworkScanner
from wan_latency import WanLatency
from update_checker import UpdateChecker
from nester_client import NesterClient  
import threading
import customtkinter as ctk
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class SeahawksHarvesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Seahawks Harvester - CyberScan Pro")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.version = "1.1.0"

        # Configuration des styles
        self._setup_styles()

        # Initialisation des modules
        self.system_info = SystemInfo()
        self.network_scanner = NetworkScanner()
        self.wan_latency = WanLatency()
        self.update_checker = UpdateChecker(self.version)
        self.nester_client = NesterClient("http://192.168.11.135:5000")  # URL du serveur Nester

        # Construction de l'interface
        self._build_ui()
        self.display_system_info()

    def _setup_styles(self):
        self.font_primary = ("Roboto Medium", 14)
        self.font_title = ("Roboto Black", 24)
        self.font_monospace = ("Consolas", 12)
        self.accent_color = "#2A9D8F"
        self.dark_bg = "#1A1A2E"
        self.light_text = "#E6E6FA"

    def _build_ui(self):
        # Configuration de la grille principale
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panneau latéral
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Titre
        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="CYBERSCAN PRO",
            font=("Roboto Black", 20),
            text_color=self.accent_color
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20)

        # Informations système
        self.sys_info_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sys_info_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        sys_info_labels = [
            ("IP Address", "ip_label"),
            ("Hostname", "hostname_label"),
            ("Version", "version_label"),
            ("Connected Devices", "connected_devices_label")
        ]

        for idx, (text, var) in enumerate(sys_info_labels):
            label = ctk.CTkLabel(
                self.sys_info_frame,
                text=text + ":",
                font=self.font_primary,
                anchor="w"
            )
            label.grid(row=idx, column=0, padx=5, pady=5, sticky="w")

            setattr(self, var, ctk.CTkLabel(
                self.sys_info_frame,
                text="",
                font=(self.font_monospace[0], self.font_primary[1]),
                text_color=self.accent_color
            ))
            getattr(self, var).grid(row=idx, column=1, padx=5, pady=5, sticky="w")

        # Boutons
        self.scan_button = ctk.CTkButton(
            self.sidebar,
            text="Scan Network",
            command=self.scan_network,
            fg_color=self.accent_color,
            hover_color="#264653",
            font=self.font_primary
        )
        self.scan_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.update_button = ctk.CTkButton(
            self.sidebar,
            text="Check Updates",
            command=self.check_for_updates,
            font=self.font_primary
        )
        self.update_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Bouton pour envoyer les données au Nester
        self.send_data_button = ctk.CTkButton(
            self.sidebar,
            text="Send Data to Nester",
            command=self.send_data_to_nester,
            fg_color="#E76F51",
            hover_color="#D45A3D",
            font=self.font_primary
        )
        self.send_data_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Zone principale
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Tableau de bord
        self.dashboard_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Section pour les résultats du scan
        self.scan_results_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.scan_results_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.scan_results_label = ctk.CTkLabel(
            self.scan_results_frame,
            text="Scan Results:",
            font=self.font_title,
            text_color=self.accent_color
        )
        self.scan_results_label.grid(row=0, column=0, sticky="w")

        self.scan_results_text = scrolledtext.ScrolledText(
            self.scan_results_frame,
            wrap=tk.WORD,
            font=self.font_monospace,
            bg=self.dark_bg,
            fg=self.light_text,
            insertbackground="white",
            padx=10,
            pady=10,
            width=80,
            height=15
        )
        self.scan_results_text.grid(row=1, column=0, sticky="nsew")

        # Section pour la latence WAN
        self.latency_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.latency_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.latency_label = ctk.CTkLabel(
            self.latency_frame,
            text="WAN Latency:",
            font=self.font_title,
            text_color=self.accent_color
        )
        self.latency_label.grid(row=0, column=0, sticky="w")

        self.latency_text = ctk.CTkLabel(
            self.latency_frame,
            text="Not measured yet",
            font=self.font_monospace,
            text_color=self.light_text
        )
        self.latency_text.grid(row=1, column=0, sticky="w")

        # Barre de statut
        self.status_bar = ctk.CTkLabel(
            self,
            text=" Ready",
            anchor="w",
            font=("Roboto", 12),
            text_color="#888888",
            fg_color="#000000"
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def display_system_info(self):
        info = self.system_info.get_system_info()
        self.ip_label.configure(text=info['Local IP Address'])
        self.hostname_label.configure(text=info['VM Name'])
        self.version_label.configure(text=self.version)

    def scan_network(self):
        self.scan_results_text.delete(1.0, tk.END)
        self.status_bar.configure(text=" Scanning network...")
        threading.Thread(target=self._perform_scan, daemon=True).start()

    def _perform_scan(self):
        try:
            self.after(0, lambda: self.scan_results_text.insert(tk.END, "Initializing cyber scan...\n"))
            scan_results = self.network_scanner.scan_network()

            # Vérification et affichage du nombre de machines connectées
            connected_devices = len(self.network_scanner.nm.all_hosts())
            self.after(0, lambda: self.connected_devices_label.configure(text=str(connected_devices)))

            self.after(0, lambda: self.scan_results_text.insert(tk.END, "\n[+] Network scan results:\n"))
            self.after(0, lambda: self.scan_results_text.insert(tk.END, "-"*50 + "\n"))
            for result in scan_results:
                self.after(0, lambda r=result: self.scan_results_text.insert(tk.END, f"• {r}\n"))

            self.after(0, lambda: self.scan_results_text.insert(tk.END, "\n[+] Measuring WAN latency...\n"))
            latency = self.wan_latency.measure_latency()
            self.after(0, lambda: self.latency_text.configure(text=f"Latency: {latency}"))
            self.after(0, lambda: self.scan_results_text.insert(tk.END, f"\nLatency results: {latency}\n"))

            self.after(0, lambda: self.status_bar.configure(text=" Scan completed"))
        except Exception as e:
            self.after(0, lambda: self.scan_results_text.insert(tk.END, f"\n[!] ERROR: {str(e)}\n"))
            self.after(0, lambda: self.status_bar.configure(text=" Scan failed"))
            messagebox.showerror("Scan Error", str(e))

    def check_for_updates(self):
        update_info = self.update_checker.check_for_updates()
        if "A new version" in update_info:
            user_response = messagebox.askyesno("Update Available", update_info + "\nDo you want to update now?")
            if user_response:
                self.update_checker.update_application()
        else:
            messagebox.showinfo("Update Check", update_info)
    def send_data_to_nester(self):
         """Envoie les données collectées au serveur Nester."""
         data = {
            "ip_address": self.ip_label.cget("text"),
            "hostname": self.hostname_label.cget("text"),
            "status": "En ligne",  # Exemple de statut
            "connected_devices": self.connected_devices_label.cget("text"),
            "scan_results": self.scan_results_text.get(1.0, tk.END),
            "wan_latency": self.latency_text.cget("text")
            }   

         result = self.nester_client.send_harvester_data(data)
         messagebox.showinfo("Data Sent", result)


if __name__ == "__main__":
    app = SeahawksHarvesterApp()
    app.mainloop()