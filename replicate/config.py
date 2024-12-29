import sys
import typing as t
from datetime import timedelta, time, datetime
import os.path
import logging
import logging.handlers
import yaml
from pydantic import BaseModel, Field, AliasChoices


__all__ = [ 'CEvery', 'IFolderMap', 'CConfiguration', 'ISmtpMail' ]


if not hasattr( logging, 'getLevelNamesMapping' ):
    # Backport of the logging.getLevelNamesMapping() function
    def _getLevelNamesMapping():
        return logging._nameToLevel     # noqa

    logging.getLevelNamesMapping = _getLevelNamesMapping


class IEvery( BaseModel ):
    days:       t.Optional[ int ]   = Field( None )
    weeks:      t.Optional[ int ]   = Field( None )
    hours:      t.Optional[ int ]   = Field( None )
    minutes:    t.Optional[ int ]   = Field( None )
    seconds:    t.Optional[ int ] = Field( None )
    time:       str                 = Field( pattern = r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$" )


class CEvery( object ):
    def __init__( self, cfg: IEvery ):
        self.__cfg: IEvery = cfg
        return

    @property
    def TimeStr( self ) -> str:
        return self.__cfg.time

    @property
    def Time( self ) -> time:
        return datetime.strptime( self.__cfg.time, "%H:%U" ).time()

    @property
    def Weeks( self ) -> t.Union[ int, None ]:
        if hasattr( self.__cfg, 'weeks' ):
            return self.__cfg.weeks

        return None

    @property
    def Days( self ) -> t.Union[ int, None ]:
        if hasattr( self.__cfg, 'days' ):
            return self.__cfg.days

        return None

    def deltaTime( self ) -> timedelta:
        result = {}
        if hasattr( self.__cfg, 'weeks' ) and isinstance( self.__cfg.weeks, int ):
            result[ 'weeks' ] = self.__cfg.weeks

        elif hasattr( self.__cfg, 'days' ) and isinstance( self.__cfg.days, int ):
            result[ 'days' ] = self.__cfg.days

        elif hasattr( self.__cfg, 'hours' ) and isinstance( self.__cfg.hours, int ):
            result[ 'hours' ] = self.__cfg.hours

        elif hasattr( self.__cfg, 'minutes' ) and isinstance( self.__cfg.minutes, int ):
            result[ 'minutes' ] = self.__cfg.minutes

        elif hasattr( self.__cfg, 'seconds' ) and isinstance( self.__cfg.seconds, int ):
            result[ 'seconds' ] = self.__cfg.seconds

        if len( result ) == 0:
            result[ 'days' ] = 7

        return timedelta( **result )


class IFolderMap( BaseModel ):
    src:        str
    dst:        str


class ILogging( BaseModel ):
    filename:   t.Optional[ str ]
    level:      str


class ISmtpMail( BaseModel ):
    host:       str
    port:       int                 = Field( 465 )   # SSL SMTP
    password:   t.Optional[ str ]   = Field( None )
    username:   t.Optional[ str ]   = Field( None )
    sender:     str
    receiver:   str



class IConfiguration( BaseModel ):
    operation:  t.Literal[ "pull", "push" ]     = Field( 'pull' )
    hostname:   str
    username:   str
    deep_sleep: bool                            = Field( True,
                                                         validation_alias = AliasChoices( 'deep_sleep',
                                                                                          'deep-sleep' ) )
    ssh_key:    t.Optional[ str ]               = Field( '~/.ssh/ssh_id_rsa',
                                                         validation_alias = AliasChoices( 'ssh_key',
                                                                                          'ssh-key' ) )
    mapping:    t.List[ IFolderMap ]
    every:      IEvery
    bandwidth:  int                 = Field( -1 )
    logging:    t.Optional[ ILogging ]
    mail:       t.Optional[ ISmtpMail ]


class CConfiguration( object ):
    LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'

    def __init__( self, filename: str, verbose: t.Optional[ bool ] = False ):
        with open( filename, 'r' ) as stream:
            self.__cfg = IConfiguration( **yaml.load( stream, Loader = yaml.Loader ) )

        self.__every = CEvery( self.__cfg.every )
        self.__logger = logging.getLogger( 'replicator' )
        if hasattr( self.__cfg, 'logging' ):
            # Setup the logging
            if hasattr( self.__cfg.logging, 'filename' ):
                logging.basicConfig( filename = self.__cfg.logging.filename,
                                     filemode = 'a',
                                     format = self.LOGGING_FORMAT )

            else:
                if os.path.exists( '/dev/log' ):
                    handler = logging.handlers.SysLogHandler( '/dev/log' )
                    handler.setFormatter( logging.Formatter( self.LOGGING_FORMAT ) )
                    handler.setLevel( logging.DEBUG )
                    self.__logger.addHandler( handler )

            if hasattr( self.__cfg.logging, 'level' ):
                self.__logger.setLevel( logging.getLevelNamesMapping()[ self.__cfg.logging.level ] )

            if verbose:
                handler = logging.StreamHandler( stream = sys.stdout )
                handler.setFormatter( logging.Formatter( self.LOGGING_FORMAT ) )
                handler.setLevel( logging.DEBUG )
                self.__logger.addHandler( handler )
                self.__logger.setLevel( logging.DEBUG )

            else:
                # Close the stdout, stderr and stdin handles and redirect to null device
                devnull = "/dev/null"
                if hasattr( os, "devnull" ):
                    # Python has set os.devnull on this system, use it instead as it might
                    # be different from /dev/null.
                    devnull = os.devnull

                for fd in (sys.stderr.fileno(), sys.stdout.fileno(), sys.stdin.fileno()):
                    try:
                        os.close( fd )

                    except OSError:
                        pass

                # Do the redirect
                devnull_fd = os.open( devnull, os.O_RDWR )
                os.dup2( devnull_fd, 0 )
                os.dup2( devnull_fd, 1 )
                os.dup2( devnull_fd, 2 )
                os.close( devnull_fd )

        return

    @property
    def LogLevel( self ) -> str:
        if hasattr( self.__cfg, 'logging' ) and hasattr( self.__cfg.logging, 'level' ):
            return self.__cfg.logging.level

        return "NOTSET"

    @property
    def Operation( self ) -> str:
        return self.__cfg.operation

    @property
    def Hostname( self ) -> str:
        return self.__cfg.hostname

    @property
    def Username( self ) -> str:
        return self.__cfg.username

    @property
    def SshKey( self ) -> str:
        return self.__cfg.ssh_key

    @property
    def Bandwidth( self ) -> int:
        return self.__cfg.bandwidth

    @property
    def Every( self ) -> CEvery:
        return self.__every

    @property
    def Folders( self ) -> t.List[ IFolderMap ]:
        return self.__cfg.mapping

    def __iter__( self ) -> t.Iterator[ IFolderMap ]:
        return iter( self.__cfg.mapping )

    @property
    def Logger( self ) -> logging.Logger:
        return self.__logger

    @property
    def DeepSleep( self ) -> bool:
        if hasattr( self.__cfg, 'deep_sleep' ):
            return self.__cfg.deep_sleep

        return True

    @property
    def Smtp( self ) -> t.Union[ ISmtpMail, None ]:
        if hasattr( self.__cfg, 'mail' ):
            return self.__cfg.mail

        return None
