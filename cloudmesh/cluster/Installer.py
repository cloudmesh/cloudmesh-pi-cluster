from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.debug import VERBOSE
import textwrap
from pydoc import locate
from pprint import pprint
from cloudmesh.common.console import Console

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

        if arguments.list and arguments.SERVICE and arguments.NAMES:

            print (arguments.NAMES)

        if arguments.list and arguments.SERVICE:

            mod = arguments.SERVICE
            cls = mod.capitalize()
            imp = f'cloudmesh.cluster.{mod}.{mod}.{cls}'
            Service = locate(imp)
            service = Service()

            print()
            print(f"Scripts for {mod}")
            print()
            for script in service.script:
                print ("    *", script)
            print()

        elif arguments.list:
            print ("list")

class Installer:


    @staticmethod
    def comment(label, allign=None):
        if allign =='top':
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

        adds all the lines of the script to the filename, if the line of the script
        does not already exist. It is useful to add lines to for example the .bashrc
        script

        :param filename:
        :param script:
        :return:
        """
        script = readfile(filename)
        for line in script:
           script = Installer.add_line(script, line)

        writefile (filename, script)

