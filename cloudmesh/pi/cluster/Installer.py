import glob
import os
import textwrap
from pydoc import locate

import cloudmesh.pi.cluster
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import banner
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


class Script(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        dict.__setitem__(self,
                         key,
                         textwrap.dedent(value))

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        return value

    def execute(self, arguments):

        def Service():
            mod = arguments.SERVICE
            cls = mod.capitalize()
            imp = f'cloudmesh.pi.cluster.{mod}.{mod}.{cls}'
            _Service = locate(imp)
            service = _Service()
            return service

        if arguments.list and arguments.SERVICE and arguments.NAMES:
            print(arguments.NAMES)

        if arguments.list and arguments.SERVICE:

            VERBOSE(arguments)

            service = Service()

            print()
            print(f"Scripts for {arguments.SERVICE}")
            print()
            if not arguments.details:
                for script in service.script:
                    print("    *", script)
                print()
            else:
                for name in service.script:
                    banner(name)
                    print(service.script[name].strip())
                print()
                print("details")

        elif arguments.list:

            print()
            print(f"Deployment Services")
            print()

            directory = os.path.dirname(cloudmesh.pi.cluster.__file__)
            entries = glob.glob(f"{directory}/*")
            for entry in entries:
                if os.path.isdir(entry):
                    entry = os.path.basename(entry)
                    if not entry.startswith("_"):
                        print("   *", entry)

            print()


class Installer:

    @staticmethod
    def comment(label, allign=None):
        if allign == 'top':
            script = textwrap.dedent("""

                # ################################################
                # {label} BEGIN
                #
                """)
        elif allign == 'bottom':
            script = textwrap.dedent("""
                #
                # {label} END
                # ################################################
                """)
        else:
            script = textwrap.dedent("""

                # ################################################
                # {label} 
                # ################################################
                """)

        return script

    @staticmethod
    def add_line(script, line):
        """
        Adds a line to a script if it dos not alreadi is in it

        :param script:
        :param line:
        :return:
        """
        if line.startswith("#") or \
                line == "\n" or \
                line not in script:
            script += line + "\n"
        return script

    @staticmethod
    def add_script(filename, script):
        """
        adds all the lines of the script to the filename, if the line of
        the script does not already exist. It is useful to add lines to for
        example the .bashrc script

        :param filename:
        :param script:
        :return:
        """
        script = readfile(filename)
        for line in script:
            script = Installer.add_line(script, line)

        writefile(filename, script)
