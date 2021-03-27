



pi k3 install [--manager=MANAGER] [--workers=WORKERS] [--step=COMMAND]
We will be using this when many workers are presents

pi k3 install [--hostname=HOSTNAMES] [--step=COMMAND]
Setting up single k3s cluster

pi k3 join --manager=MANAGER --workers=WORKERS

pi k3 join --name=NAME [--manager=MANAGER] --workers=WORKERS




pi k3 uninstall [--manager=MANAGER] [--workers=WORKERS]
pi k3 delete [--manager=MANAGER] [--workers=WORKERS]
pi k3 test --name=NAME [--manager=MANAGER] [--workers=WORKERS]
pi k3 view

pi k3 monitor

##
Inventory name for each cluster. Mechanism to setup multiple clusters, ability to active/deactive the nodes
Purge will remove all non active nodes.

Inventory yml and k3s yml file. Inventory yml creates k3s yml


1. Single
2. multiple clusters
2a. sub clusters with one single
   
