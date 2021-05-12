from cloudmesh.pi.cluster.k3.k3 import Installer
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.StopWatch import StopWatch

class MicroK8s(Installer):

    def __init__(self):
        pass

    def execute(self, arguments):
        """
        pi microk8s install snapd NAMES
        pi microk8s install NAMES
        pi microk8s uninstall NAMES
        pi microk8s start NAMES
        pi microk8s stop NAMES
        pi microk8s inspect NAMES
        pi microk8s enable addon ADDONS NAMES
        pi microk8s cluster info SERVER
        pi microk8s join NAMES SERVER
        pi microk8s get node SERVER
        pi microk8s remove node NAMES
        :param arguments:
        :return:
        """
        if arguments.NAMES:
            names = Parameter.expand(arguments.NAMES)

        if arguments.install and arguments.snapd:
            self.install_snapd(names)
        elif arguments.install:
            StopWatch.start("install")
            self.install(names)
            StopWatch.stop("install")
            StopWatch.status("install", True)
            StopWatch.print("install", "install")
        elif arguments.uninstall:
            StopWatch.start("uninstall")
            self.uninstall(names)
            StopWatch.stop("uninstall")
            StopWatch.status("uninstall", True)
            StopWatch.print("uninstall", "uninstall")
        elif arguments.start:
            self.start(names)
        elif arguments.stop:
            self.stop(names)
        elif arguments.inspect:
            self.inspect(names)
        elif arguments.enable and arguments.addon:
            self.enable_addon(arguments.ADDONS, names)
        elif arguments.cluster and arguments.info:
            self.cluster_info(arguments.SERVER)
        elif arguments.join:
            StopWatch.start("join")
            self.join_node(names, arguments.SERVER)
            StopWatch.stop("join")
            StopWatch.status("join", True)
            StopWatch.print("join", "join")
        elif arguments.remove and arguments.node:
            StopWatch.start("remove node")
            self.remove_node(names)
            StopWatch.stop("remove node")
            StopWatch.status("remove node", True)
            StopWatch.print("remove node", "remove node")
        elif arguments.get and arguments.node:
            # make sure this is last in the elif chain
            self.get_node(arguments.SERVER)

    def install_snapd(self, names):
        Console.info(f"Install snapd on {names}")
        command = "sudo apt update; sudo apt install snapd -y; " \
                  "sudo snap install core"
        self._run_and_print(command=command, names=names)

    def install(self, names):
        Console.info(f"Installing microk8s on {names}")
        Console.info("This may take a few minutes")
        command = "sudo snap install microk8s --classic"
        self._run_and_print(command=command, names=names)

    def uninstall(self, names):
        Console.info(f"Uninstalling microk8s on {names}")
        Console.info("This may take a few minutes")
        command = "sudo snap remove microk8s"
        self._run_and_print(command=command, names=names)

    def start(self, names):
        Console.info(f"Starting microk8s services on {names}")
        command = "microk8s.start"
        self._run_and_print(command=command, names=names)

    def stop(self, names):
        Console.info(f"Stopping microk8s services on {names}")
        command = "microk8s.stop"
        self._run_and_print(command=command, names=names)

    def inspect(self, names):
        Console.info(f"Inspecting microk8s services on {names}")
        command = "microk8s.inspect"
        self._run_and_print(command=command, names=names)

    def enable_addon(self, addons, names):
        addons = Parameter.expand(addons)
        addons = " ".join(addons)
        Console.info(f"Enabling addons {addons} on {names}")
        command = f"sudo microk8s.enable {addons}"
        self._run_and_print(command=command, names=names)

    def cluster_info(self, server):
        Console.info(f"Getting cluster info from server {server}")
        print()
        command = "sudo microk8s.kubectl cluster-info"
        results = Host.ssh(
            hosts=server,
            command=command
        )
        output = results[0]['stdout'].strip()
        print(output)

    def join_node(self, names, server):
        Console.info(f"Joining nodes {names} to server {server}")
        # has to be done sequentially
        #command = "sudo $(ssh white sudo microk8s.add-node | grep microk8s | head -1)"
        #self._run_and_print(command=command, names=names)

        for name in names:
            # This has to be sequantial as node.add generates a new token for
            # each call
            Console.info(f"Fetching unique join URL from {server} for each "
                         f"worker")
            command  = "sudo microk8s.add-node"
            results = Host.ssh(
                hosts=server,
                command=command
            )
            output = results[0]['stdout'].strip()

            for line in output.splitlines():
                if line.startswith("microk8s join"):
                    command = "sudo " + line
                    command = command.strip() + ' &'
                    print(f"Using join  command: {command}")
                    break

            Console.info(f"Joining {name} to the {server}")
            Console.info("This may take a few minutes")
            self._run_and_print(command=command, names=name)

    def get_node(self, server):
        Console.info(f"Getting node info from server {server}")
        command = "sudo microk8s.kubectl get node -o wide"
        results = Host.ssh(
            hosts=server,
            command=command
        )
        output = results[0]['stdout'].strip()
        print(output)

    def remove_node(self, names):
        Console.info(f"Removing nodes {names} from thier cluster")
        Console.info(f"This may take a few minutes")
        command = "sudo microk8s.leave"
        self._run_and_print(command=command, names=names)


