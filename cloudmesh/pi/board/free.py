import os
from cloudmesh.common.Host import Host
from pprint import pprint
import time
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Printer import Printer
import sys
import pygal
import webbrowser
from pygal.style import DefaultStyle
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import humanize
from cloudmesh.pi.board.monitor import Monitor


class Free(Monitor):

    def __init__(self):
        self.title = "Free"
        self.order = order = [
            'host',
            'mem.total', 'mem.used', 'mem.free', 'mem.shared',
            'mem.cache', 'mem.avail',
            'swap.total', 'swap.used', 'swap.free',
        ]
        self.command = "free -b"
        self.display = ['mem.used', 'swap.used']
        self.color = {
            'mem.used': 'C0',
            'swap.used': 'C2'}

    def update(self, entry, table=None):
        if not table:
            f = int
        else:
            f = humanize.naturalsize

        header, mem, swap = entry["stdout"].splitlines()
        # noinspection PyPep8
        entry['mem.total'], \
        entry['mem.used'], \
        entry['mem.free'], \
        entry['mem.shared'], \
        entry['mem.cache'], \
        entry['mem.avail'] = [f(v) for v in mem.split()[1:7]]
        # noinspection PyPep8
        entry['swap.total'], \
        entry['swap.used'], \
        entry['swap.free'] = [f(v) for v in swap.split()[1:4]]
        return entry
