import requests
import subprocess
import os
import sys

class UpdateChecker:
    def __init__(self, current_version="1.1.0"):
        self.current_version = current_version
        self.repo_url = "https://api.github.com/repos/HANIFSTEPHAN/APP-harvester/releases/latest"
    
    def check_for_updates(self):
        try:
            response = requests.get(self.repo_url)
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release["tag_name"]
                
                if latest_version != self.current_version:
                    return f"A new version ({latest_version}) is available!"
                else:
                    return "You are using the latest version."
            else:
                return "Unable to check for updates: Connection issue."
        except Exception as e:
            return f"Unable to check for updates: {e}"

    def update_application(self):
        try:
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            return f"Error during update: {e}"