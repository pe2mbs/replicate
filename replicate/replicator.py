from replicate.config import CConfiguration
from replicate.run import run_process


def replicator( config: CConfiguration, source: str, target: str ) -> int:
    # -a, --archive               archive mode; equals -rlptgoD (no -H,-A,-X)
    # -r, --recursive             recurse into directories
    # -u, --update                skip files that are newer on the receiver
    # -n, --dry-run               perform a trial run with no changes made
    # -e, --rsh=COMMAND           specify the remote shell to use
    # rsync --bwlimit=5000 -varue ssh -i  ~/.ssh/replicator --progress 145.53.24.178:/mnt/storage/work /mnt/storage/work
    def sshCommand() -> str:
        result = "/usr/bin/ssh"
        if config.SshKey is not None:
            result += f" -i {config.SshKey} -l replicate"

        return f'{ result } -o StrictHostKeyChecking=no'

    # As the rsync may run for a long time we need to catch the output as it been written
    # --verbose, -v / --archive, -a / --recursive, -r / --update, -u / --compress, -z / --human-readable, -h
    args = [ 'rsync', '-varuzh', '-e', sshCommand(), '--progress' ]
    if isinstance( config.Bandwidth, int ):
        args.append( f'--bwlimit={config.Bandwidth}' )

    args.append( source )
    args.append( target )
    return run_process( args, config.Logger )
