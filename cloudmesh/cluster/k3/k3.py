#
# Lesson: develop portable installers
#
# Here we explain how to start developping portable installers.
#
# Ofetn we find on the internet installers that require a great deal of doing
# things by hand. However if we have to set this up multiple times we have to do
# a lot of work and it is not sustainable.
#
# We could use tools such as ansible, chef or others DevOps tools, but often
# thsi si not needed and we still need to have programs that integrate int them
#
# So let us develop such a littel helper application and use the install of k3d
# as an example. Your  tasks is it to complete the example and develop a fully
# functionng k3 installer.
#
# We envision a single commandline such as
#
# cms pi k3 install --master=red --worker[01-03]
#
# THis command should maintain its status and be callable multiple times to skip
# installs we als add a flgg such as
#
# cms pi k3 install --master=red --worker[01-03] --install=red02
#
# Meaning overall we like to have a clusetr with master and workers, but in this
# command we only deal with the install of node red002. However this node may
# need information from the master and workers to complete, so we put it in the
# commandline otions also. If the install is ommitted, the install is conducted
# on all nodes.
#
# We also want to add the feature of a step wise install
#
# cms pi k3 install --master=red --worker[01-03] --install=red02
#                   --step=enable_containers
#
# How do weget there?
#
# Let us look at teh seemingly simple description to add a line to a file.
#
# This can be comletely automated and we provide here a simple start (not yet
# tested or verified) of this
#
# As you can see we did not just blindly implement the single task, but we
# detected that adding aline culd be useful to other projects, so we create a
# generalized helper function that we coudl reuse in other projects.
#
# Please remember that cloudmesh has a parallel execution framework for using
# ssh on remote machines
#
# cloudmesh.host.Host.ssh
#
# please learn about it as we in the second step can use this to run things in
# parallel on multiple hosts
#
# So lets get that example started:
#

from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.console import Console

import os

#
# this is just a draft
#

class Installer:

    @staticmethod
    def add_to_file(self, filename, line, warning=None):
        """
        adds a line to  a file if it is not already in it

        :return:
        """
        lines = readfile(filename)
        if line in lines:
            Console.warning(warning)
            return
        else:
            lines += f"\n{line}\n"
            writefile(filename, lines)

    def reboot(self):
        os.system("shutdown -r now")


class k3(Installer):

    def enable_containers(self, filename="/boot/cmdline.txt"):
        command = "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory"
        self.add_to_file(filename, command)


if __name__ == "__main__":
    # create an example
    filename = "/boot/cmdline.txt"
    os.system(f"cp {filename} tmp.txt")
    k3.enable_containers(filename=filename)
    os.system(f"cat {filename}")
    # k3.reboot()
