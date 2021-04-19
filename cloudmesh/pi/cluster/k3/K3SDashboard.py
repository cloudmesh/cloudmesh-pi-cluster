import re
import subprocess
import requests
import textwrap

from cloudmesh.common.console import Console
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer

class K3SDashboard():
    REMOTE_PORT = 8001
    LOCAL_PORT = 8001
    TUNNEL_CMD = "ssh -f -L {local_port}:127.0.0.1:{remote_port} -N {host_name}"
    DASHBOARD_LINK = "http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"

    DEBUG = False

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
                    """))

        return entries

    @classmethod
    def create(cls, server=None):
        """
        Create a dashboard with K3SDashboard.ADMIN_USER as the default user on server
        """
        print("Create")

    @classmethod
    def connect(cls, server=None):
        """
        Start an ssh tunnel from the local mmachine to server on dashboard port
        """
        print("Connect")

    @classmethod
    def get_admin_token(cls, server=None):
        if server is None:
            raise Exception('Server arg supplied is None')

        try:
            result = Host.ssh(hosts=server, command="sudo k3s kubectl -n kubernetes-dashboard describe secret admin-user-token | grep '^token'")
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
