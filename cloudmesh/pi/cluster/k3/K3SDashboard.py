
class K3SDashboard():

    @classmethod
    def info(cls):
        """
        1. Checks for background ssh tunnels connected to a server
        on port K3SDashboard.PORT (8001)

        2. Verify actual connection to dashboards.

        3. Fetch login token for admin user

        Present the information to user.

        :return:
        """
        print("Info")
    
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