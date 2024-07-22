
from hmx.hmx_spi_slave_commands import HmxSpiSlaveCommand

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
    intf_cmd = HmxSpiSlaveCommand(get_meta=False, get_jpeg=True, get_raw=False)

    MetaData = None
    JpegFrame = None

    while True:
        # Get JPEG.
        #JpegFrame = intf_cmd.GetJpeg(timeout=1)
        # Get Metadata.
        MetaData = intf_cmd.GetMetaData(timeout=1)

        if MetaData:
            detected_info = GetDetectInfo(MetaData)
            bd_infos = detected_info['bd_infos']
            bd_num_of_detection = detected_info['bd_num_of_detection']
            print('bd_num_of_detection = %d' % bd_num_of_detection)
            fd_infos = detected_info['fd_infos']
            fd_num_of_detection = detected_info['fd_num_of_detection']
            print('fd_num_of_detection = %d' % fd_num_of_detection)

        if JpegFrame:
            img_str = JpegFrame
            nparr = np.frombuffer(img_str, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if MetaData:
                # draw people count.
                cv2.putText(img, str(bd_num_of_detection), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                # draw detected box.
                for bd_info in bd_infos:
                    print(bd_info)
                    bd_x = bd_info['x']
                    bd_y = bd_info['y']
                    bd_width = bd_info['width']
                    bd_height = bd_info['height']
                    bd_position_str = '(' + str(bd_x) + ',' + str(bd_y) + ')'
                    cv2.rectangle(img, (bd_x, bd_y), (bd_x + bd_width, bd_y + bd_height), (255, 255, 0), 1)
                    cv2.putText(img, bd_position_str, (bd_x, bd_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                for fd_info in fd_infos:
                    print(fd_info)
                    cv2.rectangle(img, (fd_info['x'], fd_info['y']), (fd_info['x']+fd_info['width'], fd_info['y']+fd_info['height']), (0, 255, 255), 1)
                    yaw = fd_info['yaw']
                    pitch = fd_info['pitch']
                    if ((yaw != 0) or (pitch != 0)):
                        face_pose_str = '(' + str(yaw) + ', ' + str(pitch) +')'
                        cv2.putText(img, face_pose_str, (fd_info['x']+2, fd_info['y']+2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            else:
                print('JPG: No Metadata!')
            # show image in windows
            cv2.imshow('frame', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    # Terminate the SPI Slave Commands.
    intf_cmd.Terminate()