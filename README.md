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

Please note that the times are not exact as there is a slight delay
between getting the data and getting the data form the Pi.

```bash
cms pi temp "red,red[01-03]"
+-------+--------+------+----------------------------+
| host  | cpu    | gpu  | date                       |
+-------+--------+------+----------------------------+
| red   | 56.965 | 56.0 | 2020-03-28 14:34:46.926618 |
| red01 | 62.322 | 62.0 | 2020-03-28 14:34:46.949065 |
| red02 | 65.731 | 65.0 | 2020-03-28 14:34:46.933548 |
| red03 | 55.017 | 54.0 | 2020-03-28 14:34:47.218047 |
+-------+--------+------+----------------------------+
```

## Watching the temperature continiously

To watch the temperature continiously in the termoinal, use a repeat rate.  
To end the  program press CTRL-C

```
cms pi temp "red,red[01-03]" --rate=1.0
```

## Graph

### Sparkline

```
cms pi temp "red,red[01-03]"  --output=sparkline
▄▆█▃
```

### Bar

```
cms pi temp "red,red[01-03]"  --output=bar
```

![Display as bars](images/bar.png)

### Line

```
cms pi temp "red,red[01-03]"  --output=line
```

![Display as bars](images/line.png)


### Browser

```
cms pi temp "red,red[01-03]"  --output=browser
```

![Display as bars](images/browser.png)

### Live animation

A live animation is available with

```
cms pi temp "red,red[01-03]" --rate=1 --output=live
```

![Display as bars](images/live.png)