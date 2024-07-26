import os
import mmap
import tempfile

from hmx.hmx_spi_slave_commands import HmxSpiSlaveCommand
from hmx.hmx_meta_data_format import *
from hmx.hmx_i2c_cmd import HmxI2cCmd
import hmx.logger as HxLogger

from time import sleep
from datetime import datetime
import numpy as np
import time
import cv2
import logging

# Set Logger
Log = logging.getLogger(HxLogger.MAIN_SCRIPT)


def create_temp_shm(name, size):
    global temp_dir, temp_file_path, mm, temp_file
    # Create a temporary directory
    # temp_dir = tempfile.mkdtemp()
    # temp_file_path = os.path.join(temp_dir, name)
    temp_file_path = tempfile.gettempdir() + '/' + name

    # Open the file for reading and writing
    temp_file = open(temp_file_path, 'w+b')
    print("temp_file_path:", temp_file_path)
    # Ensure the file is of the specified size
    temp_file.truncate(size)
        
    # Create a memory-mapped file
    mm = mmap.mmap(temp_file.fileno(), size)

    
def cleanup_temp_shm():
    # Cleanup: Delete the temporary file and directory
    # Note: In a real application, ensure this happens even if an exception is raised
    mm.close()
    temp_file.close()
    os.remove(temp_file_path)
    os.rmdir(temp_dir)


if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()

    # Example usage
    create_temp_shm("hmx_shm", 1024)

    # Start to use SPI Slave Command.
    intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)

    MetaData = None
    JpegFrame = None
    RawFrame = None

    i = 0

    while True:
        # Get Metadata.
        MetaData = intf_cmd.GetMetaData(timeout=1)
        if MetaData:
            # input("MetaData: %s" % MetaData)
            detected_info = GetDetectInfo(MetaData)
            bd_infos = detected_info['bd_infos']
            bd_num_of_detection = detected_info['bd_num_of_detection']
            print('bd_infos = %s' % bd_infos)
            print('bd_num_of_detection = %d' % bd_num_of_detection)
            fd_infos = detected_info['fd_infos']
            fd_num_of_detection: int = detected_info['fd_num_of_detection']
            print('fd_infos = %s' % fd_infos)
            print('fd_num_of_detection = %d' % fd_num_of_detection)
            # input("bd_infos and fd_infos above ^^^")
            print("bd_num_of_detection.to_bytes(1, byteorder='big'):", bd_num_of_detection.to_bytes(1, byteorder='big'))
            print("bd_num_of_detection.to_bytes(2, byteorder='big'):", bd_num_of_detection.to_bytes(2, byteorder='big'))
            print("bd_num_of_detection.to_bytes(1, byteorder='little'):", bd_num_of_detection.to_bytes(1, byteorder='little'))
            mm[:1] = bd_num_of_detection.to_bytes(1, byteorder='big')

        # Get JPEG.
        JpegFrame = intf_cmd.GetJpeg(timeout=1)
        if JpegFrame:
            # input("JpegFrame: %s" % JpegFrame)
            img_str = JpegFrame
            nparr = np.frombuffer(img_str, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if MetaData:
                # draw people count.
                #cv2.putText(img, str(bd_num_of_detection), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
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
                    # Reg ID
                    reg_id = fd_info['register_id']
                    if reg_id > 0:
                        cv2.putText(img, 'ID: '+str(reg_id), (fd_info['x'] + 5, fd_info['y'] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 128, 255), 2, cv2.LINE_AA)
                        # Face Bounding Box
                        cv2.rectangle(img, (fd_info['x'], fd_info['y']), (fd_info['x']+fd_info['width'], fd_info['y']+fd_info['height']), (0, 128, 255), 1)
                    else:
                        # Face Bounding Box
                        cv2.rectangle(img, (fd_info['x'], fd_info['y']), (fd_info['x']+fd_info['width'], fd_info['y']+fd_info['height']), (0, 255, 255), 1)
                    # Draw Head Pose
                    yaw = fd_info['yaw']
                    pitch = fd_info['pitch']
                    if ((yaw != 0) or (pitch != 0)):
                        yaw_str = 'yaw=' + str(yaw)
                        pitch_str = 'pitch=' + str(pitch)
                        cv2.putText(img, yaw_str, (fd_info['x']+fd_info['width'], fd_info['y']+13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                        cv2.putText(img, pitch_str, (fd_info['x']+fd_info['width'], fd_info['y']+23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            # show image in windows
            cv2.imshow('frame', img)
            #cv2.imwrite('./captured/' + str(i).zfill(8) + '_result.jpg', img)

        # Get Raw
        #RawFrame = intf_cmd.GetRaw(timeout=1)
        if RawFrame:
            img_str = RawFrame
            nparr = np.frombuffer(img_str, np.uint8)
            nparr.shape = (480, 640) # For HM0360, 640x480, Mono
            img = cv2.cvtColor(nparr, cv2.COLOR_GRAY2RGB)
            # The Info from Metadata.
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
                        yaw_str = 'yaw=' + str(yaw)
                        pitch_str = 'pitch=' + str(pitch)
                        cv2.putText(img, yaw_str, (fd_info['x']+fd_info['width'], fd_info['y']+10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                        cv2.putText(img, pitch_str, (fd_info['x']+fd_info['width'], fd_info['y']+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            # show image in windows
            cv2.imshow('frame', img)
            #cv2.imwrite(filename_bmp, nparr)
            #cv2.imwrite(filename_result_jpg, img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('1'):
            intf_cmd.Terminate()
            sleep(1)
            i2c_cmd = HmxI2cCmd()
            i2c_cmd.FrReg()
            sleep(0.5)
            intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)
            sleep(2)
        elif key == ord('2'):
            intf_cmd.Terminate()
            sleep(1)
            i2c_cmd = HmxI2cCmd()
            i2c_cmd.FrUnReg()
            sleep(0.5)
            intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)
            sleep(2)
        elif key == ord('3'):
            intf_cmd.Terminate()
            sleep(1)
            i2c_cmd = HmxI2cCmd()
            i2c_cmd.FrClear()
            sleep(0.5)
            intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)
            sleep(2)
        elif key == ord('q'):
            break

        i += 1
    cv2.destroyAllWindows()

    # Terminate the SPI Slave Commands.
    intf_cmd.Terminate()