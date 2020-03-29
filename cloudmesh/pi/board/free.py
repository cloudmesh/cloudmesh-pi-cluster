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

    temp_min = 150.0
    temp_max = 0.0


    temp_min = 150.0
    temp_max = 0.0

    def __init__(self):
        self.order = order=['host',
                         'mem.total', 'mem.used', 'mem.free', 'mem.shared',
                         'mem.cache', 'mem.avail',
                         'swap.total', 'swap.used', 'swap.free',
                         ]
        self.command = "free -b"

    def update(self, entry):
        header, mem, swap = entry["stdout"].splitlines()
        entry['mem.total'], \
        entry['mem.used'], \
        entry['mem.free'], \
        entry['mem.shared'], \
        entry['mem.cache'], \
        entry['mem.avail'] = [humanize.naturalsize(v) for v in mem.split()[1:7]]
        entry['swap.total'], \
        entry['swap.used'], \
        entry['swap.free'] = [humanize.naturalsize(v) for v in
                              swap.split()[1:4]]
        return entry

