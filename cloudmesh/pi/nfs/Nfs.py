from cloudmesh.common.sudo import Sudo
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Host import Host

class Nfs:

    # please modify to what makes sense for you
    # commandlines and in general
    
    def __init__(self):
        pass

    def install(self,hostnames=None, manager=None):
        print("Testing")
        Sudo.execute('apt-get install nfs-kernel-server', decode = False)


    def uninstall(self):
        raise NotImplementedError

    def info(self):
        print("Is the nfs server running")

    def share(self,paths,hostnames):
        mounting, mountingTo = paths.split(',')
        print('Check Mounts',mounting,mountingTo)

        #create and bind paths on manager
        Sudo.execute(f'mkdir -p {mountingTo}', debug = True)
        Sudo.execute(f'chown -R pi:pi {mountingTo}')
        Sudo.execute(f'mount --bind {mounting} {mountingTo}', debug = True)

        #preserve binding after reboot
        Sudo.writefile('/etc/fstab',f'{mounting}\t{mountingTo}\tnone\tbind\t0\t0',append=True)
        
        #SHARE EXPORT PATH WITH WORKERS

        #get manager IP
        managerIP = Shell.run('hostname -I').split(' ')[1]

        try:
            workers = hostnames.split(',')
            #iterate through worker hostnames
            for i in range(1,len(workers)):
                worker = workers[i]
                #add each hostname into manager exports file
                Sudo.writefile('/etc/exports',f'{mountingTo} {worker}(rw,no_root_squash,sync,no_subtree_check)',append=True)
                
                #ssh into workers, mount directory
                r = Host.ssh(hosts=f"pi@{worker}",command = f"sudo mkdir -p {mountingTo}")
                print(r)
                r = Host.ssh(hosts=f"pi@{worker}",command = f"sudo chown -R pi:pi {mountingTo}")
                print(r)
                r = Host.ssh(hosts=f"pi@{worker}",command = f"sudo mount -vvvv {managerIP}:{mountingTo} {mountingTo}")
                print(r)
                # Sudo.execute(f'''ssh pi@{worker} &&
                #                 mkdir {mountingTo} &&
                #                 chown -R pi:pi {mountingTo} &&
                #                 mount {managerIP}:{mountingTo} {mountingTo}''')
        
        except AttributeError as e:
            print("No hostnames provided")
        except IndexError as e:
            pass

    def unshare(self,path, hostnames):
        #get manager hostname
        managerHN = Shell.run('hostname').strip()
        pis = hostnames.split(',')
        firstPi = pis[0]

        #if manager is included in hostnames, then we will be unsharing its drive with all workers
        if firstPi == managerHN:
            # Sudo.execute(f'sudo umount -l {path}')
            pis.remove(firstPi)

            if path in Sudo.readfile('/etc/fstab'):
                print('found')
                lines = Sudo.readfile("/etc/fstab").splitlines()
                print(lines)
                new_lines = Shell.remove_line_with(Sudo.readfile("/etc/fstab").splitlines(),f'{path}')
                print(new_lines)
                Sudo.writefile("/etc/fstab",new_lines)

                # Sudo.writefile('/etc/fstab',Shell.remove_line_with(Sudo.readfile('/etc/fstab').splitlines(),f'{path}'))

        # #Remove permissions for workers in /etc/exports file
        # exportsFileText = readfile('/etc/exports').splitlines()
        # for worker in pis:
        #     exportsFileText = (Shell.remove_line_with(exportsFileText,f'{pi}'))

        # writefile('/etc/exports',exportsFileText)

        # #unmount the shared drives in the workers
        # for worker in pis:
        #     Host.ssh(hosts=f"pi@{worker}",command = f"sudo umount -l {path}")