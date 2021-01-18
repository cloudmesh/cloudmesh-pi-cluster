Pi4 reports a change in SD card timing spec for mmc0 when using sdhci.quirks2=4 and not using it. 

Without: sd uhs DDR50 (50MB/s)

With: high-speed (25 MB/s)

mmc1 is always just high-speed. I'm not sure why there are two mmc. I suppose because there are two partitions on the sd card.

Still working on actual benchmarks.

## Setup
To enable quirks
``` 
sudo nano /boot/cmdline.txt
```
And add the below to the end
```
sdhci.debug_quirks2=4
```

## Without quirks2

```
pi@raspberrypi:~ $ sudo cat /sys/kernel/debug/mmc0/ios
clock:		50000000 Hz
actual clock:	50000000 Hz
vdd:		21 (3.3 ~ 3.4 V)
bus mode:	2 (push-pull)
chip select:	0 (don't care)
power mode:	2 (on)
bus width:	2 (4 bits)
timing spec:	7 (sd uhs DDR50)
signal voltage:	1 (1.80 V)
driver type:	0 (driver type B)
```

```
pi@raspberrypi:~ $ sudo cat /sys/kernel/debug/mmc1/ios
clock:		50000000 Hz
actual clock:	41666667 Hz
vdd:		21 (3.3 ~ 3.4 V)
bus mode:	2 (push-pull)
chip select:	0 (don't care)
power mode:	2 (on)
bus width:	2 (4 bits)
timing spec:	2 (sd high-speed)
signal voltage:	0 (3.30 V)
driver type:	0 (driver type B)
```

## With quirks2

```
pi@raspberrypi:~ $ sudo cat /sys/kernel/debug/mmc0/ios
clock:		50000000 Hz
actual clock:	50000000 Hz
vdd:		21 (3.3 ~ 3.4 V)
bus mode:	2 (push-pull)
chip select:	0 (don't care)
power mode:	2 (on)
bus width:	2 (4 bits)
timing spec:	2 (sd high-speed)
signal voltage:	0 (3.30 V)
driver type:	0 (driver type B)
```

```
pi@raspberrypi:~ $ sudo cat /sys/kernel/debug/mmc1/ios
clock:		50000000 Hz
actual clock:	41666667 Hz
vdd:		21 (3.3 ~ 3.4 V)
bus mode:	2 (push-pull)
chip select:	0 (don't care)
power mode:	2 (on)
bus width:	2 (4 bits)
timing spec:	2 (sd high-speed)
signal voltage:	0 (3.30 V)
driver type:	0 (driver type B)
```

## Benchmarking quirks SD card fix
Inspiration http://www.pidramble.com/wiki/benchmarks/microsd-cards

Install utility for buffered raw throughput testing.

```
sudo apt-get install -y hdparm
```

Run throughput tests
```
sudo hdparm -t /dev/mmcblk0
```

### Without quirks

```
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p1

/dev/mmcblk0p1:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads: 134 MB in  3.01 seconds =  44.46 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p1

/dev/mmcblk0p1:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads: 134 MB in  3.02 seconds =  44.43 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p1

/dev/mmcblk0p1:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads: 134 MB in  3.02 seconds =  44.42 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p2

/dev/mmcblk0p2:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads: 140 MB in  3.03 seconds =  46.19 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p2

/dev/mmcblk0p2:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads: 134 MB in  3.01 seconds =  44.46 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p2

/dev/mmcblk0p2:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads: 134 MB in  3.01 seconds =  44.46 MB/sec
```

```
pi@raspberrypi:~ $ curl https://raw.githubusercontent.com/geerlingguy/raspberry-pi-dramble/master/setup/benchmarks/microsd-benchmarks.sh | sudo bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2247  100  2247    0     0   8415      0 --:--:-- --:--:-- --:--:--  8415

Raspberry Pi Dramble microSD benchmarks
microSD clock: 50.000 MHz

Installing iozone...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 4040k  100 4040k    0     0  1983k      0  0:00:02  0:00:02 --:--:-- 1984k

Building iozone for Linux-arm


Building fileop for Linux-arm


Building the pit_server

Install complete!

Running hdparm test...

/dev/mmcblk0:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads: 134 MB in  3.01 seconds =  44.51 MB/sec

Running dd test...

51200+0 records in
51200+0 records out
419430400 bytes (419 MB, 400 MiB) copied, 14.8317 s, 28.3 MB/s

Running iozone test...
	Iozone: Performance Test of File I/O
	        Version $Revision: 3.488 $
		Compiled for 32 bit mode.
		Build: linux-arm 

	Contributors:William Norcott, Don Capps, Isom Crawford, Kirby Collins
	             Al Slater, Scott Rhine, Mike Wisner, Ken Goss
	             Steve Landherr, Brad Smith, Mark Kelly, Dr. Alain CYR,
	             Randy Dunlap, Mark Montague, Dan Million, Gavin Brebner,
	             Jean-Marc Zucconi, Jeff Blomberg, Benny Halevy, Dave Boone,
	             Erik Habbinga, Kris Strecker, Walter Wong, Joshua Root,
	             Fabrice Bacchella, Zhenghua Xue, Qin Li, Darren Sawyer,
	             Vangel Bojaxhi, Ben England, Vikentsi Lapa,
	             Alexey Skidanov, Sudhir Kumar.

	Run began: Mon Jan 18 21:50:52 2021

	Include fsync in write timing
	O_DIRECT feature enabled
	Auto Mode
	File size set to 102400 kB
	Record Size 4 kB
	Command line used: ./iozone -e -I -a -s 100M -r 4k -i 0 -i 1 -i 2
	Output is in kBytes/sec
	Time Resolution = 0.000001 seconds.
	Processor cache size set to 1024 kBytes.
	Processor cache line size set to 32 bytes.
	File stride size set to 17 * record size.
                                                              random    random     bkwd    record    stride                                    
              kB  reclen    write  rewrite    read    reread    read     write     read   rewrite      read   fwrite frewrite    fread  freread
          102400       4     2604     2666    12185    12207     9959     2652                                                                

iozone test complete.

microSD card benchmark complete!
```

### With quirks

```
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p2

/dev/mmcblk0p2:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads:  78 MB in  3.05 seconds =  25.59 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p2

/dev/mmcblk0p2:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads:  70 MB in  3.08 seconds =  22.76 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p2

/dev/mmcblk0p2:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads:  70 MB in  3.08 seconds =  22.74 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p2

/dev/mmcblk0p2:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads:  70 MB in  3.08 seconds =  22.73 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p1

/dev/mmcblk0p1:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads:  70 MB in  3.05 seconds =  22.96 MB/sec
pi@raspberrypi:~ $ sudo hdparm -t /dev/mmcblk0p1

/dev/mmcblk0p1:
 HDIO_DRIVE_CMD(identify) failed: Invalid argument
 Timing buffered disk reads:  70 MB in  3.08 seconds =  22.76 MB/sec
```

## Testing new firmware potential 1.8V fix
 
 It did not fix the issue.
 
 What I did:
```
1. Installed latest Pi OS (1-11) using fresh download of Pi imager.On pi:
# Update rpi-eeprom-update
$ sudo apt update
$ sudo apt full-upgrade
$ sudo reboot# move latest firmware to /lib/firmware/raspberrypi/bootloader/critical to force rpi-eeprom to update
$ sudo cp /lib/firmware/raspberrypi/bootloader/latest/pieeprom-2021-01-16.bin /lib/firmware/raspberrypi/bootloader/critical/# verify it recognizes it can update
$ sudo rpi-eeprom-update# update the eeprom
$ sudo rpi-eeprom-update -a
$ sudo reboot#verify update took (current and latest under bootloader should match)
$ sudo rpi-eeprom-update
```
