import textwrap
import os

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.pi.cluster.k3.K3SDashboard import K3SDashboard
from cloudmesh.common.StopWatch import StopWatch


class Installer:

    @staticmethod
    def _get_server_token(server):
        Console.info("Fetching the server token")

        command = "sudo cat /var/lib/rancher/k3s/server/node-token"
        results = Host.ssh(
            hosts=server,
            command=command
        )
        token = results[0]['stdout'].strip()

        if token == "" or "::server:" not in token:
            Console.error("Could not determine SERVER token")
            token = None
        # Console.info(f'token is {token}')
        return(token)

    @staticmethod
    def _get_server_ip(server, interface):
        Console.info(f"Fetching the server {interface} IP")

        command = f"ip -4 addr show {interface} | grep inet"
        results = Host.ssh(
            hosts=server,
            command=command
        )
        ip_str = results[0]['stdout'].strip()
        if ip_str == "":
            Console.error(f"Could not determine SERVER IP for {interface}")
            ip = None
        else:
            ip = ip_str.split(" ")[1].split('/')[0]
            Console.info(f'Server {interface} IP is {ip}')
        return(ip)

    @staticmethod
    def _run_and_print(command, names):
        results = Host.ssh(
            hosts=names,
            command=command
        )
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))


class K3(Installer):

    def __init__(self):
        pass

    def execute(self, arguments):
        """
        pi k3 enable containers NAMES
        pi k3 install server NAMES
        pi k3 install agent NAMES SERVER
        pi k3 install cluster NAMES
        pi k3 uninstall server NAMES
        pi k3 uninstall agent NAMES
        pi k3 uninstall cluster NAMES
        pi k3 kill NAMES
        pi k3 start server NAMES
        pi k3 start agent NAMES
        pi k3 start cluster NAMES
        pi k3 stop server NAMES
        pi k3 stop agent NAMES
        pi k3 stop cluster NAMES
        pi k3 remove node NAMES SERVER
        pi k3 cluster info SERVER
        pi k3 dashboard create SERVER
        pi k3 dashboard connect SERVER
        pi k3 dashboard disconnect [SERVER]
        pi k3 dashboard info
        pi k3 dashboard
        pi k3 import image NAMES SOURCE DESTINATION
        pi k3 api deploy SERVER PORTS YAML PYTHON
        :param arguments:
        :return:
        """

        if arguments.install and arguments.server:
            StopWatch.start("install server")
            self.install_server(arguments.NAMES)
            StopWatch.stop("install server")
            StopWatch.status("install server", True)
            StopWatch.print("install server", "install server")

        elif arguments.install and arguments.agent:
            StopWatch.start("install agent")
            self.install_agent(arguments.NAMES, arguments.SERVER)
            StopWatch.stop("install agent")
            StopWatch.status("install agent", True)
            StopWatch.print("install agent", "install agent")

        elif arguments.install and arguments.cluster:
            StopWatch.start("install cluster")
            self.install_cluster(arguments.NAMES)
            StopWatch.stop("install cluster")
            StopWatch.status("install cluster", True)
            StopWatch.print("install cluster", "install cluster")

        elif arguments.uninstall and arguments.server:
            StopWatch.start("uninstall server")
            self.uninstall_server(arguments.NAMES)
            StopWatch.stop("uninstall server")
            StopWatch.status("uninstall server", True)
            StopWatch.print("uninstall server", "uninstall server")

        elif arguments.uninstall and arguments.agent:
            StopWatch.start("uninstall agent")
            self.uninstall_agent(arguments.NAMES)
            StopWatch.stop("uninstall agent")
            StopWatch.status("uninstall agent", True)
            StopWatch.print("uninstall agent", "uninstall agent")

        elif arguments.uninstall and arguments.cluster:
            StopWatch.start("uninstall cluster")
            self.uninstall_cluster(arguments.NAMES)
            StopWatch.stop("uninstall cluster")
            StopWatch.status("uninstall cluster", True)
            StopWatch.print("uninstall cluster", "uninstall cluster")

        elif arguments.enable and arguments.containers:
            self.add_c_groups(arguments.NAMES)

        elif arguments.start and arguments.server:
            self.start_server(arguments.NAMES)

        elif arguments.start and arguments.agent:
            self.start_agent(arguments.NAMES)

        elif arguments.start and arguments.cluster:
            self.start_cluster(arguments.NAMES)

        elif arguments.stop and arguments.server:
            self.stop_server(arguments.NAMES)

        elif arguments.stop and arguments.agent:
            self.stop_agent(arguments.NAMES)

        elif arguments.stop and arguments.cluster:
            self.stop_cluster(arguments.NAMES)

        elif arguments.remove and arguments.node:
            StopWatch.start("remove node")
            self.remove_node(arguments.NAMES, arguments.SERVER)
            StopWatch.stop("remove node")
            StopWatch.status("remove node", True)
            StopWatch.print("remove node", "remove node")

        elif arguments.cluster and arguments.info:
            self.cluster_info(arguments.SERVER)

        elif arguments.kill:
            self.kill_all(arguments.NAMES)

        elif arguments.dashboard:
            if arguments.create:
                K3SDashboard.create(server=arguments.SERVER)
            elif arguments.info:
                K3SDashboard.info()
            elif arguments.connect:
                K3SDashboard.connect(server=arguments.SERVER)
            elif arguments.disconnect:
                K3SDashboard.disconnect(server=arguments.SERVER)
            else:
                K3SDashboard.browser()

        elif arguments["import"] and arguments.image:
            self.import_image(arguments.NAMES, arguments.SOURCE,
                              arguments.DESTINATION)

        elif arguments.api and arguments.deploy:
            self.api_deploy(arguments.SERVER, arguments.PORTS,
                            arguments.YAML, arguments.PYTHON)


    def add_c_groups(self, names):
        names = Parameter.expand(names)
        Console.info(f'Enabling containers for {names}')
        cgroups = 'cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory'
        command = f"""if test -f /boot/firmware/cmdline.txt
                then
                  FILE=/boot/firmware/cmdline.txt
                elif test -f /boot/cmdline.txt
                then
                  FILE=/boot/cmdline.txt
                fi
                if grep -q "{cgroups}" $FILE
                then
                  true
                else
                  sudo sed -i "$ s/$/ cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory/" $FILE
                fi"""
        self._run_and_print(command, names)

        manager, workers = Host.get_hostnames(names)
        command = 'sudo reboot'
        if workers:
            Console.info(f'Executing `{command}` for {workers}')
            Host.ssh(hosts=workers, command=command)

        if manager:
            Console.info(f'Executing `{command}` for {manager}')
            Host.ssh(hosts=manager, command=command)

    def install_server(self, names):
        names = Parameter.expand(names)
        if len(names) > 1:
            Console.error("This command currently supports only one server")
            return
        Console.info(f'Installing K3s as stand-alone server on {names}')
        eth_ip = self._get_server_ip(names, 'eth0')
        wlan_ip = self._get_server_ip(names, 'wlan0')
        if eth_ip is None or wlan_ip is None:
            Console.error("Internal and external IP could not be determined, "
                          "check that both interfaces are up.")
            return
        command = 'curl -sfL https://get.k3s.io | ' \
                  f'INSTALL_K3S_EXEC="--node-ip {eth_ip} ' \
                  f'--node-external-ip {wlan_ip}" sh -'
        self._run_and_print(command, names)

    def install_agent(self, names, server):
        Console.info(f'Installing K3s on {names} as agent of {server}')
        names = Parameter.expand(names)
        token = self._get_server_token(server)
        if token is None:
            return ""
        command = f"curl -sfL https://get.k3s.io | K3S_URL=https://{server}:6443 " \
                  f"K3S_TOKEN={token} sh -"
        self._run_and_print(command, names)

    def install_cluster(self, names):
        names = Parameter.expand(names)
        manager, workers = Host.get_hostnames(names)
        if manager is None:
            Console.error("A manager is required, if trying to install a "
                          "stand-alone cluster on a worker, use `cms pi k3 "
                          "install server``")
            return
        self.install_server(manager)
        self.install_agent(manager, manager)
        if workers:
            self.install_agent(workers, manager)
        K3SDashboard.create(server=manager)

    def uninstall_server(self, names):
        Console.info(f'Uninstalling server install of K3s on {names}')
        names = Parameter.expand(names)
        command = "/usr/local/bin/k3s-uninstall.sh"
        self._run_and_print(command, names)

    def uninstall_agent(self, names):
        Console.info(f'Uninstalling agent install of K3s on {names}')
        names = Parameter.expand(names)
        command = "/usr/local/bin/k3s-agent-uninstall.sh"
        self._run_and_print(command, names)

    def uninstall_cluster(self, names):
        names = Parameter.expand(names)
        manager, workers = Host.get_hostnames(names)
        self.uninstall_agent(names)
        self.uninstall_server(manager)

    def start_server(self,names):
        Console.info(f'Starting server on {names}')
        names = Parameter.expand(names)
        command = "sudo systemctl start k3s"
        self._run_and_print(command,names)

    def start_agent(self,names):
        Console.info(f'Starting agent on {names}')
        names = Parameter.expand(names)
        command = "sudo systemctl start k3s-agent"
        self._run_and_print(command,names)

    def start_cluster(self,names):
        names = Parameter.expand(names)
        manager, workers = Host.get_hostnames(names)
        self.start_server(manager)
        self.start_agent(names)

    def stop_server(self, names):
        Console.info(f'Stopping server on {names}')
        names = Parameter.expand(names)
        command = "sudo systemctl stop k3s"
        self._run_and_print(command, names)

    def stop_agent(self, names):
        Console.info(f'Stopping agent on {names}')
        names = Parameter.expand(names)
        command = "sudo systemctl stop k3s-agent"
        self._run_and_print(command, names)

    def stop_cluster(self, names):
        names = Parameter.expand(names)
        manager, workers = Host.get_hostnames(names)
        self.stop_server(manager)
        self.stop_agent(names)

    def kill_all(self,names):
        names = Parameter.expand(names)
        manager, workers = Host.get_hostnames(names)
        command = "/usr/local/bin/k3s-killall.sh"
        if workers:
            Console.info(f'Stopping k3s services and containers on {workers}')
            self._run_and_print(command, workers)
        if manager:
            Console.info(f'Stopping k3s services and containers on {manager}')
            self._run_and_print(command,manager)

    def remove_node(self,names,server):
        Console.info(f'Removing agents {names} from server {server}')
        names = Parameter.expand(names)

        for name in names:
            Console.info(f'Draining agent {name}')
            command = f"sudo kubectl drain {name} --ignore-daemonsets " \
                      f"--delete-emptydir-data"
            self._run_and_print(command, server)

            Console.info(f'Deleting agents {name}')
            command = f"sudo kubectl delete node {name}"
            self._run_and_print(command, server)

    def cluster_info(self,server):
        Console.info(f'Getting cluster info for {server}')
        Console.info("sudo kubectl get nodes -o wide")
        command = "sudo kubectl get nodes -o wide"
        results = Host.ssh(
            hosts=server,
            command=command
        )
        output = results[0]['stdout'].strip()
        print(output)

        nodes = []
        for line in output.splitlines():
            node = line.split(" ")[0]
            if node != "NAME":
                nodes.append(node)

        Console.info("Server node token")
        command = "sudo cat cat /var/lib/rancher/k3s/server/node-token"

        results = Host.ssh(
            hosts=server,
            command=command
        )
        output = results[0]['stdout'].strip()
        print(output)

        Console.info("Containers running on nodes")
        command = "sudo crictl ps"

        results = Host.ssh(
            hosts=nodes,
            command=command
        )

        for item in results:
            print(f"NODE: {item['host']}")
            print(item['stdout'])
            print()

    def import_image(self,names, source ,destination):
        names = Parameter.expand(names)

        Console.info(f"Copying image to {names} using source: {source} and "
                     f"destination: {destination}")
        Console.info("This may take a few minutes depending on the file size "
                     "and number of destinations")
        results = Host.put(
            hosts=names,
            source=source,
            destination=destination
        )

        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

        filepath = ""
        if not destination.endswith(source):
            if not destination[-1] == "/":
                filepath = f"{destination}/{source}"
            else:
                filepath = f"{destination}{source}"
        else:
            filepath = destination

        Console.info(f"Import image on {names} using filepath:{filepath}")

        command = f"sudo k3s ctr images import {filepath}"
        self._run_and_print(command, names)

    def api_deploy(self,server,ports,yaml,python):
        ports = Parameter.expand(ports)
        Console.info(f"Deploying cloudmesh openapi service based on yaml:"
                     f"{yaml} python file: {python} to ports: {ports} on "
                     f"server {server}")

        yaml_name = yaml.replace(".yaml", "")
        yaml_name = yaml_name.replace("_", "-")

        command = f"mkdir -p ~/.cloudmesh/k3s/"
        results = Host.ssh(hosts=server, command=command)
        if results[0]['success'] == 'False':
            Console.error(f"Creation of  ~/.cloudmesh/k3s result: "
                         f"{results[0]['success']}")
            return

        # todo make work with filepath and filename

        results = Host.put(
            hosts=server,
            source=yaml,
            destination="~/.cloudmesh/k3s/"
        )

        if results[0]['success'] == 'False':
            Console.error(f"Copy of {yaml} to ~/.cloudmesh/k3s result: "
                     f"{results[0]['success']}")
            return

        results = Host.put(
            hosts=server,
            source=python,
            destination="~/.cloudmesh/k3s/"
        )

        if results[0]['success'] == 'False':
            Console.error(f"Copy of {pyhthon} to ~/.cloudmesh/k3s result: "
                     f"{results[0]['success']}")
            return

        for port in ports:
            Console.info(f"Deploying service for port: {port}")
            pod_template = textwrap.dedent(f'''
            apiVersion: v1
            kind: Pod
            metadata:
              name: cloudmesh-openapi-{yaml_name}-port-{port}-pod
              labels:
                app: cloudmesh-openapi-{yaml_name}-port-{port}-pod
            spec:
              containers:
              - name: cloudmesh-openapi
                image: cloudmesh-openapi:latest
                imagePullPolicy: Never
                command: [ "/bin/bash", "-c", "--" ]
                args: [ "while true; do sleep 30; done;" ]
                volumeMounts:
                - name: config-volume
                  mountPath: /etc/config
              volumes:
                - name: config-volume
                  configMap:
                    name: cloudmesh-openapi-{yaml_name}-port-{port}-configmap
            ''').strip()

            lb_service_template = textwrap.dedent(f'''
            apiVersion: v1
            kind: Service
            metadata:
              name: cloudmesh-openapi-{yaml_name}-port-{port}-lb-service
            spec:
              selector:
                app: cloudmesh-openapi-{yaml_name}-port-{port}-pod
              ports:
                - protocol: TCP
                  port: {port}
                  targetPort: {port}
              type: LoadBalancer
            ''').strip()

            pod_filename = f"cloudmesh-openapi-{yaml_name}-port-{port}-pod.yaml"
            lb_service_filename = f"cloudmesh-openapi-{yaml_name}-port-" \
                                  f"{port}-lb-service.yaml"

            with open(pod_filename,"w+") as f:
                f.writelines(pod_template)

            with open(lb_service_filename,"w+") as f:
                f.writelines(lb_service_template)

            results = Host.put(
                hosts=server,
                source=pod_filename,
                destination="~/.cloudmesh/k3s/")

            if results[0]['success'] == 'False':
                Console.error(f"Copy of {pod_filename} to ~/.cloudmesh/k3s result: "
                              f"{results[0]['success']}")
                Console.info("Skipping to next port deployment")
                continue

            results = Host.put(
                hosts=server,
                source=lb_service_filename,
                destination="~/.cloudmesh/k3s/"
            )

            if results[0]['success'] == 'False':
                Console.error(f"Copy of {lb_service_filename} to ~/.cloudmesh/k3s result: "
                              f"{results[0]['success']}")
                Console.info("Skipping to next port deployment")
                continue

            os.remove(pod_filename)
            os.remove(lb_service_filename)

            ## todo all below make work for raspi os; ~/.cloudmesh does not work

            command = f"sudo kubectl create configmap cloudmesh-openapi-" \
                      f"{yaml_name}-port-{port}-configmap " \
                      f"--from-file=/home/ubuntu/.cloudmesh/k3s/{yaml} " \
                      f"--from-file=/home/ubuntu/.cloudmesh/k3s/{python}"
            results = Host.ssh(hosts=server, command=command)
            if results[0]['success'] == 'False':
                Console.warning(f"{command}\n result: {results[0]['success']}")

            command = "sudo kubectl apply -f " \
                      f"/home/ubuntu/.cloudmesh/k3s/{pod_filename}"
            results = Host.ssh(hosts=server, command=command)
            if results[0]['success'] == 'False':
                Console.warning(f"{command}\n result: {results[0]['success']}")

            command = "sudo kubectl apply -f " \
                      f"/home/ubuntu/.cloudmesh/k3s/{lb_service_filename}"
            results = Host.ssh(hosts=server, command=command)
            if results[0]['success'] == 'False':
                Console.warning(f"{command}\n result: {results[0]['success']}")

            command = f'sudo kubectl exec cloudmesh-openapi-' \
                      f'{yaml_name}-port-{port}-pod -- bash -c "cms openapi ' \
                      f'server start /etc/config/{yaml} --host=0.0.0.0 ' \
                      f'--port={port} > /dev/null 2>/dev/null &"'
            results = Host.ssh(hosts=server, command=command)
            if results[0]['success'] == 'False':
                Console.warning(f"{command}\n result: {results[0]['success']}")

        Console.info("Services are available at:")
        command = f'sudo kubectl get service '
        results = Host.ssh(hosts=server, command=command)
        if results[0]['success'] == True:
            print(results[0]['stdout'])
        else:
            Console.warning(f"{command}\n result: {results[0]['success']}")

