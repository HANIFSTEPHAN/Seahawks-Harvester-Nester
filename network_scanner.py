import nmap
import socket
import netifaces

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def get_main_interface(self):
        """Détecte l'interface réseau principale utilisée pour accéder à Internet."""
        EXCLUDED_PREFIXES = ("lo", "vmnet", "virbr", "vboxnet", "tun", "docker", "br")

        try:
            # On se connecte à 8.8.8.8 pour trouver l'interface utilisée
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google DNS (ne fait pas réellement de connexion)
            main_ip = s.getsockname()[0]  # Récupère l'IP utilisée pour la connexion
            s.close()

            # On cherche quelle interface possède cette IP
            for iface in netifaces.interfaces():
                if iface.startswith(EXCLUDED_PREFIXES):
                    continue  # On ignore les interfaces virtuelles

                addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
                if addrs:
                    for addr in addrs:
                        if addr['addr'] == main_ip:  # Vérifie si l'IP correspond
                            return iface, addr['addr'], addr.get('netmask')

        except Exception as e:
            print(f"Erreur lors de la détection de l'interface principale : {e}")
        return None, None, None

    def get_network_range(self):
        """Calcule la plage réseau à partir de l'interface principale."""
        iface, ip, netmask = self.get_main_interface()
        if not iface or not ip or not netmask:
            return None

        try:
            # Convertir le masque en notation CIDR
            cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))
            return f"{ip}/{cidr}"
        except Exception as e:
            print(f"Erreur lors du calcul du réseau : {e}")
        return None

    def scan_network(self):
        """Scanne automatiquement le réseau local et retourne les résultats."""
        try:
            network_range = self.get_network_range()
            if not network_range:
                return ["Impossible de déterminer la plage réseau."]
            
            print(f"Scanning network: {network_range}")
            self.nm.scan(hosts=network_range, arguments='-n -sV')
            results = []
            
            for host in self.nm.all_hosts():
                try:
                    hostname = socket.gethostbyaddr(host)[0]
                except socket.herror:
                    hostname = "Inconnu"
                
                machine_info = f"Machine: {host} ({hostname})"
                if 'tcp' in self.nm[host]:
                    machine_info += "\n  Ports ouverts:"
                    for port in self.nm[host]['tcp']:
                        service_name = self.nm[host]['tcp'][port]['name']
                        machine_info += f"\n    - Port {port}: {service_name}"
                results.append(machine_info)
            return results
        except Exception as e:
            return [f"Erreur pendant le scan : {e}"]

