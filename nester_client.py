import requests
import json

class NesterClient:
    def __init__(self, nester_url):
        self.nester_url = nester_url

    def send_harvester_data(self, data):
        """Envoie les données du Harvester au serveur Nester."""
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{self.nester_url}/api/harvester/data", data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                return "Data sent successfully!"
            else:
                return f"Failed to send data: {response.status_code}"
        except Exception as e:
            return f"Error sending data: {e}"