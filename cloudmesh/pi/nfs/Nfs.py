from cloudmesh.common.sudo import Sudo
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Host import Host


class Nfs:
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

    def unshare(self, path, hostnames, terminate=False):
        # get manager hostname
        # manager_hn = Shell.run('hostname').strip()

        pis = hostnames.split(',')
        manager = pis[0]
        workers = pis[1:]

        # if manager is included in hostnames, then we will be unmounting its shared drive
        # (We do not want it shared with anyone, so no need to keep it mounted)
        if terminate:
            print("taking down manager share")
            # unmount shared directory
            print("umount manager /mnt/nfs")
            r = Host.ssh(hosts=f"pi@{manager}", command=f"sudo umount -l {path}")
            print(r)
            print("remove manager /mnt/nfs")
            r = Host.ssh(hosts=f"pi@{manager}", command=f'sudo rm -r {path}')
            print(r)

            print("editing manager fstab for terminate")
            # remove mount binding on manager pi
            # lines = Sudo.readfile("/etc/fstab")
            lines = Host.ssh(hosts=f"pi@{manager}", command="cat /etc/fstab")[0]['stdout']
            print(lines)
            lines = lines.splitlines()
            new_lines = Shell.remove_line_with(lines, path)
            lines = "\n".join(new_lines)
            # Sudo.writefile("/etc/fstab",lines)
            print("rewrite fstab manager")
            r = Host.ssh(hosts=f"pi@{manager}", command=f"echo \"{lines}\" | sudo tee /etc/fstab")
            print(r)

        # For each worker pi entered, we remove permissions for workers from the MANAGER'S /etc/exports file
        print("removing permissions for workers in /etc/exports")
        exports_file_text = Host.ssh(hosts=f"pi@{manager}", command=f"cat /etc/exports")[0]['stdout']
        lines = exports_file_text.splitlines()

        for worker in workers:
            lines = Shell.remove_line_with(lines, worker)

        new_lines = "\n".join(lines)
        r = Host.ssh(f"pi@{manager}", command=f"echo \"{new_lines}\" | sudo tee /etc/exports")
        print(r)

        # For each worker, we unmount its shared drive, remove shared drive
        # and remove mounting instructions from /etc/fstab files
        for worker in workers:
            # unmount shared directory, remove shared directory
            print(f"unmounting {worker}")
            Host.ssh(hosts=f"pi@{worker}", command=f"sudo umount -l {path}")
            Host.ssh(hosts=f"pi@{worker}", command=f"sudo rm -r {path}")

            # remove mounting instructions
            print('edit worker fstab')
            lines = Host.ssh(hosts=f"pi@{worker}", command=f"cat /etc/fstab")[0]['stdout']
            lines = lines.splitlines()
            lines = Shell.remove_line_with(lines, path)
            new_lines = "\n".join(lines)
            r = Host.ssh(hosts=f"pi@{worker}", command=f"echo \"{new_lines}\" | sudo tee /etc/fstab")
            print(r)
# Look into mount timeouts
