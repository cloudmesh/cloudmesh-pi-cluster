from cloudmesh.common.sudo import Sudo
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Host import Host
from cloudmesh.common.console import Console
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import str_bool
from cloudmesh.common.util import yn_choice
from cloudmesh.common.parameter import Parameter
from cloudmesh.burn.usb import USB
from cloudmesh.burn.sdcard import SDCard

import subprocess
import textwrap
import re

class Nfs:
    verbose = True

    @classmethod
    def debug(cls,str):
        if Nfs.verbose:
            print(str)

    def __init__(self):
        pass

    @staticmethod
    def hostexecute(script, name_of_pi):
        """

        :param script:
        :type script:
        :param name_of_pi:
        :type name_of_pi:
        :return:
        :rtype:
        """
        for command in script.splitlines():
            print(command)
            results = Host.ssh(hosts=name_of_pi, command=command)
            print(Printer.write(results))
            return results

    # install necessary dependencies for NFS sharing
    def install(self, host, user='pi'):
        # if os in [....]
        command = f"sudo apt-get install nfs-kernel-server"
        r = Host.ssh(hosts=f"{user}@{host}",command = command)
        print(Printer.write(r))
        result = r[0]['success']
        Console.info(f"{user}@{host}: {command} ---> {result}")

    # uninstall necessary dependencies for NFS sharing
    def uninstall(self, host, user='pi'):
        # if os in [....]
        command = f"'apt-get –-purge remove nfs-kernel-server"
        r = Host.ssh(hosts=f"{user}@{host}",command = command)
        print(Printer.write(r))
        result = r[0]['success']
        Console.info(f"{user}@{host}: {command} ---> {result}")

    def info(self):
        print("Is the nfs server running")
        Console.error("Not yet implemented")

    # mount manager directory to a shared directory, share that directory with workers
    # (shared directory will be created on each pi)
    def share(self, paths, hostnames, usb=None, user='pi'):
        #for debugging
        result = {}

        #check to see what the USB parameter is
        usb = str_bool(usb)

        #create new filesystem which will be share point, assign proper owners
        def _create_share_system(host, path, username):

            command = f"sudo mkdir -p {path}"
            r = Host.ssh(hosts=f"{username}@{host}", command=command)
            result[f"{username}@{host}: " + command] = r[0]['success']

            command = f"sudo chown -R {username}:{username} {path}"
            r = Host.ssh(hosts=f"{username}@{host}", command=command)
            result[f"{username}@{host}: " + command] = r[0]['success']

        try:
            #necessary IPs & hostnames for sharing
            manager_ip = Shell.run('hostname -I').strip().split(' ')[0]

            if not usb:
                mounting, mounting_to = paths.split(',')
            else:
                mounting_to = paths

            pis = Parameter.expand(hostnames)
            manager = pis[0]
            workers = pis[1:]

            if usb:
                if not yn_choice(
                        'Please ensure that the USB storage medium is inserted into the '
                        'manager pi and type y and press Enter when done'):
                    Console.error("You pressed no but the script is continuing as normal...")
                    return ""
                card = SDCard()
                card.info()
                USB.check_for_readers()
                print('Please enter the device path e.g. "/dev/sda" or enter no input to default to /dev/sda '
                      '(remember, do not add quotation marks)\n')
                print('The contents of the device of the path you enter WILL BE FORMATTED AND DELETED and used '
                      'as cluster file storage: ')
                device = input()
                if device == '':
                    device = '/dev/sda'
                print(device)
                script = textwrap.dedent(
                    f"""
                    sudo mkfs.ext4 -F {device}
                    """).strip()
                results = Nfs.hostexecute(script, f"{user}@{manager}")
                for entry in results:
                    if "is mounted; will not make a filesystem here" in str(entry["stderr"]):
                        Console.error("The USB is already mounted. Do you still want to use it as nfs?\n")
                        if not yn_choice('Type y and press Enter to continue, or n to stop the program: '):
                            Console.ok('\nStopping...')
                            return ""
                        else:
                            Console.ok('Continuing...')
                results = Host.ssh(hosts=f"{user}@{manager}", command=f"sudo blkid {device}")
                print(Printer.write(results))
                for entry in results:
                    print(str(entry["stdout"]))
                    blkid = str(entry["stdout"])
                print(blkid)
                blkid2 = re.findall(r'\S+', blkid)
                print(blkid2)
                result2 = [i for i in blkid2 if i.startswith('UUID=')]
                print(result2)
                listToStr = ' '.join(map(str, result2))
                result3 = re.findall(r'"([^"]*)"', listToStr)
                result3 = " ".join(str(x) for x in result3)
                print(type(result3))
                print(result3)
                script = textwrap.dedent(
                    f"""
                    echo "UUID={result3} {mounting_to} ext4 defaults 0 2" | sudo tee /etc/fstab -a
                    sudo mount -a
                    """).strip()
                Nfs.hostexecute(script, f"{user}@{manager}")


            # create on manager the share point
            _create_share_system(manager,mounting_to,user)

            #bind on manager an existing filesystem to the share point
            if not usb:
                command = f"sudo mount --bind {mounting} {mounting_to}"
            else:
                command = f"sudo mount -a"
            r = Host.ssh(hosts=f"{user}@{manager}", command=command)
            print(Printer.write(r))
            for entry in r:
                if 'does not exist' in str(entry['stderr']):
                    Console.error(f'Directory {mounting} does not exist!')
                    return ""
            result[f"{user}@{manager}: " + command] = r[0]['success']

            if not usb:
                # preserve binding after reboot on manager
                add_to_fstab = f"{mounting}\t{mounting_to}\tnone\tbind\t0\t0"
                command = f"echo \"{add_to_fstab}\" | sudo tee --append /etc/fstab"
                r = Host.ssh(hosts=f"{user}@{manager}", command=command)
                print(Printer.write(r))
                result[f"{user}@{manager}: " + command] = r[0]['success']

            # add each worker hostname into manager exports file
            for worker in workers:
                add_to_exports = f"{mounting_to} {worker}(rw,no_root_squash,sync,no_subtree_check)"
                command = f"echo \"{add_to_exports}\" | sudo tee --append /etc/exports"
                r = Host.ssh(hosts=f"{user}@{manager}",command=command)
                print(Printer.write(r))
                result[f"{user}@{manager}: " + command] = r[0]['success']
            
            #restart NFS exports 
            command = "sudo exportfs -r"
            r = Host.ssh(hosts=f"{user}@{manager}", command=command)
            print(Printer.write(r))
            for entry in r:

                if 'duplicated export entries' in str(entry['stderr']):
                    Console.error("Detected duplicated export entries. Removing...")
                    filename = path_expand("/etc/exports")
                    export_file = []
                    r2 = Host.ssh(hosts=f"{user}@{manager}",command="sudo cat /etc/exports")
                    print(Printer.write(r2))
                    for entry2 in r2:
                        string_of_export = str(entry2['stdout'])
                    fixed_export_list = string_of_export.splitlines()
                    no_duplicates = [i for n, i in enumerate(fixed_export_list) if i not in fixed_export_list[:n]]
                    print(no_duplicates)
                    home_dir = path_expand("~")
                    with open(f'{home_dir}/exportfile.txt', 'w') as f:
                        for item in no_duplicates:
                            f.write("%s\n" % item)
                    r2 = Host.ssh(hosts=f"{user}@{manager}", command=f"sudo cp {home_dir}/exportfile.txt /etc/exports")
                    print(Printer.write(r2))
                    r2 = Host.ssh(hosts=f"{user}@{manager}", command=f"sudo rm {home_dir}/exportfile.txt")
                    print(Printer.write(r2))
                    r2 = Host.ssh(hosts=f"{user}@{manager}", command="sudo cat /etc/exports")
                    print(Printer.write(r2))
                    command = "sudo exportfs -r"
                    r = Host.ssh(hosts=f"{user}@{manager}", command=command)
                    print(Printer.write(r))

            result[f"{user}@{manager}: " + command] = r[0]['success']

            if not usb:
                r = Host.ssh(hosts=f"{user}@{manager}", command=f'chmod +rx {mounting}')
                print(Printer.write(r))
            else:
                r = Host.ssh(hosts=f"{user}@{manager}", command=f'chmod +rx {mounting_to}')
                print(Printer.write(r))

            for worker in workers:
                #create share point on workers
                _create_share_system(worker,mounting_to,user)

                #mount worker share point to manager share point 
                command = f"sudo mount {manager_ip}:{mounting_to} {mounting_to}"
                r = Host.ssh(hosts=f"{user}@{worker}", command=command)
                print(Printer.write(r))
                result[f"{user}@{worker}: " + command] = r[0]['success']

                #preserve mount after reboot on worker
                add_to_fstab = f"{manager_ip}:{mounting_to}\t{mounting_to}\tnfs\tx-systemd.automount\t0\t0"
                command = f"echo \"{add_to_fstab}\" | sudo tee --append  /etc/fstab"
                r = Host.ssh(hosts=f"{user}@{worker}", command=command)
                print(Printer.write(r))
                result[f"{user}@{worker}: " + command] = r[0]['success']

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

    def unshare(self, path, hostnames, terminate=True, user='pi'):
        #for debugging
        result = {}
        
        #unmount and delete share point, remove reboot instructions
        def _unshare(host,path):
            command=f"sudo umount -f {path}"
            r = Host.ssh(hosts=f"{user}@{host}", command=command)
            result[f"{user}@{host}: " + command] = r[0]['success']

            command = f"sudo rm -r {path}"
            r = Host.ssh(hosts=f"{user}@{host}", command=command)
            result[f"{user}@{host}: " + command] = r[0]['success']

            command = "cat /etc/fstab"
            lines = Host.ssh(hosts=f"{user}@{host}", command=command)[0]['stdout']
            result[f"{user}@{host}: " + command] = r[0]['success']
            lines = lines.splitlines()
            new_lines = Shell.remove_line_with(lines, path)
            lines = "\n".join(new_lines)

            command = f"echo \"{lines}\" | sudo tee /etc/fstab"
            r = Host.ssh(hosts=f"{user}@{host}", command=command)
            result[f"{user}@{host}: " + command] = r[0]['success']
        
        #necessary hostnames for unsharing
        pis = Parameter.expand(hostnames)
        manager = pis[0]
        workers = pis[1:]

        #remove share point on workers
        for worker in workers:
            _unshare(worker,path)

        #remove worker access permissions for manager share point
        command = f"cat /etc/exports"
        r = Host.ssh(hosts=f"{user}@{manager}", command=command)
        result[f"{user}@{manager}: " + command] = r[0]['success']
        exports_file_text = r[0]['stdout']
        lines = exports_file_text.splitlines()

        for worker in workers:
            lines = Shell.remove_line_with(lines, worker)

        new_lines = "\n".join(lines)
        command = f"echo \"{new_lines}\" | sudo tee /etc/exports"
        r = Host.ssh(f"{user}@{manager}", command=command)
        result[f"{user}@{manager}: " + command] = r[0]['success']

        # unmount and remove manager share point, if specified 
        # otherwise we may want to remove workers but still keep the manager share point open
        if terminate:
            _unshare(manager,path)
        
        for key,value in result.items():
            Console.info(f"{key} --> {value}")
        result.clear()
