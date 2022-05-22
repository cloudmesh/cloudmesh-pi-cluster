from cloudmesh.common.sudo import Sudo
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Host import Host
from cloudmesh.common.console import Console
from cloudmesh.common.Printer import Printer

import subprocess

class Nfs:
    verbose = True

    @classmethod
    def debug(cls,str):
        if Nfs.verbose:
            print(str)

    def __init__(self):
        pass

    # install necessary dependencies for NFS sharing
    def install(self, host):
        # if os in [....]
        command = f"sudo apt-get install nfs-kernel-server"
        r = Host.ssh(hosts=f"pi@{host}",command = command)
        print(Printer.write(r))
        result = r[0]['success']
        Console.info(f"pi@{host}: {command} ---> {result}")

    # uninstall necessary dependencies for NFS sharing
    def uninstall(self):
        # if os in [....]
        command = f"'apt-get –-purge remove nfs-kernel-server"
        r = Host.ssh(hosts=f"pi@{host}",command = command)
        result = r[0]['success']
        Console.info(f"pi@{host}: {command} ---> {result}")

    def info(self):
        print("Is the nfs server running")
        Console.error("Not yet implemented")

    # mount manager directory to a shared directory, share that directory with workers
    # (shared directory will be created on each pi)
    def share(self, paths, hostnames):
        #for debugging
        result = {}
        #create new filesystem which will be share point, assign proper owners
        def _create_share_system(host, path):
            command = f"sudo mkdir -p {path}"
            r = Host.ssh(hosts=f"pi@{host}", command=command)
            result[f"pi@{host}: " + command] = r[0]['success']

            command = f"sudo chown -R pi:pi {path}"
            r = Host.ssh(hosts=f"pi@{host}", command=command)
            result[f"pi@{host}: " + command] = r[0]['success']

        try:
            #necessary IPs & hostnames for sharing
            manager_ip = Shell.run('hostname -I').split(' ')[1]
            mounting, mounting_to = paths.split(',')
            pis = hostnames.split(',')
            manager = pis[0]
            workers = pis[1:]

            # create on manager the share point
            _create_share_system(manager,mounting_to)

            #bind on manager an existing filesystem to the share point
            command = f"sudo mount --bind {mounting} {mounting_to}"
            r = Host.ssh(hosts=f"pi@{manager}", command=command)
            print(Printer.write(r))
            result[f"pi@{manager}: " + command] = r[0]['success']

            # preserve binding after reboot on manager
            add_to_fstab = f"{mounting}\t{mounting_to}\tnone\tbind\t0\t0"
            command = f"echo \"{add_to_fstab}\" | sudo tee --append /etc/fstab"
            r = Host.ssh(hosts=f"pi@{manager}", command=command)
            print(Printer.write(r))
            result[f"pi@{manager}: " + command] = r[0]['success']

            # add each worker hostname into manager exports file
            for worker in workers:
                add_to_exports = f"{mounting_to} {worker}(rw,no_root_squash,sync,no_subtree_check)"
                command = f"echo \"{add_to_exports}\" | sudo tee --append /etc/exports"
                r = Host.ssh(hosts=f"pi@{manager}",command=command)
                print(Printer.write(r))
                result[f"pi@{manager}: " + command] = r[0]['success']
            
            #restart NFS exports 
            command = "sudo exportfs -r"
            r = Host.ssh(hosts=f"pi@{manager}", command=command)
            print(Printer.write(r))
            result[f"pi@{manager}: " + command] = r[0]['success']


            for worker in workers:
                #create share point on workers
                _create_share_system(worker,mounting_to)

                #mount worker share point to manager share point 
                command = f"sudo mount {manager_ip}:{mounting_to} {mounting_to}"
                r = Host.ssh(hosts=f"pi@{worker}", command=command)
                print(Printer.write(r))
                result[f"pi@{worker}: " + command] = r[0]['success']

                #preserve mount after reboot on worker
                add_to_fstab = f"{manager_ip}:{mounting_to}\t{mounting_to}\tnfs\tx-systemd.automount\t0\t0"
                command = f"echo \"{add_to_fstab}\" | sudo tee --append  /etc/fstab"
                r = Host.ssh(hosts=f"pi@{worker}", command=command)
                print(Printer.write(r))
                result[f"pi@{worker}: " + command] = r[0]['success']

            for key,value in result.items():
                Console.info(f"{key} --> {value}")
            result.clear()

        except AttributeError as e:
            Console.error("Not enough hostnames")
            raise
        except ValueError as e:
            Console.error("2 filesystem paths must be provided")
            raise
        except subprocess.CalledProcessError as e:
            print(e.output)
        except IndexError as e:
            pass

    def unshare(self, path, hostnames, terminate=True):
        #for debugging
        result = {}
        
        #unmount and delete share point, remove reboot instructions
        def _unshare(host,path):
            command=f"sudo umount -f {path}"
            r = Host.ssh(hosts=f"pi@{host}", command=command)
            result[f"pi@{host}: " + command] = r[0]['success']

            command = f"sudo rm -r {path}"
            r = Host.ssh(hosts=f"pi@{host}", command=command)
            result[f"pi@{host}: " + command] = r[0]['success']

            command = "cat /etc/fstab"
            lines = Host.ssh(hosts=f"pi@{host}", command=command)[0]['stdout']
            result[f"pi@{host}: " + command] = r[0]['success']
            lines = lines.splitlines()
            new_lines = Shell.remove_line_with(lines, path)
            lines = "\n".join(new_lines)

            command = f"echo \"{lines}\" | sudo tee /etc/fstab"
            r = Host.ssh(hosts=f"pi@{host}", command=command)
            result[f"pi@{host}: " + command] = r[0]['success']
        
        #necessary hostnames for unsharing
        pis = hostnames.split(',')
        manager = pis[0]
        workers = pis[1:]

        #remove share point on workers
        for worker in workers:
            _unshare(worker,path)

        #remove worker access permissions for manager share point
        command = f"cat /etc/exports"
        r = Host.ssh(hosts=f"pi@{manager}", command=command)
        result[f"pi@{manager}: " + command] = r[0]['success']
        exports_file_text = r[0]['stdout']
        lines = exports_file_text.splitlines()

        for worker in workers:
            lines = Shell.remove_line_with(lines, worker)

        new_lines = "\n".join(lines)
        command = f"echo \"{new_lines}\" | sudo tee /etc/exports"
        r = Host.ssh(f"pi@{manager}", command=command)
        result[f"pi@{manager}: " + command] = r[0]['success']

        # unmount and remove manager share point, if specified 
        # otherwise we may want to remove workers but still keep the manager share point open
        if terminate:
            _unshare(manager,path)
        
        for key,value in result.items():
            Console.info(f"{key} --> {value}")
        result.clear()
