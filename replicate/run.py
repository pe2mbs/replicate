import typing as t
import subprocess


def run_process( args, logger, stdout: t.Optional[ list ] = None ) -> t.Union[ int, None ]:
    def _log_stream( std_stream ):
        for line in std_stream:
            line = line.decode( 'utf-8' ).strip( '\n' )
            if line != "":
                if isinstance( stdout, list ):
                    stdout.append( line )

                else:
                    logger.info( line )

        return

    cmdline = ' '.join( args )
    logger.info( f"{cmdline}" )
    process = subprocess.Popen( args, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    while process.returncode is None:
        _log_stream( process.stdout )
        _log_stream( process.stderr )
        process.poll()

    if process.returncode == 0:
        logger.info( f"Process result code: { process.returncode }" )

    else:
        logger.error( f"Process result code: {process.returncode}" )

    return process.returncode
