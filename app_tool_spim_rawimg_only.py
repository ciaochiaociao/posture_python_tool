
from hmx.hmx_spi_master_commands import HmxSpiMasterCommand

from hmx.hmx_meta_data_format import *
import hmx.logger as HxLogger

from time import sleep
from datetime import datetime
import numpy as np
import time
import cv2
import logging

# Set Logger
Log = logging.getLogger(HxLogger.MAIN_SCRIPT)


if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()

    # Start to use SPI Slave Command.
    intf_cmd = HmxSpiMasterCommand(get_meta=False, get_jpeg=False, get_raw=True)

    RawFrame = None

    while True:
        # Get Raw
        RawFrame = intf_cmd.GetRaw(timeout=1)

        if RawFrame:
            img_str = RawFrame
            nparr = np.frombuffer(img_str, np.uint8)
            nparr.shape = (480, 640) # For HM0360, 640x480, Mono
            img = cv2.cvtColor(nparr, cv2.COLOR_GRAY2RGB)
            # show image in windows
            cv2.imshow('frame', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    # Terminate the SPI Slave Commands.
    intf_cmd.Terminate()