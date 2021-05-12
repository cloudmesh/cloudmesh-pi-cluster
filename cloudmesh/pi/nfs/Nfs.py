from cloudmesh.common.sudo import Sudo
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Host import Host


class Nfs:
    verbose = True

    @classmethod
    def debug(cls,str):
        if Nfs.verbose:
            print(str)

    def __init__(self):
        pass

    # install necessary dependencies for NFS sharing
    def install(self):
        Sudo.execute('apt-get install nfs-kernel-server', decode=False)

    # uninstall necessary dependencies for NFS sharing
    def uninstall(self):
        Sudo.execute('apt-get –-purge remove nfs-kernel-server', decode=False)

    def info(self):
        print("Is the nfs server running")

    # mount manager directory to a shared directory, share that directory with workers
    # (shared directory will be created on each pi)
    def share(self, paths, hostnames):
        # get manager IP
        manager_ip = Shell.run('hostname -I').split(' ')[1]

        try:
            mounting, mounting_to = paths.split(',')
            print('Mounting', mounting, 'to', mounting_to)

            pis = hostnames.split(',')
            manager = pis[0]
            workers = pis[1:]

            # create and bind directory paths on manager
            print("mkdir /mnt/nfs manager")
            r = Host.ssh(hosts=f"pi@{manager}", command=f" sudo mkdir -p {mounting_to}")
            print(r)
            print("chown /mnt/nfs manager")
            r = Host.ssh(hosts=f"pi@{manager}", command=f"sudo chown -R pi:pi {mounting_to}")
            print(r)
            print("mount bind /mnt/nfs manager")
            r = Host.ssh(hosts=f"pi@{manager}", command=f"sudo mount --bind {mounting} {mounting_to}")
            print(r)
            print("Manager directories bound")

            # preserve binding after reboot on manager
            print("edit fstab manager")
            add_to_fstab = f"{mounting}\t{mounting_to}\tnone\tbind\t0\t0"
            r = Host.ssh(hosts=f"pi@{manager}", command=f"echo \"{add_to_fstab}\" | sudo tee --append /etc/fstab")
            print(r)
            print("Binding preserved for reboot")

            # add each worker hostname into manager exports file
            for worker in workers:
                print(f"Adding {worker} to manager exports")
                add_to_exports = f"{mounting_to} {worker}(rw,no_root_squash,sync,no_subtree_check)"
                r = Host.ssh(hosts=f"pi@{manager}",
                             command=f"echo \"{add_to_exports}\" | sudo tee --append /etc/exports")
                print(r)
            Host.ssh(hosts=f"pi@{manager}", command="sudo exportfs -r")

            # ssh into workers, mount directory
            for worker in workers:
                print(f'Setting up {worker}')
                print("mkdir /mnt/nfs worker")
                r = Host.ssh(hosts=f"pi@{worker}", command=f"sudo mkdir -p {mounting_to}")
                print(r)
                r = Host.ssh(hosts=f"pi@{worker}", command=f"sudo chown -R pi:pi {mounting_to}")
                print('*****ATTEMPTING MOUNT******')
                r = Host.ssh(hosts=f"pi@{worker}", command=f"sudo mount -vvvv {manager_ip}:{mounting_to} {mounting_to}")
                print(r)
                print("edit fstab worker")
                add_to_fstab = f"{manager_ip}:{mounting_to}\t{mounting_to}\tnfs\tx-systemd.automount\t0\t0"
                r = Host.ssh(hosts=f"pi@{worker}", command=f"echo \"{add_to_fstab}\" | sudo tee --append  /etc/fstab")
                print(r)

        except AttributeError as e:
            print("Error: Not enough hostnames")
            raise
        except ValueError as e:
            print("Error: 2 filesystem paths must be provided")
            raise
        except IndexError as e:
            pass

    def unshare(self, path, hostnames, terminate=True):
        result = {}
        
        def _unshare(host,path):
            command=f"sudo umount -l {path}"
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
        
        pis = hostnames.split(',')
        manager = pis[0]
        workers = pis[1:]

        for worker in workers:
            _unshare(worker,path)

        # For each worker pi entered, we remove permissions for workers from the MANAGER'S /etc/exports file
        # print("removing permissions for workers in /etc/exports")
        command = f"cat /etc/exports"
        r = Host.ssh(hosts=f"pi@{manager}", command=command)
        exports_file_text = r[0]['stdout']
        result[f"pi@{manager}: " + command] = r[0]['success']
        lines = exports_file_text.splitlines()

        for worker in workers:
            lines = Shell.remove_line_with(lines, worker)

        new_lines = "\n".join(lines)
        command = f"echo \"{new_lines}\" | sudo tee /etc/exports"
        r = Host.ssh(f"pi@{manager}", command=command)
        result[f"pi@{manager}: " + command] = r[0]['success']

        # if manager is included in hostnames, then we will be unmounting its shared drive
        # (We do not want it shared with anyone, so no need to keep it mounted)
        if terminate:
            _unshare(manager,path)
        
        for key,value in result.items():
            print(key,'--->',value)
