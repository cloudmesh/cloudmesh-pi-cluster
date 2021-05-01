from cloudmesh.common.sudo import Sudo
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Host import Host
import os

class Nfs:
    def __init__(self):
        pass

    #install necessaryd dependencies for NFS sharing
    def install(self):
        Sudo.execute('apt-get install nfs-kernel-server', decode = False)

    #uninstall necessaryd dependencies for NFS sharing
    def uninstall(self):
        Sudo.execute('apt-get –-purge remove nfs-kernel-server', decode = False)

    def info(self):
        print("Is the nfs server running")

    #mount manager directory to a shared directory, share that directory with workers (shared directory will be created on each pi)
    def share(self,paths,hostnames):
        mounting, mountingTo = paths.split(',')
        print('Mounting',mounting,'to',mountingTo)

        #create and bind directory paths on manager
        Sudo.execute(f'mkdir -p {mountingTo}', debug = True)
        Sudo.execute(f'chown -R pi:pi {mountingTo}')
        Sudo.execute(f'mount --bind {mounting} {mountingTo}', debug = True)
        print("Manager directories binded")

        #preserve binding after reboot on manager
        Sudo.writefile('/etc/fstab',f'{mounting}\t{mountingTo}\tnone\tbind\t0\t0',append=True)
        print("Binding preserved for reboot")

        #get manager IP
        managerIP = Shell.run('hostname -I').split(' ')[1]

        try:
            pis = hostnames.split(',')
            manager = pis[0]
            workers = pis[1:]

            #add each worker hostname into manager exports file
            for worker in workers:
                print(f"Adding {worker} to manager exports")
                Sudo.writefile('/etc/exports',f'{mountingTo} {worker}(rw,no_root_squash,sync,no_subtree_check)',append=True)
            Sudo.execute('sudo exportfs -r')

            #ssh into workers, mount directory
            for worker in workers:
                print(f'Setting up {worker}')
                r = Host.ssh(hosts=f"pi@{worker}",command = f"sudo mkdir -p {mountingTo}")
                r = Host.ssh(hosts=f"pi@{worker}",command = f"sudo chown -R pi:pi {mountingTo}")
                print('*****ATTEMPTING MOUNT******')
                r = Host.ssh(hosts=f"pi@{worker}",command = f"sudo mount -vvvv {managerIP}:{mountingTo} {mountingTo}")
                addToFSTAB = f"{managerIP}:{mountingTo}\t{mountingTo}\tnfs\tx-systemd.automount\t0\t0"
                r = Host.ssh(hosts=f"pi@{worker}",command = f"echo \"{addToFSTAB}\" | sudo tee --append  /etc/fstab")
        
        except AttributeError as e:
            print("No hostnames provided")
        except ValueError  as  e:
            print("2 directory paths must be provided")
        except IndexError as e:
            pass

    def unshare(self,path, hostnames):
        #get manager hostname
        managerHN = Shell.run('hostname').strip()
        pis = hostnames.split(',')
        firstPi = pis[0]

        #if manager is included in hostnames, then we will be unmounting its shared drive 
        #(We dont want it shared with anyone, so no need to keep it mounted)
        if firstPi == managerHN:
            print("manager hostname found")
            #unmount shared directory
            Sudo.execute(f'sudo umount -l {path}')
            r = Sudo.execute(f'sudo rm -r {path}')
            print(r)
            pis.remove(firstPi)

            if path in Sudo.readfile('/etc/fstab'):
                print("mount path found in fstab")
                #remove mount binding on manager pi
                lines = Sudo.readfile("/etc/fstab")
                lines = lines.splitlines()
                new_lines = Shell.remove_line_with(lines,path)
                lines = "\n".join(new_lines)
                Sudo.writefile("/etc/fstab",lines)

        #For each worker pi entered, we remove permissions for workers from the MANAGER'S /etc/exports file
        print("removing permissions for workers in /etc/exports")
        exportsFileText = Sudo.readfile('/etc/exports')
        lines = exportsFileText.splitlines()

        for worker in pis:
            lines = Shell.remove_line_with(lines,worker)

        new_lines = "\n".join(lines)
        Sudo.writefile("/etc/exports",new_lines)

        #For each worker, we unmount its shared drive, remove shared drive, and remove mounting instructions from /etc/fstab files
        for worker in pis:
            #unmount shared directory, remove shared directory
            print(f"unmounting {worker}")
            Host.ssh(hosts=f"pi@{worker}",command = f"sudo umount -l {path}")
            Host.ssh(hosts=f"pi@{worker}",command = f"sudo rm -r {path}")

            #remove mounting instructions
            lines = Host.ssh(hosts=f"pi@{worker}",command = f"cat /etc/fstab")[0]['stdout']
            lines = lines.splitlines()
            lines = Shell.remove_line_with(lines,path)
            new_lines = "\n".join(lines)
            r = Host.ssh(hosts=f"pi@{worker}",command = f"echo \"{new_lines}\" | sudo tee /etc/fstab")


# Look into mount timeouts
