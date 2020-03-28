# Documentation

This README is managed in 

* [README.md](https://github.com/cloudmesh/cloudmesh-pi-cluster/blob/master/README.md)
* <https://github.com/cloudmesh/cloudmesh-pi-cluster>

## Prerequisite

Set up cloudmesh on the master 

```bash
$ sudo apt-get update
$ sudo apt-get full-upgrade
$ sudo apt-get install emacs
$ ssh-keygen
$ echo 'alias python="/usr/bin/python3"' >> ~/.bashrc
$ source .bashrc
$ python --version
$ python -m venv ~/ENV3
$ source ~/ENV3/bin/activate
$ pip install pip -U 
$ pip install cloudmesh-installer 
$ cloudmesh-installer get pi
```

## Setting LEDS

``` bash
$ cms pi led green on
$ cms pi led green off
$ cms pi led red on
$ cms pi led red off
```

## Getting the Temperature

```bash
cms pi temp "red,red[01-03]"
+-------+--------+------+
| host  | cpu    | gpu  |
+-------+--------+------+
| red   | 55.991 | 55.0 |
| red01 | 62.322 | 62.0 |
| red02 | 64.757 | 65.0 |
| red03 | 55.504 | 55.0 |
+-------+--------+------+
```

## Watching the temperature continiously

To watch the temperature continiously in the termoinal, use a repeat rate.  
To end the  program press CTRL-C

```
cms pi temp "red,red[01-03]" --rate=1.0
```