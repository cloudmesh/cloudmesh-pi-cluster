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
        Sudo.execute('apt-get install nfs-kernel-server')


    def uninstall(self):
        raise NotImplementedError

    def info(self):
        print("Is the nfs server running")

    def share(self,paths,hostnames=None):
        mounting, mountingTo = paths.split(',')
        print('Check Mounts',mounting,mountingTo)

        #create and bind paths on manager
        Sudo.execute(f'''mkdir -p {mountingTo} && 
                        chown -R pi:pi {mountingTo} && 
                        mount --bind {mounting} {mountingTo}''')

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
                r = Host.ssh(hosts=f"pi@{worker}",command = f"sudo mount pi@{managerIP}:{mountingTo} {mountingTo}")
                print(r)
                # Sudo.execute(f'''ssh pi@{worker} &&
                #                 mkdir {mountingTo} &&
                #                 chown -R pi:pi {mountingTo} &&
                #                 mount {managerIP}:{mountingTo} {mountingTo}''')
        
        except AttributeError as e:
            print("No hostnames provided")
        except IndexError as e:
            pass

    #def unshare(self,paths=None, hostnames=None, force = False):
        

        


        
