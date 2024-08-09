from hmx.hmx_spi_slave_commands import HmxSpiSlaveCommand
import hmx.logger as HxLogger

import logging

# Set Logger
Log = logging.getLogger(HxLogger.MAIN_SCRIPT)

if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()
    intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)
