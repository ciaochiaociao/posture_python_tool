
from hmx.hmx_uart_rx_commands import HmxUartRxCommand

from hmx.hmx_meta_data_format import *
import hmx.logger as HxLogger

from time import sleep
from datetime import datetime
import numpy as np
import cv2
import logging

# Set Logger
Log = logging.getLogger(HxLogger.MAIN_SCRIPT)

captured_file_path = './captured/'

if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()

    # Start to use SPI Slave Command.
    intf_cmd = HmxUartRxCommand(get_meta=False, get_jpeg=False, comport='COM10', get_raw=True, baudrate=921600)

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

            # Save Image
            now = datetime.now()
            filename = now.strftime("%Y_%m%d_%H%M%S")
            cv2.imwrite(captured_file_path + filename + '.bmp', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    # Terminate the SPI Slave Commands.
    intf_cmd.Terminate()