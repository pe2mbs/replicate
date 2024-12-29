# Replicate
This package was build to replicate files between two TrueNAS systems. 
After the replication is done, 'rtcwake' is called to put the backup system
to sleep, until the next wakeup time. This wakeup time is configured in 
the configuration file. When there are errors during the rsync operation
these errors may be mailed to a configured address. 


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
pip install git+https://github.com/pe2mbs/replicate.git
```
Use 'main' when you need to latest development branch or use 'stable'
for the latest stable release.

On installing the replicate module also the dependencies are installed
in the virtual environment. 

# Starting the replication
The start command is therefor:

```bash
$ /etc/replicate/venv/bin/replicate
```
The configuration is stored in /etc/replicate/config.yaml

# Example configuration
The following configuration this is set up on the backup node. This node 
sleeps until 1:00 AM every day, on boot the task should be started.
when finished the node shall goback into deep sleep until the next day.
Make sure that the config file has attribute 0600, so that only root 
can read the file, as it stores possible password and key filename.  

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
    level:      INFO
mail:
    username:   truenas@example.com
    password:   a-very-secret-password-for-truenas@example.com
    sender:     truenas@backup.example.coms
    receiver:   foobar@example.com
    host:       example.com
    port:       465
```

## operation
Operations are push or pull, for a backup system this should always be 'pull'.
When omitted 'pull' is the default.

## hostname
This is the hostname or IP address of the primary NAS, where the files must be 
replicated from.

## username
This is username on the primary NAS, a public key must be setup for this user.

## ssh-key
This is the public key file for the replication user. see for more information 
https://www.ssh.com/academy/ssh-keys

## deep-sleep
This boolean flag indicates if the system shall go into sleep mode by using 
rtcwake. When 'deep-sleep' is omitted true is the default.

## every
Any of the 'weeks', 'days', 'hours', 'minutes' or 'seconds' must be set.
The smallest value is 1 day, 24 hours, 1440 minutes or 86400 seconds. 

The setting in the example, performs once a day at 6:00 AM the replication
and then goto sleep again.

### weeks
The number of weeks between replication.

### days
The number of days between replication.

### hours
The number of hours between replication.

### minutes
The number of minutes between replication.

### seconds
The number of seconds between replication.

### time
This is the time HH:MM when the system shall wake up after the time is passed.

## bandwidth
The bandwidth can be limited during the replication, when omitted the maximum 
bandwidth is used by the replication program. The bandwidth is set in KiloBytes
per second. For a 100 MBit line set the 'bandwidth' to 5000 to use half of the 
line capacity.

## mapping
the mapping is a list or src (source) and dst (destination) folders. 
### src
The source path on the primary NAS.

### dst
The destination path on the backup NAS.

## logging:
When the logging section is omitted not logging is performed.

### filename
When filename is omitted the logging is done to syslog.

### level
When set to INFO only on errors there shall be an e-mail sent.
Whenever level is set to DEBUG after every operation an e-mail is sent, this
primary intended for development.

## mail
When the mail section is included the replication program shall send e-mails

### host
The SMTP host name or IP-address

### port
The SMTP port to be used, this maybe 465, 587 depending on the configuration
of the mail server.

### username
The username to connect to the SMTP host

### password
The password that belongs to username to connect to the SMTP host.

### sender
This is the e-mail address of the sender, some mail servers may allow any 
e-mail address, then configure an address that indicates the machine, 
( like truenas.backup@example.com )

### receiver
This is the email address where the emails are send to.


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

# Tested 
This is tested on TrueNAS scale version 24.04.
