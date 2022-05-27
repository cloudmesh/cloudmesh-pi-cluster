# How to run pytest for nfs

To run pytest for cms pi nfs, `ssh` into the manager Pi.
Then clone cloudmesh-pi-cluster while standing
in cm.

```bash
(ENV3) you@yourhostcomputer $ ssh red
pi@red:~ $ cd ~/cm
pi@red:~/cm $ git clone https://github.com/cloudmesh/cloudmesh-pi-cluster.git
```

Then switch to appropriate branch
and install requirements.

```bash
pi@red:~/cm $ cd cloudmesh-pi-cluster
pi@red:~/cm/cloudmesh-pi-cluster $ git checkout nfs
pi@red:~/cm/cloudmesh-pi-cluster $ git pull
pi@red:~/cm/cloudmesh-pi-cluster $ pip install -e .
```

Lastly, run the pytest. You can
customize the parameters --username
and --hostname.

```bash
(ENV3) pi@red:~cm/cloudmesh-pi-cluster $ pytest -v --capture=no tests/test_nfs.py --username=pi --hostname=red,red0[1-3]
```

