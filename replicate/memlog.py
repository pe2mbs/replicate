import logging.handlers
from logging import LogRecord


class MemoryHandler( logging.handlers.MemoryHandler ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.errorCount = 0
        return

    def flush( self ):
        pass

    def getBuffer( self ) -> str:
        result: str = ''
        for record in self.buffer:
            # When a split on CR results in more lines, just use the last line.
            result += record.getMessage().split( '\r' )[ -1 ] + "\n"

        super().flush()
        return result

    def gerErrors( self ) -> str:
        result: str = ''
        for record in self.buffer:
            if record.levelno <= logging.ERROR:
                result += record.getMessage()

        super().flush()
        return result

    def emit(self, record: LogRecord ):
        if record.levelno <= logging.ERROR:
            self.errorCount += 1

        return super().emit( record )
