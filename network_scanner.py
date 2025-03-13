import nmap
import socket
import netifaces

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def get_local_ip(self):
        """Récupère l'adresse IP locale de la machine."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception as e:
            print(f"Error retrieving local IP: {e}")
            return None

    def get_network_range(self):
        """Détermine automatiquement la plage réseau du LAN en fonction de l'adresse IP locale."""
        try:
            interfaces = netifaces.interfaces()
            for iface in interfaces:
                if netifaces.AF_INET in netifaces.ifaddresses(iface):
                    for addr in netifaces.ifaddresses(iface)[netifaces.AF_INET]:
                        ip = addr['addr']
                        netmask = addr['netmask']
                        
                        # Calcul de la plage réseau
                        cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
                        network_range = f"{ip}/{cidr}"
                        return network_range
        except Exception as e:
            print(f"Error retrieving network range: {e}")
        return None

    def scan_network(self):
        """Scanne automatiquement le réseau local et retourne les résultats."""
        try:
            network_range = self.get_network_range()
            if not network_range:
                return ["Unable to determine network range."]
            
            self.nm.scan(hosts=network_range, arguments='-n -sV')
            results = []
            
            for host in self.nm.all_hosts():
                try:
                    hostname = socket.gethostbyaddr(host)[0]
                except socket.herror:
                    hostname = "Unknown"
                
                machine_info = f"Machine: {host} ({hostname})"
                if 'tcp' in self.nm[host]:
                    machine_info += "\n  Open ports:"
                    for port in self.nm[host]['tcp']:
                        service_name = self.nm[host]['tcp'][port]['name']
                        machine_info += f"\n    - Port {port}: {service_name}"
                results.append(machine_info)
            return results
        except Exception as e:
            return [f"Error during scan: {e}"]