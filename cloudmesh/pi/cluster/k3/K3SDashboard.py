import os
import re
import subprocess
import requests
import textwrap

from cloudmesh.common.console import Console
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell

class K3SDashboard():
    # Remote Port: Port the dashboard is running on on the cluster itself
    # Local Port: Port on local machine to use to tunnel to remote port
    REMOTE_PORT = 8001
    LOCAL_PORT = 8001

    # Accesssing Dashboard
    TUNNEL_CMD = "ssh -f -L {local_port}:127.0.0.1:{remote_port} -N {host_name}"
    DASHBOARD_LINK = \
        "http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"

    # Creating Dashboard
    VERSIONS_URL = "https://github.com/kubernetes/dashboard/releases"
    DASHBOARD_DOWNLOAD = \
        "https://raw.githubusercontent.com/kubernetes/dashboard/{VERSION}/aio/deploy/recommended.yaml"


    @classmethod
    def info(cls, verbose=True):
        """
        1. Checks for background ssh tunnels connected to a server
        on port K3SDashboard.REMOTE_PORT (8001)
        2. Verify actual connection to dashboards.
        3. Fetch login token for admin user

        Present the information to user.

        :return:
        """
        ps = subprocess.check_output(['ps', 'aux'], encoding='UTF-8')
        # Regular expression to capture whole line of ssh tunneel process
        p = re.compile(f".*ssh \-f \-L {cls.LOCAL_PORT}:127\.0\.0\.1:{cls.REMOTE_PORT} \-N.*")

        if verbose:
            Console.info("Finding running dashboards...")

        found = p.findall(ps)
        if len(found) > 1 and verbose:
            Console.error(f"Too many running dashboard connections found: \n {found}")
        elif len(found) == 0 and verbose:
            Console.ok(textwrap.dedent(
            """
            No running Dashboards connections found. 
            Use 'cms pi k3 dashboard connect SERVER' to create a connection
            """
            ))

        try:
            r = requests.get(cls.DASHBOARD_LINK, timeout=5)
            if r.status_code == 200:
                active = "Active"
            else:
                active = "Up but not ready"
        except:
            active = "Not Active"

        entries = []
        for p_match in found:
            temp = p_match.split()
            entry = {
                "Server Access Point": temp[-1],
                "Remote Port": cls.REMOTE_PORT,
                "Local Port": cls.LOCAL_PORT,
                "Dashboard Status": active,
                "PID": temp[1]
            }
            entries += [entry]

        if verbose and len(entries) > 0:
            server = entries[0]["Server Access Point"]
            print(Printer.write(entries, order=["Server Access Point", "Remote Port", "Local Port", "Dashboard Status", "PID"]))
            if active == "Active":
                Console.info("Dashboard Link:")
                print(cls.DASHBOARD_LINK)
                Console.info("Fetching authentication token...")
                print(cls.get_admin_token(server=server))
            else:
                Console.info(textwrap.dedent(
                    f"""
                    You appear to have set up a connection to your server,
                    but no dashboard is running on {server}:{cls.REMOTE_PORT}.
                    Please wait a moment and try again.
                    """))

        # Should always just be of length 1
        return entries

    @classmethod
    def create(cls, server=None):
        """
        Create a dashboard with a default user on the specified server
        """
        if server is None:
            raise Exception('No server supplied for dashboard creation')

        Console.info("Installing Dashboard")
        statuses = []

        # Note the usage of double brackets around "url_effective". This is because the intended full command is:
        # curl -w '%{url_effective}' ....
        # The double brackets are used to escape formatting that is done when passed into Host.ssh
        version_fetch_cmd = \
            "curl -w '%{{url_effective}}' -I -L -s -S {VERSION_URL}/latest -o /dev/null | sed -e 's|.*/||'"

        Console.info(f"Attempting to communicate with {server}")

        res = Host.ssh(
            hosts=server,
            command=version_fetch_cmd,
            VERSION_URL=cls.VERSIONS_URL)

        version = res[0]['stdout']
        statuses.append({
            "step": "Version Fetch",
            "success": res[0]['success'],
            "stdout": version,
            "stderr": res[0]['stderr']
        })

        Console.info(f"Downloading dashboard on {server}")
        download_cmd = f"sudo k3s kubectl create -f {cls.DASHBOARD_DOWNLOAD.format(VERSION=version)}"
        res = Host.ssh(
            hosts=server,
            command = download_cmd
        )
        statuses.append({
            "step": "Create Dashboard",
            "success": res[0]['success'],
            "stdout": res[0]['stdout'],
            "stderr": res[0]['stderr']
        })

        cmds = cls.create_admin_user_cmd()
        res = Host.ssh(
            hosts=server,
            command=cmds[0])
        statuses.append({
            "step": "Create Admin Role",
            "success": res[0]['success'],
            "stdout": res[0]['stdout'],
            "stderr": res[0]['stderr']
        })

        res = Host.ssh(
            hosts=server,
            command=cmds[1])
        statuses.append({
            "step": "Create Admin User",
            "success": res[0]['success'],
            "stdout": res[0]['stdout'],
            "stderr": res[0]['stderr']
        })

        res = Host.ssh(
            hosts=server,
            command=cmds[2]
        )
        statuses.append({
            "step": "Deploy Admin Config",
            "success": res[0]['success'],
            "stdout": res[0]['stdout'],
            "stderr": res[0]['stderr']
        })

        Console.info(f"Starting dashboard on {server}")
        start_cmd = "nohup sudo k3s kubectl proxy >/home/pi/k3sdashboard.log 2>&1 &"
        res = Host.ssh(
            hosts=server,
            command=start_cmd
        )
        statuses.append({
            "step": "Start Dashboard",
            "success": res[0]['success'],
            "stdout": res[0]['stdout'],
            "stderr": res[0]['stderr']
        })

        res = Host.ssh(
            hosts=server,
            # Use grep -qxF to match whole line (check if already present to prevent duplicate)
            command=f"grep -qxF '{start_cmd}' /etc/rc.local || sudo sed -i '$i {start_cmd}' /etc/rc.local"
        )
        statuses.append({
            "step": "Enable Persistence",
            "success": res[0]['success'],
            "stdout": res[0]['stdout'],
            "stderr": res[0]['stderr']
        })

        print(Printer.write(statuses, order=["step", "success", "stdout", "stderr"], header=["Step", "Success", "stdout", "stderr"]))

    @classmethod
    def connect(cls, server=None):
        """
        Start a port forwarding connection between local machine and server to access dashboard
        """
        if server is None:
            raise Exception('Server arg is None')
        Console.info("Establishing connection to server dashboard...")
        ec = os.system(cls.TUNNEL_CMD.format(
            local_port=cls.LOCAL_PORT, remote_port=cls.REMOTE_PORT, host_name=server))
        if ec == 0:
            Console.ok('Connection created. Try "cms pi k3 dashboard info" to verify connection.')
        else:
            Console.error(f'Failed to create connection. Non-zero exit code with ssh: {ec}')

    @classmethod
    def disconnect(cls, server=None):
        """
        Kill the PID started by cls.connect
        """
        info = cls.info(verbose=False)
        for entry in info:
            if server is None or server == entry['Server Access Point']:
                Console.info(f"Disconnecting from {entry['Server Access Point']}...")
                os.system(f"kill {entry['PID']}")
                Console.ok("Verify with 'cms pi k3 dashboard info'")

    @classmethod
    def browser(cls):
        Console.ok("Opening dashboard...")
        Shell.browser(cls.DASHBOARD_LINK)
        return

    @classmethod
    def get_admin_token(cls, server=None):
        if server is None:
            raise Exception('Server arg supplied is None')

        try:
            cmd = "sudo k3s kubectl -n kubernetes-dashboard describe secret admin-user-token | grep '^token'"
            result = Host.ssh(hosts=server, command=cmd)
            entry = result[0]
            token = entry['stdout']
            token = token.split()[1]
            return token
        except KeyError as e:
            Console.error("Unexpected result of Host.ssh")
            print(result)
        except IndexError as e:
            Console.error("Unexpected result of Host.ssh")
            print(result)
        except Exception as e:
            Console.error("Error communicating with server. Full output:")
            print(e.message)

    @classmethod
    def create_admin_user_cmd(cls):
        cmds = [
            textwrap.dedent(
            """
            cat << EOF >> dashboard.admin-user-role.yml
            apiVersion: rbac.authorization.k8s.io/v1
            kind: ClusterRoleBinding
            metadata:
                name: admin-user
            roleRef:
                apiGroup: rbac.authorization.k8s.io
                kind: ClusterRole
                name: cluster-admin
            subjects:
            -  kind: ServiceAccount
               name: admin-user
               namespace: kubernetes-dashboard
            EOF
            """
            ),
            textwrap.dedent(
            """
            cat << EOF >> dashboard.admin-user.yml
            apiVersion: v1
            kind: ServiceAccount
            metadata:
                name: admin-user
                namespace: kubernetes-dashboard
            EOF
            """
            ),
            "sudo k3s kubectl create -f dashboard.admin-user.yml -f dashboard.admin-user-role.yml"
        ]
        return cmds

