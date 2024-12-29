# Replicate
This package was build to replicate files between two TrueNAS systems. 


# Installation
The package is installed in /etc/replicate/venv/bin using the virtual
environment of Python. 

```bash
$ sudo -i 
$ mkdir /etc/replicate
$ cd /etc/replicate
$ python3 -m venv venv
```
On the creation of the virtual environment an error is given, however 
a basic virtual environment is created. The next step is to get pip and
install it.

```bash
$ wget -c https://bootstrap.pypa.io/pip/pip.pyz
$ ./venv/bin/python3 ./pip.pyz install pip
$ rm pip.pyz
```

Install the replicate module from a wheel
```bash
$ ./venv/bin/pip install replicate-1.0.12-py3-none-any.whl
```

Or install the replicate module from git directly.
```bash
pip install git+https://github.com/pe2mbs.com/replicate.git@main
```
Use 'main' when you need to latest development branch or use 'stable'
for the latest stable release.

On installing the replicate module also the dependencies are installed
in the virtual environment. 

# Starting 
The start command is therefor:

```bash
$ /etc/replicate/venv/bin/replicate
```
    

The configuration is stored in /etc/replicate/config.yaml 

# Example configuration
The following configuration this is setup on the backup node. This node 
sleeps until 1:00 AM every day, on boot the task should be started.
when finished the node shall goback into deep sleep until the next day.

```yaml
operation:  pull
hostname:   123.123.123.123
username:   replicate
ssh-key:    /etc/replicate/replicator
deep-sleep: true
every:
    days:   1
    time:   01:00
bandwidth:  5000
mapping:
-   src:    /mnt/storage/work
    dst:    /mnt/storage
-   src:    /mnt/storage/prive
    dst:    /mnt/storage
logging:
    filename:   /var/log/replicate/replicate.log
    level:      DEBUG
mail:
    username:   truenas@example.com
    password:   a-very-secret-password-for-truenas@example.com
    sender:     truenas@backup.example.coms
    receiver:   foobar@example.com
    host:       example.com
    port:       465
```

# Stopping the system from sleeping after the rsync task
To stop the system to go into deep sleep, do the following:

## Using the shell option
Using the system console-shell execute the following command

```bash
$ pkill replicator
```

## Using the SSH session
Using an SSH session to stop the system from deep sleep. 

```bash
$ ssh truenas
```

When the DNS name truenas is not available first the IP address must 
be known. It can be obtained via the system console or login to the 
web interface.

```bash
$ ssh <IP-address>
```

After login the logfile /etc/log/replicate/replicate.log should show
that the replicator program is terminated. If the replicator program 
is still working the synchronization, keep the SSH session open. 

## After maintenance 
When the maintenance is done, simply restart the system (make sure
no SSH session is open). The system reboots the replicator program 
starts upon finishing the system shall go back into deep sleep.

