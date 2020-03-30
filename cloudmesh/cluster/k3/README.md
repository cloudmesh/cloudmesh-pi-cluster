# Setting up a Pi Kubernetes Cluster

Source: <https://blog.alexellis.io/test-drive-k3s-on-raspberry-pi/>

Use cloudmesh.common.Shell wherever possible. Onet use pipes and >> <<
develop alternative python programs as they may be easier to do than shell scripts
 
 
## Related information

This may be the way to go just taht we do the install from the master instead of a laptop?

* <https://github.com/alexellis/k3sup#-micro-tutorial-for-raspberry-pi-2-3-or-4->

We can wrap the join commands in our parallel ssh command to make things faster i hope

* <https://github.com/OmegaSquad82/ansible-k3sup>


## Enable Containers


if "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory" not in /boot/cmdline.txt
   cat  cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory >>  /boot/cmdline.txt
   

see cloudmesh.k3.k3.enable_containers():
        