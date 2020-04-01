from cloudmesh.pi.board.monitor import Monitor


class Temperature(Monitor):

    def __init__(self):
        self.title = "Temperature"
        self.order = order = ['host', 'cpu', 'gpu', 'date']
        self.command = "cat" \
                       " /sys/class/thermal/thermal_zone0/temp;" \
                       " /opt/vc/bin/vcgencmd measure_temp"
        self.display = ['cpu', 'gpu']
        self.color = {
            'cpu': 'C0',
            'gpu': 'C2'}

    def update(self, entry, table=None):
        cpu, gpu = entry["stdout"].splitlines()
        entry["gpu"] = float(gpu.split("=", 1)[1][:-2])
        entry["cpu"] = float(cpu) / 1000.0
        return entry
