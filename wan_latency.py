from ping3 import ping

class WanLatency:
    def __init__(self, target="google.com"):
        self.target = target

    def measure_latency(self):
        try:
            latency = ping(self.target, unit="ms")
            if latency is not None and latency > 0:
                return f"WAN Latency: {latency:.2f} ms"
            else:
                return "WAN Latency: Unable to measure"
        except Exception as e:
            return f"Error measuring latency: {e}"