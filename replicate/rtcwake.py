import time
from replicate.config import CConfiguration
from replicate.run import run_process
from datetime import datetime


def rtc_wake( config: CConfiguration ):
    # RTC wake up for the next time
    dt = datetime.now().replace( hour = config.Every.Time.hour,
                                 minute = config.Every.Time.minute,
                                 second = 0 )
    dt += config.Every.deltaTime()
    config.Logger.info( f"dt  {dt}")
    args = [ 'sudo', 'rtcwake', '-v', '--auto', '--date', dt.strftime('%Y%m%d%H%M%S'), '--mode', 'off' ]
    line = ' '.join( args )
    config.Logger.info( f"RTC-wake [{ line }]" )
    run_process( args, config.Logger )
    # admin     ALL=(root) NOPASSWD: /sbin/rtcwake
    # replicate ALL=(root) NOPASSWD: /sbin/rtcwake
    return
