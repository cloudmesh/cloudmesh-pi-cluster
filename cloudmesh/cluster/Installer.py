from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile

class Installer:

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

