import os
import subprocess
import shutil

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.Host import Host
from cloudmesh.common.JobSet import JobSet
import platform
import sys
from cloudmesh.common.util import banner
from pprint import pprint
import textwrap
from cloudmesh.common.Tabulate import Printer

class Mongo:

    def execute(self, arguments):
        """
        pi mongo start [--type=TYPE] [--master=MASTER] [--port=PORT] [--dbpath=DBPATH] [--ip_bind=IP_BIND]
        pi mongo install [--master=MASTER] [--workers=WORKERS]
        pi mongo uninstall --master=MASTER [--workers=WORKERS]
        pi mongo stop

        :param arguments:
        :return:
        """
        self.master = arguments.master
        self.workers = Parameter.expand(arguments.workers)

        master = []
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
            ipbind = arguments['--dbpath']

        port = None
        if '--port' in arguments.keys():
            ipbind = arguments['--port']


        if arguments.dryrun:
            self.dryrun = True

        if (hosts is None) and (arguments.stop is None):
           Console.error("You need to specify at least one master or worker")
           return

        if arguments.install:
            self.install(hosts)

        elif arguments.start:
            if(arguments['--type'] == "local"):
                self.start_local(port, dbpath, ipbind)
            elif(arguments['--type'] == "replica"):
                self.start_replica(arguments.master)

        elif arguments.stop:
            self.stop()
        elif arguments.test:
            print("Test Mongo")
            # self.test(master)
            #self.run_script(name="spark.test", hosts=self.master)
            
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
            mkdir ~/data
            cd ~/data
            mkdir db
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
        if port is None:
            port=27011
        if dbpath is None:
            dbpath="/home/pi/data/db"
        if ip is None:
            ip="127.0.0.1"

        command = f"sudo mongod --config=/home/pi/mongodb.conf --dbpath={dbpath} --port={port} --bind_ip={ip}"
        output = subprocess.run(command.split(" "), shell=False, capture_output=True)
        Console.msg(output.stdout.decode('utf-8'))
        banner("MongoDB service started succesfully")
        return

    def start_replica(self, master):
        Console.msg("Replica")

        # Currently this value is fixed to a 1 Master and 3 Worker config only
        hosts = [master+"001", master+"002", master+"003"]

        for host in hosts:
            command = f"scp /home/pi/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/mongo/bin/repl_setup.cfg pi@{host}:/home/pi/mongodb.conf"
            os.system(command)

        
        command1 = "mongod --config /home/pi/mongodb.conf --port 27031"
        ssh = subprocess.Popen(["ssh", "%s" % hosts[0], command1],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        command2 = "mongod --config /home/pi/mongodb.conf --port 27032"
        ssh = subprocess.Popen(["ssh", "%s" % hosts[1], command2],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        command3 = "mongod --config /home/pi/mongodb.conf --port 27033"
        ssh = subprocess.Popen(["ssh", "%s" % hosts[2], command3],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        cfg="""{
            _id: rs0,
            members: [
                {_id: 1, host: 'localhost:27031'},
                {_id: 2, host: 'localhost:27032'},
                {_id: 3, host: 'localhost:27033'}
            ]
        }
        """

        command_inst = "mongo localhost:27031 --eval \"JSON.stringify(db.adminCommand({'replSetInitiate' : "+cfg+"}))\""
        os.system(command_inst)

        return

    def stop(self):
        command = "sudo service mongodb stop"
        subprocess.run(command.split(" "), shell=False, capture_output=False)

        command = "sudo service mongod stop"
        subprocess.run(command.split(" "), shell=False, capture_output=False)

        banner("MongoDB service stopped succesfully")
        return