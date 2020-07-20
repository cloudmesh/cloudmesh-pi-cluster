import os
import subprocess
from pprint import pprint
from cloudmesh.common.Host import Host
from cloudmesh.common.util import banner
from cloudmesh.common.JobSet import JobSet
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.console import Console
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.parameter import Parameter


class Mongo:

    def execute(self, arguments):
        """
        pi mongo start [--type=TYPE] [--master=MASTER] [--workers=WORKERS] [--port=PORT] [--dbpath=DBPATH] [--ip_bind=IP_BIND]
        pi mongo install [--master=MASTER] [--workers=WORKERS]
        pi mongo uninstall --master=MASTER [--workers=WORKERS]
        pi mongo test [--port=PORT]
        pi mongo stop

        :param arguments:
        :return:
        """
        self.master = arguments.master
        self.workers = Parameter.expand(arguments.workers)

        hosts = []
        if arguments.master:
            hosts.append(arguments.master)

        if arguments.workers:
            hosts = hosts + Parameter.expand(arguments.workers)

        ipbind = None
        if '--ip_bind' in arguments.keys():
            ipbind = arguments['--ip_bind']

        dbpath = None
        if '--dbpath' in arguments.keys():
            dbpath = arguments['--dbpath']

        port = None
        if '--port' in arguments.keys():
            port = arguments['--port']

        if arguments.dryrun:
            self.dryrun = True

        if (hosts is None) and (arguments.stop is None) and (arguments.test is None):
            Console.error("You need to specify at least one master or worker")
            return

        if arguments.install:
            self.install(hosts)

        elif arguments.start:
            if (arguments['--type'] == "local"):
                self.start_local(port, dbpath, ipbind)
            elif (arguments['--type'] == "replica"):
                self.start_replica(arguments.master, arguments.workers, port)

        elif arguments.stop:
            self.stop()

        elif arguments.test:
            if port == None:
                Console.error(
                    "You need to specify exactly 1 port number. If multiple are specified, first will be selected")
            else:
                self.test(port=port)

        elif arguments.uninstall:
            self.uninstall(hosts)

    def install(self, hosts):

        job_set = JobSet("mongo_install", executor=JobSet.ssh)
        command = """
            sudo apt update
            sudo apt -y upgrade
            sudo apt -y install mongodb
            sudo apt-get -y install python3-pip
            python3 -m pip install pymongo
            mkdir -p /home/pi/data/db
            """
        # Install mongodb on all Pis
        for host in hosts:
            job_set.add({"name": host, "host": host, "command": command})
        job_set.run(parallel=len(hosts))
        job_set.Print()

        # Copy config files to all hosts
        # Have not used JobSet here. Copying serially...
        for host in hosts:
            command = f"scp /home/pi/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/mongo/bin/local_setup.cfg pi@{host}:/home/pi/mongodb.conf"
            os.system(command)

        banner("MongoDB Setup and Configuration Complete")

    def uninstall(self, hosts):
        job_set = JobSet("mongo_install", executor=JobSet.ssh)
        command = """
            sudo apt-get -y remove mongodb
            sudo apt-get -y remove --purge mongodb
            sudo apt-get autoremove
            python3 -m pip uninstall pymongo
            """

        for host in hosts:
            job_set.add({"name": host, "host": host, "command": command})

        job_set.run(parallel=len(hosts))
        job_set.Print()
        banner("MongoDB Removed Succesfully")
        return

    def start_local(self, port, dbpath, ip):

        # Setting defaults if no argument is provided
        if port is None:
            port = 27051
        if dbpath is None:
            dbpath = "/home/pi/data/db"
        if ip is None:
            ip = "127.0.0.1"

        Console.msg("mongod instance started on IP=" + ip + " PORT=" + port + " \nwith DBPATH=" + dbpath)
        command = f"sudo mongod --config=/etc/mongodb.conf --dbpath={dbpath} --port={port} --bind_ip={ip}"
        output = subprocess.run(command.split(" "), shell=False, capture_output=True)
        Console.msg(output.stdout.decode('utf-8'))
        banner("MongoDB service started succesfully")
        return

    def start_replica(self, master, workers, port):
        Console.msg("Replica")

        # Currently this value is fixed to a 1 Master and 3 Worker config only. It is recommended to
        # have an odd number of members in replica sets to avoid ties during voting.
        hosts = Parameter.expand(workers)
        ports = Parameter.expand(port)

        if (workers is None) or (port is None):
            Console.error(
                "Specify 3 workers only. Currently this command supports 1 Primary 3 Secondary configuration. Hence, you need to supply 3 ports for configuration")
            return
        elif (len(hosts) > 3 or len(ports) > 3):
            Console.error(
                "Specify 3 workers only. Currently this command supports 1 Primary 3 Secondary configuration. Hence, you need to supply 3 ports for configuration")
            return

        for host in hosts:
            command = f"scp /home/pi/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/mongo/bin/repl_setup.cfg pi@{host}:/home/pi/mongodb.conf"
            os.system(command)

        command1 = f"mongod --config /home/pi/mongodb.conf --port {ports[0]}"
        ssh = subprocess.Popen(["ssh", "%s" % hosts[0], command1],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        command2 = f"mongod --config /home/pi/mongodb.conf --port {ports[1]}"
        ssh = subprocess.Popen(["ssh", "%s" % hosts[1], command2],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        command3 = f"mongod --config /home/pi/mongodb.conf --port {ports[2]}"
        ssh = subprocess.Popen(["ssh", "%s" % hosts[2], command3],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        cfg = """{
            _id: rs0,
            members: [
                {_id: 1, host: '""" + hosts[0] + """:""" + ports[0] + """'},
                {_id: 2, host: '""" + hosts[1] + """:""" + ports[1] + """'},
                {_id: 3, host: '""" + hosts[2] + """:""" + ports[2] + """'}
            ]
        }
        """

        command_instantiate = "mongo " + hosts[0] + ":" + ports[
            0] + " --eval \"JSON.stringify(db.adminCommand({'replSetInitiate' : " + cfg + "}))\""
        os.system(command_instantiate)

        return

    def stop(self):
        command = "sudo service mongodb stop"
        subprocess.run(command.split(" "), shell=False, capture_output=False)

        command = "sudo service mongod stop"
        subprocess.run(command.split(" "), shell=False, capture_output=False)

        banner("MongoDB service stopped succesfully")
        return

    def test(self, port):
        Console.msg("Running Test on Local...")
        # The user may specify multiple ports. Selecting only the first port.
        port = Parameter.expand(port)
        port = port[0]

        Console.msg("PORT=" + port)
        self.start_local(port=port, ip=None, dbpath=None)

        Console.msg("Local instance started. Listening for requests...")
        command = "mongo 127.0.0.1:" + port + " --eval \"printjson(db.serverStatus())\""
        returncode = os.system(command)
        if (returncode == 0):
            Console.ok("Success!")
        else:
            Console.error("Test Error! Check physical connections. Port may be already in use.")

        banner("MongoDB Test Completed")
        return 