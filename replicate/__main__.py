import getopt
import time
import os
import sys
import logging.handlers
from replicate.config import CConfiguration
from replicate.memlog import MemoryHandler
from replicate.replicator import replicator
from replicate.rtcwake import rtc_wake
from replicate.run import run_process
from replicate.sendmail import send_email
from replicate.version import __version__, __date__


def usage():
    print( """replicate for rsync, version {version} - {date}

Syntax:

    replicate [ <options> ]

Description:
    When the replication is performed the system shall call rtcwake to wakeup 
    the system at the next time.
    
Options:
    -v                  Verbose output for testing 
    -h/--help           This help information
    -c/--config FILE    Alternate configuration file (default config.yaml, 
                        see below)

Config file

    operation:  pull                        # 'pull' or 'push', for a sleeping 
                                            # system this must be 'pull'
    hostname:   145.53.24.178               # remote host IP address or fully 
                                            # qualified domain name.
    username:   replicate                   # username on the remote host.
    ssh-key:    ./replicator                # the SSH private key for public 
                                            # key verification.
    every:
        days:   1                           # Every day start at 1:00 AM 
        time:   01:00
    bandwidth:  5000                        # Bandwidth in KB/s 
    mapping:
    -   src:    /mnt/storage/work           # The source folder to copy from 
        dst:    /mnt/storage                # The destination folder to copy to
    -   src:    /mnt/storage/prive
        dst:    /mnt/storage
    logging:
        filename:   ./replicate.log         # Logging filename, when omitted 
                                            # syslog shall be used with level 
                                            # not is set to NOTSET
        level:      DEBUG                   # NOTSET, ERROR, WARNING, INFO or 
                                            # DEBUG   
    """.format( version = __version__, date = __date__  ) )
    return


def main():
    try:
        opts, args = getopt.getopt( sys.argv[ 1: ], "hc:v", [ "help", "config=" ] )

    except getopt.GetoptError as err:
        # print help information and exit:
        print( err )  # will print something like "option -a not recognized"
        usage()
        sys.exit( 2 )

    config = 'config.yaml'
    for location in ( os.getcwd(), '/etc/replicate', '/home/replicate', '/home/replicate/bin' ):
        if os.path.exists( os.path.join( location, config ) ):
            # Got it
            config = os.path.join( location, config )
            break

    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True

        elif o in ( "-h", "--help" ):
            usage()
            sys.exit()

        elif o in ( "-c", "--config" ):
            config = a

        else:
            assert False, "unhandled option"

    end_time = time.time() + 300
    result = []
    config = CConfiguration( config, verbose )
    handler = MemoryHandler( 1000 )
    handler.setLevel( logging.DEBUG )
    handler.setFormatter( config.LOGGING_FORMAT )
    config.Logger.addHandler( handler )
    if config.Operation == 'pull':
        for mapping in config.Folders:
            result.append( replicator( config,
                                       f"{ config.Username }@{ config.Hostname }:{ mapping.src }",
                                       mapping.dst ) )

    elif config.Operation == 'push':
        for mapping in config.Folders:
            result.append( replicator( config,
                                       mapping.src,
                                       f"{ config.Username }@{ config.Hostname }:{ mapping.dst }" ) )

    else:
        raise ValueError( 'operation only pull or push allowed')

    all_ok = all( v == 0 for v in result )
    config.Logger.info( f"all_ok  {all_ok} <= {result}" )
    if config.Smtp is not None and not all_ok:
        # report error
        send_email( "NAS backup has an issue", "No all tasks were completed successfully\n\n" +
                    handler.getBuffer(), config.Smtp, config.Logger )

    elif config.Smtp is not None and config.LogLevel == 'DEBUG':
        send_email( "NAS backup has complete", handler.getBuffer(), config.Smtp, config.Logger )

    elif handler.errorCount > 0:
        send_email( "NAS backup has errors", handler.gerErrors(), config.Smtp, config.Logger )

    # Remove the e-Mail handler
    config.Logger.removeHandler( handler )
    config.Logger.info( f"DeepSleep: {config.DeepSleep} / {all_ok}" )
    if config.DeepSleep and all_ok:
        config.Logger.info( "Sleeping for 300 seconds to wait for SSH session to connect" )
        stdout = [ ]
        while time.time() < end_time:
            result = run_process( [ 'who' ], config.Logger, stdout )
            if len( stdout ) > 0:
                break

            time.sleep( 30 )

        if result == 0 and len( stdout ) == 0:
            rtc_wake( config )
            time.sleep( 10 )

        else:
            config.Logger.info( f"Users Online: { len( stdout ) }" )

    time.sleep( 1 )
    sys.exit( 0 )


# main()
