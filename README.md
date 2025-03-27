# Seahawks Harvester - Documentation pour les techniciens

## Fonctionnalités principales
1. **Scan du réseau** : Cliquez sur "Scan Network" pour lancer un scan du réseau local. Les résultats seront affichés dans la zone de texte.
2. **Vérification des mises à jour** : Cliquez sur "Check Updates" pour vérifier si une nouvelle version de l'application est disponible.
3. **Affichage des informations système** : L'adresse IP locale, le nom de la VM et le nombre de machines connectées sont affichés en temps réel.

## Installation (et deploiement sur vmware : compatible avec windows , macOs ,linux )
1. Clonez le dépôt GitHub :
   ```bash
   git clone https://github.com/HANIFSTEPHAN/Seahawks-Harvester-Nester.git

2. cd Seahawks-Harvester-Nester
3. git branch -a 
4. git pull origin 

### pour installer les dependances dans requirements.txt
1. Crée un environnement virtuel
   
   python -m venv venv  
   
   Sur macOS/Linux: source venv/bin/activate  
   Sur Windows: venv\Scripts\activate  

2. Installer  les dépendances 
   
   pip install -r requirements.txt

### A noter  
## Configuration
Avant d'utiliser l'application, vous devez configurer l'URL du serveur Nester :

1. Ouvrez le fichier `main.py`
2. Localisez la ligne suivante :
   ```python
   self.nester_client = NesterClient("http://172.20.10.2:5000")  # URL du serveur Nester
3. Remplacez http://172.20.10.2:5000 par l'URL de votre propre serveur Nester
4. Sauvegardez le fichier