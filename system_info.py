import socket

class SystemInfo:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip_address = socket.gethostbyname(self.hostname)

    def get_system_info(self):
        return {
            "Local IP Address": self.ip_address,
            "VM Name": self.hostname
        }