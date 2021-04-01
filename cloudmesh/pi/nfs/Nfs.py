from cloudmesh.common.sudo import Sudo

class Nfs:

    # please modify to what makes sense for you
    # commandlines and in general
    
    def __init__(self):
        pass

    def install(self):
        print("Testing")
        '''sudo apt-get install nfs-kernel-server
        sudo mkdir /mnt/nfs
        sudo chown -R pi:pi /mnt/nfs 
        sudo mount /dev/sda1 /mnt/nfs '''
        Sudo.execute('apt-get install nfs-kernel-server')

    def uninstall(self):
        raise NotImplementedError

    def info(self):
        print("Is the nfs server running")

    def share(self,path=None,hostnames=None):
        print(path,hostnames)