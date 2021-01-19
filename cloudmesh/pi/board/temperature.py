from cloudmesh.pi.board.monitor import Monitor
from cloudmesh.common.console import Console


class Temperature(Monitor):

    def __init__(self):
        self.title = "Temperature"
        self.order = order = ['host', 'cpu', 'gpu', 'date']
        self.command = \
            'cat' \
            ' /sys/class/thermal/thermal_zone0/temp;' \
            ' /opt/vc/bin/vcgencmd measure_temp | sed \"s/[^0-9.]//g\"'
        self.display = ['cpu', 'gpu']
        self.color = {
            'cpu': 'C0',
            'gpu': 'C2'}

    def update(self, entry, table=None):
        try:
            cpu, gpu = entry["stdout"].splitlines()
            entry["gpu"] = float(gpu)
            entry["cpu"] = float(cpu) / 1000.0
        except Exception as e:
            Console.error(str(e))
            entry["gpu"] = 0.0
            entry["cpu"] = 0.0
        return entry
