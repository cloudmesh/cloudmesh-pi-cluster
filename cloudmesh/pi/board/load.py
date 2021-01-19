from cloudmesh.pi.board.monitor import Monitor


class Load(Monitor):

    def __init__(self):
        self.title = "Load"
        self.order = order = [
            'host',
            '1', '5', '10',
            'proc.running', 'proc.total'
        ]
        self.command = "cat /proc/loadavg"
        self.display = ['1', '5', '10']
        self.color = {
            '1': 'C0',
            '5': 'C2',
            '10': 'C7',
        }

    def update(self, entry, table=None):
        entry['1'], \
        entry['5'], \
        entry['10'], \
        procs, \
        entry['last.pid'] = entry["stdout"].split()
        entry['proc.running'], entry['proc.total'] = [int(x) for x in
                                                      procs.split("/")]
        for a in '1', '5', '10':
            entry[a] = float(entry[a])
        return entry
